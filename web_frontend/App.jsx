import React, { useState, useEffect } from "react";

// In local dev this is empty — relative paths go through Vite's proxy
// (vite.config.js) to the same-origin API. In production the frontend
// (Cloudflare Pages) and API (Render) are on different domains, so this
// must be set to the full Render URL via the VITE_API_BASE_URL build-time
// env var, and every request needs credentials: "include" so the
// cross-site session cookie (LINE Login) is sent/accepted.
const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export default function App() {
  const [userMessage, setUserMessage] = useState("");
  const [messages, setMessages] = useState([
    { role: "ai", text: "您好，請輸入您的法律問題！" }
  ]);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/auth/me`, { credentials: "include" })
      .then(r => r.json())
      .then(data => setUser(data.logged_in ? data : null));
  }, []);

  // No fixed-time cooldown: the send button is disabled purely by `loading`.
  // The backend commits any DB write synchronously inside the same
  // request/response cycle (see web_bp.py's user_message()), so by the time
  // `await fetch(...)` resolves and `loading` goes back to false, a valid
  // question's data (if any) has already been persisted — there's no way to
  // race ahead of the database. Invalid input (empty, or rejected by the
  // backend's spamfilter) never reaches the DB write at all and returns
  // fast, so the button naturally unlocks again just as quickly.
  const handleSend = async (e) => {
    e.preventDefault();
    const trimmedMessage = userMessage.trim();
    if (!trimmedMessage) {
      setMessages(prev => [...prev, { role: "error", text: "請輸入訊息" }]);
      return;
    }

    setLoading(true);
    setMessages(prev => [...prev, { role: "user", text: trimmedMessage }]);

    try {
      const resp = await fetch(`${API_BASE}/api/user_message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ user_input: trimmedMessage })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "API 錯誤");
      setMessages(prev => [...prev, { role: "ai", text: data.response }]);
      setUserMessage("");
    } catch (err) {
      setMessages(prev => [...prev, { role: "error", text: err.message || "送出失敗，請稍後再試" }]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await fetch(`${API_BASE}/auth/logout`, { method: "POST", credentials: "include" });
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
            <a href={`${API_BASE}/auth/line`}>
              <button className="login-btn"><span style={{ color: "#fff" }}>LINE 登入</span></button>
            </a>
          )}
        </div>
      </div>
      <div className="chat-area">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-row ${msg.role}`}>
            <div
              className={`chat-message ${
                msg.role === "user" ? "chat-user" : msg.role === "error" ? "chat-error" : "chat-ai"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>
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
          disabled={loading || !userMessage.trim()}
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
