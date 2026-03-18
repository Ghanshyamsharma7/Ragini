// src/components/ChatWindow.jsx
import { useEffect, useRef } from "react";

function TypingDots() {
  return (
    <div className="typing-indicator">
      <span /><span /><span />
    </div>
  );
}

function ChatWindow({ messages, isLoading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="chat-window">
      <div className="messages-inner">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`message-row ${m.role === "user" ? "message-row--user" : "message-row--assistant"}`}
          >
            <div className={`bubble ${m.role === "user" ? "bubble--user" : "bubble--assistant"}`}>
              {m.text}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message-row message-row--assistant">
            <div className="bubble bubble--assistant">
              <TypingDots />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}

export default ChatWindow;