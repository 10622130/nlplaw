# 法律智能小幫手

台灣法律問答與歷屆考題練習服務，支援 LINE Bot 與 Web 兩種介面。

---

### 專案動機：

台灣法律知識對一般民眾而言門檻高、資料分散。本專案目標是透過 GPT-4o 提供即時法律問答，並整合歷屆律師考試題目，讓有備考需求的使用者能在 LINE 或網頁上練習。

原始版本（`LINE/lawbot/`）以單一 Python 檔案實作所有邏輯，全域變數儲存答題狀態、無輸入驗證、無冪等保護，在多人同時使用時必定出錯。本次重構將兩個分散的資料夾整合成具備分層架構、容器化部署、並通過本地測試的完整服務。

---

### 重點設計：

- **為什麼用 Blueprint 而非直接在 app 上註冊 route**

  直接在 `app` 上定義 route，每個 route 檔案在 import 時就需要拿到 `app` 物件，造成 module-level 循環依賴。為了提高系統維護性，使用Blueprint 讓 route 定義與 app 物件解耦，在 `register_blueprint()` 時才綁定，各 blueprint 可以獨立掛到測試用的 minimal app。


- **為什麼 LINE Webhook 的冪等記錄要在處理完之後才寫入，而非一開始就寫**

  LINE 在網路不穩或 server 回應太慢時，會把同一則訊息重送。如果一開始就寫下「這則訊息已處理」，但後續 AI 呼叫或資料庫寫入失敗，下次 LINE 重送時會因為記錄已存在而直接跳過，用戶的訊息永遠不會得到回覆。選擇在全部處理完之後才寫入記錄，萬一中途失敗，LINE 重送時可以從頭再處理一次。取捨是：極少數情況下同一則訊息可能被處理兩次，但對法律問答場景而言，收到兩次回答比完全沒有回答好。

- **為什麼把業務邏輯從 Blueprint 抽出到 Service Layer**
  把所有邏輯放在同一個 route function 裡，表面上簡單，但任何修改都需要動路由檔案，而且函式依賴 Flask 的 `request` 物件，在沒有 HTTP 請求的情況下（例如寫測試）就無法直接呼叫。把業務邏輯搬到 `services/linebot_service.py` 之後，路由只負責接收請求、驗證簽名、把資料傳給 service，service 函式本身不依賴 Flask，可以在測試中直接呼叫，不需要模擬 HTTP 環境。


---

### 任務清單：

**已完成：**
- 所有 events 正確處理，非 message event 不再誤回 400 導致 LINE 無限重試
- Idempotency（冪等性）保護，防止 LINE Webhook 重送造成重複處理
- Service Layer 抽離，業務邏輯與 HTTP 邊界分離
- 輸入驗證：空白、純符號、超過 200 字、非中文比例過高
- 意圖辨識：考題模式（科目 → 年份 → 出題 → 答題）與法律問答分流
- 考題答題狀態以 DB（ExamSession）儲存，multi-worker 安全
- 容器化部署（Docker + docker-compose），含 PostgreSQL 與 mock 考題 API
- Web LINE Login OAuth 2.0：匿名與登入並行，登入後問答寫入 DB
- Rich Menu 腳本整合至 `core/richmenu.py`

**待解決：**
- LINE Bot 考題流程 end-to-end 測試（含 mock 考題 API）
- Rich Menu 部署執行（`flask setup-richmenu`）
- Health check endpoint
- 單元測試（Service Layer 函式優先）
- 移除 `LINE/` 舊資料夾（待考題與 Rich Menu 確認完成後）
