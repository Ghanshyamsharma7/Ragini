// src/components/MessageInput.jsx
import { useState, useRef, useEffect } from "react";

function MessageInput({ onSend, disabled, isLoading }) {
  const [text, setText] = useState("");
  const textareaRef = useRef(null);

  // Auto-expand textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
  }, [text]);

  const sendMessage = () => {
    if (!text.trim() || disabled || isLoading) return;
    onSend(text.trim());
    setText("");
    // Reset height
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const canSend = text.trim() && !disabled && !isLoading;

  return (
    <div className="message-input-wrap">
      <div className={`message-input-box ${disabled ? "message-input-box--disabled" : ""}`}>
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKey}
          rows={1}
          placeholder={
            disabled
              ? "Select class & subject first…"
              : "Ask Ragini anything…"
          }
          disabled={disabled || isLoading}
          className="message-textarea"
        />

        <button
          onClick={sendMessage}
          disabled={!canSend}
          className={`send-btn ${canSend ? "send-btn--active" : ""}`}
          title="Send"
        >
          {isLoading ? (
            <span className="send-spinner" />
          ) : (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 13V3M3 8l5-5 5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </button>
      </div>
      <p className="input-hint">Enter to send · Shift+Enter for new line</p>
    </div>
  );
}

export default MessageInput;
