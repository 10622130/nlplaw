import React, { useState, useRef, useEffect } from "react";

export default function App() {
  const [userMessage, setUserMessage] = useState("");
  const [messages, setMessages] = useState([
    { role: "ai", text: "您好，請輸入您的法律問題！" }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastSendTime, setLastSendTime] = useState(0);
  const [user, setUser] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    fetch("/auth/me")
      .then(r => r.json())
      .then(data => setUser(data.logged_in ? data : null));
  }, []);

  const canSend = () => Date.now() - lastSendTime > 10000;

  const handleSend = async (e) => {
    e.preventDefault();
    setError("");
    if (!userMessage.trim()) { setError("請輸入訊息"); return; }
    if (!canSend()) { setError("請稍候 10 秒再送出"); return; }

    setLoading(true);
    setLastSendTime(Date.now());
    setMessages(prev => [...prev, { role: "user", text: userMessage }]);

    try {
      const resp = await fetch("/api/user_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userMessage })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "API 錯誤");
      setMessages(prev => [...prev, { role: "ai", text: data.response }]);
      setUserMessage("");
    } catch (err) {
      setError(err.message || "送出失敗，請稍後再試");
    } finally {
      setLoading(false);
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => setError(""), 3000);
    }
  };

  const handleLogout = async () => {
    await fetch("/auth/logout", { method: "POST" });
    setUser(null);
  };

  return (
    <div className="form-container">
      <div className="form-title">
        法律智能小幫手
        <div style={{ marginTop: "8px" }}>
          {user ? (
            <span style={{ fontSize: "0.85rem" }}>
              {user.display_name}&nbsp;
              <button className="login-btn" onClick={handleLogout}>登出</button>
            </span>
          ) : (
            <a href="/auth/line">
              <button className="login-btn"><span style={{ color: "#fff" }}>LINE 登入</span></button>
            </a>
          )}
        </div>
      </div>
      <div className="chat-area">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-row ${msg.role}`}>
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
          {loading
            ? <span style={{ fontSize: "1rem" }}>送出中...</span>
            : <span style={{ fontSize: "1.5rem", display: "flex", alignItems: "center", justifyContent: "center" }}>&uarr;</span>
          }
        </button>
      </form>
    </div>
  );
}
