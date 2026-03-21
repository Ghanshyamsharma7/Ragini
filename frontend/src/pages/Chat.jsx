// src/pages/Chat.jsx
import { useContext, useEffect, useState } from "react";
import API from "../api/api";
import { AuthContext } from "../context/AuthContext";

import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import MessageInput from "../components/MessageInput";
import SessionSelector from "../components/SessionSelector";

function Chat() {
  const { user } = useContext(AuthContext);

  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const [className, setClassName] = useState("");
  const [subject, setSubject] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const canStart = className && subject;
  const hasMessages = messages.length > 0;

  useEffect(() => {
    if (user) loadSessions();
  }, [user]);

  async function loadSessions() {
    try {
      const res = await API.get("/session/list");
      setSessions(res.data);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    }
  }

  async function selectSession(s) {
    try {
      setCurrentSession(s);
      setClassName(s.class_name || "");
      setSubject(s.subject || "");

      const res = await API.get(`/session/${s.id}/history`);
      const msgArr = [];
      res.data.forEach((r) => {
        // rows come back as arrays: [question, answer, created_at]
        // or as objects depending on SQLAlchemy — handle both
        const question = r.question ?? r[0];
        const answer   = r.answer   ?? r[1];
        if (question) msgArr.push({ role: "user",      text: question });
        if (answer)   msgArr.push({ role: "assistant", text: answer });
      });
      setMessages(msgArr);
      setSidebarOpen(false);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  }

  async function createSession() {
    try {
      const res = await API.post("/session/create", {
        class_name: className,
        subject,
      });
      const s = res.data;
      setCurrentSession(s);
      setSidebarOpen(false);
      return s;
    } catch (err) {
      console.error("Session creation failed:", err);
      throw err;
    }
  }

  async function deleteSession(id) {
    try {
      await API.delete(`/session/${id}`);
      if (currentSession?.id === id) {
        setCurrentSession(null);
        setMessages([]);
        setClassName("");
        setSubject("");
      }
      // Reload sessions list after delete
      await loadSessions();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  }

  async function handleSend(text) {
    try {
      if (!canStart && !currentSession) return;
      setIsLoading(true);
      setMessages((m) => [...m, { role: "user", text }]);

      let sessionId = currentSession?.id;
      let payloadClass = className;
      let payloadSubject = subject;

      if (!sessionId) {
        const s = await createSession();
        sessionId = s.id;
        payloadClass = s.class_name || payloadClass;
        payloadSubject = s.subject || payloadSubject;
      }

      const res = await API.post("/query/ask", {
        class_name: payloadClass,
        subject: payloadSubject,
        question: text,
        session_id: sessionId,
      });

      setMessages((m) => [...m, { role: "assistant", text: res.data.answer }]);

      // Reload sessions AFTER answer so title is updated in sidebar
      await loadSessions();

    } catch (err) {
      console.error("Message send failed:", err);
      setMessages((m) => [...m, { role: "assistant", text: "Something went wrong. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  }

  const firstName = user?.name?.split(" ")[0] || "there";

  return (
    <div className="chat-root">
      {sidebarOpen && (
        <div className="mobile-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      <Sidebar
        sessions={sessions}
        onNew={() => {
          setCurrentSession(null);
          setMessages([]);
          setClassName("");
          setSubject("");
          setSidebarOpen(false);
        }}
        onSelect={selectSession}
        onDelete={deleteSession}
        isOpen={sidebarOpen}
      />

      <main className="chat-main" onClick={() => sidebarOpen && setSidebarOpen(false)}>
        {/* Mobile topbar */}
        <div className="mobile-topbar">
          <button
            className="hamburger-btn"
            onClick={(e) => { e.stopPropagation(); setSidebarOpen(true); }}
          >
            <span /><span /><span />
          </button>
          <span className="mobile-title">{currentSession?.title || "Ragini"}</span>
        </div>

        <div className="chat-column">

          {/* Welcome screen — only when no messages */}
          {!hasMessages && (
            <div className="welcome-area">
              <div className="welcome-avatar">T</div>
              <h1 className="welcome-heading">Hi, {firstName} 👋</h1>
              <p className="welcome-sub">
                I'm Tatvagyan, your personal study assistant.<br />
                Select your class and subject to get started.
              </p>
              <div className="selector-card">
                <SessionSelector
                  className={className}
                  subject={subject}
                  onClassChange={setClassName}
                  onSubjectChange={setSubject}
                  locked={false}
                />
              </div>
              {!canStart && (
                <p className="selector-hint">
                  Pick a class and subject above, then ask me anything ↓
                </p>
              )}
            </div>
          )}

          {/* Messages */}
          {hasMessages && (
            <ChatWindow messages={messages} isLoading={isLoading} />
          )}

          {/* Input — always at bottom */}
          <div className="input-area">
            <MessageInput
              onSend={handleSend}
              disabled={!canStart && !currentSession}
              isLoading={isLoading}
            />
          </div>

        </div>
      </main>
    </div>
  );
}

export default Chat;