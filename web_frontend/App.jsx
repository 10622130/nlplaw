import React, { useState, useRef } from "react";

export default function App() {
  const [userMessage, setUserMessage] = useState("");
  const [messages, setMessages] = useState([
    { role: "ai", text: "您好，請輸入您的法律問題！" }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastSendTime, setLastSendTime] = useState(0);
  const timerRef = useRef(null);

  // 節流：每 10 秒只能送一次
  const canSend = () => {
    const now = Date.now();
    return now - lastSendTime > 10000;
  };

  const handleSend = async (e) => {
    e.preventDefault();
    setError("");
    if (!userMessage.trim()) {
      setError("請輸入訊息");
      return;
    }
    if (!canSend()) {
      setError("請稍候 10 秒再送出");
      return;
    }
    setLoading(true);
    setLastSendTime(Date.now());

    // 新增使用者訊息
    setMessages((prev) => [
      ...prev,
      { role: "user", text: userMessage }
    ]);

    // 串接後端 API
    try {
      const resp = await fetch("/api/user_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userMessage })
      });
      if (!resp.ok) {
        const errData = await resp.json();
        throw new Error(errData.error || "API 錯誤");
      }
      const data = await resp.json();
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: data.response }
      ]);
      setUserMessage("");
    } catch (err) {
      setError("送出失敗，請稍後再試");
    } finally {
      setLoading(false);
      // 自動清除錯誤訊息
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => setError(""), 3000);
    }
  };

      <button className="login-btn"><span style={{color: "#fff"}}>登入</span></button>
  return (
    <div className="form-container">
      <div className="form-title">法律智能小幫手</div>
      <div className="chat-area">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-row ${msg.role}`}
          >
            <div className={`chat-message ${msg.role === "user" ? "chat-user" : "chat-ai"}`}>
              {msg.text}
            </div>
          </div>
        ))}
      </div>
      {error && (
        <div style={{ color: "#e00", margin: "8px 0", textAlign: "center" }}>
          {error}
        </div>
      )}
      <form className="input-bar" onSubmit={handleSend}>
        <input
          className="user-message-input"
          type="text"
          placeholder="請輸入訊息"
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          disabled={loading}
          maxLength={200}
        />
        <button
          className="send-btn"
          type="submit"
          disabled={loading || !userMessage.trim() || !canSend()}
          aria-label="送出"
        >
          {loading ? (
            <span style={{fontSize: "1rem"}}>送出中...</span>
          ) : (
            <span style={{fontSize: "1.5rem", display: "flex", alignItems: "center", justifyContent: "center"}}>&uarr;</span>
          )}
        </button>
      </form>
    </div>
  );
}