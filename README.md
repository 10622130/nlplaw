# 法律智能小幫手

台灣法律問答與歷屆考題練習服務，支援 LINE Bot 與 Web 兩種介面。

---

### 專案動機：

台灣法律知識對一般民眾而言門檻高、資料分散。本專案目標是透過 GPT-4o 提供即時法律問答，並整合歷屆律師考試題目，讓有備考需求的使用者能在 LINE 或網頁上練習。

原始版本以單一 Python 檔案實作所有邏輯，全域變數儲存答題狀態、無輸入驗證、無冪等保護，缺少 request 管理邏輯。本次重構整合成具備分層架構、容器化部署、並通過本地測試的完整服務。

---

### 專案架構：

```
NLP/
├── core/                    ← 可跨框架、平台複用的function
│   ├── ai.py                   GPT-4o 呼叫，注入法律顧問系統提示
│   ├── spamfilter.py           輸入驗證：空白、長度、中文比例
│   ├── security.py             LINE Webhook HMAC-SHA256 
│   ├── line_api.py             LINE Messaging API / OAuth 封裝
│   ├── richmenu.py             Rich Menu 建立腳本（CLI 工具）
│   └── exam_api.py             呼叫外部考題 API
│
├── api/flask_app/           ← HTTP 應用層
│   ├── app.py                  註冊 blueprints
│   ├── config.py               環境變數驗證
│   ├── routes/                 後端服務互動的HTTP 端點
│   │   ├── linebot_bp.py          LINE Webhook
│   │   ├── web_bp.py              Web 
│   │   ├── ai_bp.py               /api/ai
│   │   └── auth_bp.py             LINE Login OAuth 2.0
│   ├── services/               業務邏輯層
│   │   ├── linebot_service.py     LINE Bot 訊息處理 pipeline
│   │   └── exam_service.py        考題流程邏輯
│   └── models/                 SQLAlchemy ORM（PostgreSQL）
│       ├── user.py
│       ├── user_input.py
│       ├── processed_event.py     冪等保護（Primary Key: webhookEventId）
│       └── exam_session.py        考題答題寫入狀態
│
├── web_frontend/            ← React + Vite 前端
├── DB/                      ← 資料庫研究腳本（Pinecone、歷史資料匯入）
├── ETL/                     ← 離線資料管線腳本
├── mock_exam_api.py         ← 本地測試用 mock 考題 API（docker-compose 引用）
└── docker-compose.yml       ← api + db + mock-exam 三服務
```

---

### 重點設計：

- **為什麼用 Blueprint 而非直接在 app 上註冊 route**

  1. 提高系統維護性，使用 Blueprint 讓 route 定義與 app 物件解耦，在 `register_blueprint()` 時才綁定，各 blueprint 可以獨立掛到測試用的 minimal app。
  2. 增加程式可讀性以及可測試性，除了方便閱讀外，pytest 在測試同名 .py 檔案時需要放在不同 folder 並提供 `__init__.py` 方便辨別。


- **為什麼 LINE Webhook 的冪等記錄要在處理完之後才寫入，而非一開始就寫**

  LINE 在網路不穩或 server 回應太慢時，會把同一則訊息重送。如果一開始就寫下「這則訊息已處理」，但後續 AI 呼叫或資料庫寫入失敗，下次 LINE 重送時會因為記錄已存在而直接跳過，用戶的訊息永遠不會得到回覆。選擇在全部處理完之後才寫入記錄，萬一中途失敗，LINE 重送時可以從頭再處理一次。取捨是：極少數情況下同一則訊息可能被處理兩次，但對法律問答場景而言，收到兩次回答比完全沒有回答好。

---

### 任務清單：

**已完成：**
- 所有 events 正確處理，非 message event 不再誤回 400 導致 LINE 無限重試
- Idempotency（冪等性）保護，防止 LINE Webhook 重送造成重複處理
- Service Layer 抽離，業務邏輯與 HTTP 邊界分離
- 輸入驗證：空白、純符號、超過 200 字、非中文比例過高
- 意圖辨識：考題模式（科目 → 年份 → 出題 → 答題）與法律問答分流
- 考題答題狀態以 DB（ExamSession）儲存，提供多人使用狀態管理功能
- 容器化部署（Docker + docker-compose），含 PostgreSQL 與 mock 考題 API
- Web LINE Login OAuth 2.0：匿名與登入並行，登入後問答寫入 DB
- Rich Menu 腳本整合至 `core/richmenu.py`
- Rich Menu 部署執行（`flask setup-richmenu`）
- 移除 `LINE/` 舊資料夾

**待解決：**
- LINE Bot 考題流程 end-to-end 測試（含 mock 考題 API）
- Health check endpoint
- 單元測試
