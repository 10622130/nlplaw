# Refactor Notes

## 目標

將 `LINE/lawbot/` 與 `api/flask_app/` 整合為單一可維護的服務，修正原有架構缺陷，並為後續功能擴充建立清晰的分層基礎。

---

## 目錄結構變更

```
api/flask_app/
├── routes/                  ← 原 blueprints/，改名以符合職責語意
│   ├── linebot_bp.py        ← HTTP 邊界層，只負責驗簽與 event dispatch
│   ├── ai_bp.py
│   └── web_bp.py
├── services/                ← 新增，業務邏輯層
│   └── linebot_service.py
├── models/
│   ├── database.py
│   ├── user.py
│   ├── user_input.py
│   └── processed_event.py  ← 新增，Idempotency 保護
└── ...

core/                        ← 跨服務共用模組，不含 Flask 依賴
├── ai.py
├── line_api.py
├── security.py
├── spamfilter.py
└── ...
```

---

## 模組設計說明

### `routes/linebot_bp.py` — HTTP 邊界層

**職責：** 接收 LINE Webhook，驗證簽名，將 event 分派（dispatch）給對應 handler。不包含任何業務邏輯。

**為何用 Blueprint：**
URL 階層只是命名慣例，無法解決以下兩個問題：

1. **Application Factory Pattern** — 不用 Blueprint，route 要能被 register 就必須在定義時拿到 `app` 物件，代表要在 module level import `app`，建立循環依賴。沒有 factory，就無法在測試時建立隔離的 app instance。Blueprint 讓 route 定義與 app 實例化解耦，factory 在 `register_blueprint()` 時才把兩者綁定。

2. **測試隔離** — Blueprint 可以單獨掛到測試用的 minimal app 上，只測該 blueprint 的邏輯，不需載入其他 blueprint 及其依賴。URL 階層的方式下，所有 route 都在同一個 `app`，測試時全部一起載入。

這個架構用 Blueprint 的真正原因是 factory pattern，不是 URL 管理。

**主要改動：**
- 修正原本只處理 `events[0]` 的問題，改為迴圈處理所有 events
- 修正 `follow`、`postback` 等非 message event 被 `abort(400)` 誤殺的 bug（原本導致 LINE 無限重試）
- 加入 Idempotency 檢查（見下方）

**Event dispatch 流程：**
```
callback()
  └─ _handle_event()              ← Idempotency 檢查 + type dispatch
       ├─ "message"  → _handle_message_event() → linebot_service
       ├─ "follow"   → handle_follow_event()   → linebot_service
       └─ 其他       → log & ignore (return 200，不 abort)
```

**`_handle_event()` 可能的 exception 來源：**

| 位置 | 可能失敗原因 |
|------|-------------|
| `ProcessedEvent.exists()` | DB 連線中斷、query timeout |
| `get_openai_response()` | OpenAI API timeout、rate limit、network error |
| `db.session.commit()` | DB 連線中斷、constraint violation |
| `send_line_reply()` | LINE API timeout、reply token 過期、network error |
| `ProcessedEvent.record()` | DB 連線中斷 |

任何 exception 導致 `ProcessedEvent.record()` 未執行時，該 event 不會被標記為已處理，LINE 重送時可重新完整處理。

---

### `models/processed_event.py` — Idempotency（冪等性）保護

**背景：LINE Webhook Retry 機制** — 當 LINE 在 timeout 內沒收到 HTTP 200，會將**完全相同的 payload**（含同一個 `webhookEventId`）重送。觸發情境包含：GPT-4o 回應超時、server 回傳 5xx、網路中斷。

**Idempotency（冪等性）定義：** 對同一操作執行多次，結果與執行一次相同。

**Idempotency Check（冪等性檢查）實作：**
- `webhook_event_id` 為 primary key（LINE 保證全域唯一）
- `exists()` 使用 `db.session.get()` 走 PK lookup，O(1) 查詢
- `record()` 在 event **處理完成後**才寫入

**為何在處理完後才寫入（At-Least-Once Delivery）：**
若先寫入再處理，處理中途失敗後 `ProcessedEvent` 已存在，下次重送直接跳過，造成 event 永遠不被正確處理（資料遺失）。選擇事後寫入，代價是「業務邏輯成功但 `record()` 本身失敗」時會重複處理，這是 **At-Least-Once** 的取捨，對法律問答場景可接受。

**與 Idempotent Operation 的區別：**
`_ensure_user()` 是 **Idempotent Operation（冪等操作）**：本身執行多次結果相同（INSERT IF NOT EXISTS），不需要事先檢查。`ProcessedEvent.exists()` 是 **Idempotency Check（冪等性檢查）**：在整個 pipeline 入口阻止重複執行。兩者是不同層次的概念，互相獨立。

---

### `services/linebot_service.py` — 業務邏輯層（Service Layer）

**職責：** 執行完整的訊息處理 pipeline，與 Flask request context 解耦，可獨立單元測試。

**函式：**

| 函式 | 說明 |
|------|------|
| `handle_text_message()` | 確保 user 存在 → 驗證輸入 → 呼叫 AI → 寫 DB → 回覆 |
| `handle_follow_event()` | 確保 user 存在 → 發送歡迎訊息 |
| `_ensure_user()` | Idempotent Operation：user 不存在才建立，多次呼叫結果相同 |
| `_get_ai_response()` | 呼叫 OpenAI，成功則寫入 `UserInput`，失敗則 rollback 並回傳錯誤訊息 |
| `_send_reply()` | 呼叫 LINE reply API，記錄成功/失敗 log |

**設計原則：** 每個 private function 只做一件事，錯誤在各自層級處理，不向上傳遞未預期的 exception。

---

### `core/security.py` — 簽名驗證（HMAC-SHA256）

**職責：** 驗證 LINE Webhook 的 `X-Line-Signature` header，確保請求來源合法。

**實作：** 以 Channel Secret 對 request body 做 HMAC-SHA256，再與 header 比對。

**為何用 `hmac.compare_digest()` 而非 `==`：**
普通字串比較（`==`）是 short-circuit comparison，找到第一個不同字元就立刻回傳，比較時間與相同前綴長度正相關。攻擊者可透過大量嘗試測量回應時間，逐字元推敲出正確 signature，即 **Timing Attack（時序攻擊）**。`hmac.compare_digest()` 是 **Constant-Time Comparison**，無論在哪個位置不同，都固定跑完全部字元，執行時間不洩漏任何資訊。

---

### `core/spamfilter.py` — 輸入驗證（Input Validation）

**職責：** 在進入 AI pipeline 前過濾無效輸入，保護 API 成本與用戶體驗。

**回傳格式：** `tuple[bool, str]`，`(True, normalized_text)` 或 `(False, error_message)`

**驗證順序：**
1. 空白 / 空字串 → 回覆「請輸入文字訊息」
2. 全形字元正規化（全形空白、全形英數 → 半形）
3. 長度超過 200 字 → 回覆「請將問題縮短至 200 字以內」
4. 非中文字比例超過 20% → 回覆「請用中文輸入台灣法律相關問題」

---

### `core/ai.py` — AI 呼叫封裝

**職責：** 封裝 OpenAI GPT-4o 呼叫，注入系統提示詞限制回答範圍。

**現狀：** 每次呼叫為獨立對話，無 conversation history（MVP 決策，待後續實作）。

---

### `core/line_api.py` — LINE Messaging API 封裝

| 函式 | 說明 |
|------|------|
| `send_line_reply()` | 使用 reply token 回覆，token 30 秒內有效 |
| `send_line_push()` | 主動推播，不受 reply token 限制（保留供 GPT 逾時降級使用，目前未啟用） |

---

### `Dockerfile`

**改動：**
- `python:3.10` → `python:3.10-slim`（image 縮小約 400MB）
- build context 改為專案根目錄，同時複製 `api/` 和 `core/`
- 啟動指令從 `app:app` 改為 `api.flask_app.app:app`

### `docker-compose.yml`

**服務：**
- `api`：Flask + Gunicorn，port 5002，等待 `db` healthy 後啟動
- `db`：PostgreSQL 16 Alpine，port 5432，named volume 持久化

`SQLALCHEMY_DATABASE_URI` 定義在 compose（指向內部 `db` service），其餘 secrets 從 `.env` 讀取，`.env` 已由 `.gitignore` 保護。

---

## 尚未實作（下一階段）

- LINE bot 考題流程 end-to-end 測試
- Rich Menu 切換部署（`flask setup-richmenu`）
- Health check endpoint
- 單元測試（Service Layer 函式優先）
- Step 8：移除 `LINE/` 舊資料夾（待考題 + Rich Menu 確認後）

---

## 目前專案狀態

### Local 開發環境（docker-compose.yml）

| Service | Image | Port | 說明 |
|---------|-------|------|------|
| `api` | 本地 build | 5002 | Flask + Gunicorn |
| `db` | postgres:16-alpine | 5432 | PostgreSQL，named volume 持久化 |
| `mock-exam` | python:3.10-slim | 8080 | 本地 mock 考題 API |

**環境變數：**
- `SQLALCHEMY_DATABASE_URI`、`EXAM_API_URL`、`LINE_LOGIN_REDIRECT_URI` 定義在 compose
- LINE / OpenAI / LINE Login secrets 從 `.env` 讀取

### Web LINE Login（OAuth 2.0）

**新增模組：** `api/flask_app/routes/auth_bp.py`

| Endpoint | 說明 |
|----------|------|
| `GET /auth/line` | 產生 CSRF state，redirect 到 LINE 授權頁 |
| `GET /auth/line/callback` | 驗 state，換 token，取 profile，寫 session |
| `GET /auth/me` | 回傳目前登入狀態與 user_id |
| `POST /auth/logout` | 清除 session |

**匿名 / 登入並行：** `web_bp.py` 的 `/api/user_message` 在 `session.get('user_id')` 有值時才寫 `UserInput` DB，匿名請求維持 stateless 不受影響。

**userId 一致性：** LINE Login Channel 和 Messaging API Channel 在同一個 Provider 下，同一個用戶的 `userId` 相同，web 和 LINE bot 的問答記錄共用同一個 `user_id`。

### `mock_exam_api.py`

標準庫 `http.server` 實作，不需額外安裝套件。收到任何 POST 都回傳固定民法測試題目，供 exam pipeline 本地端對端測試。`EXAM_API_URL` 以環境變數注入，local 與 production 共用同一份 code，只換 URL。

### 已驗證功能

| 功能 | 驗證方式 | 結果 |
|------|---------|------|
| Webhook 簽名驗證 | curl with dummy signature | ✅ 400 拒絕 |
| Follow event 歡迎訊息 | curl with valid signature | ✅ 200，user 寫入 DB |
| Idempotency（重送保護） | 重送相同 webhookEventId | ✅ 200，DB 只有 1 筆記錄 |
| 空白訊息攔截 | curl text = `"   "` | ✅ 200，validation 攔截 |
| 純符號訊息攔截 | curl text = `"!!!???"` | ✅ 200，validation 攔截 |
| 非 message event 處理 | curl postback event | ✅ 200，靜默 ignore |
