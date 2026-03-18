
// src/components/Sidebar.jsx
import { useContext } from "react";
import { PlusIcon, TrashIcon } from "@heroicons/react/24/solid";
import ProfileMenu from "./ProfileMenu";

function Sidebar({ sessions, onNew, onSelect, onDelete, isOpen }) {
  return (
    <aside
      className={`sidebar ${isOpen ? "sidebar--open" : ""}`}
      onClick={(e) => e.stopPropagation()}
    >
      {/* Brand + New Chat */}
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <span className="brand-dot" />
          Ragini
        </div>
        <button className="new-chat-btn" onClick={onNew} title="New Chat">
          <PlusIcon className="icon-sm" />
        </button>
      </div>

      {/* Section label */}
      <p className="sidebar-section-label">Recent</p>

      {/* Session list */}
      <nav className="sidebar-nav">
        {sessions.length === 0 && (
          <p className="sidebar-empty">No chats yet</p>
        )}
        {sessions.map((s) => (
          <div
            key={s.id}
            onClick={() => onSelect(s)}
            className="session-item"
          >
            <span className="session-title">{s.title || "Untitled"}</span>
            <button
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(s.id);
              }}
              title="Delete"
            >
              <TrashIcon className="icon-xs" />
            </button>
          </div>
        ))}
      </nav>

      {/* Profile at bottom */}
      <div className="sidebar-footer">
        <ProfileMenu />
      </div>
    </aside>
  );
}

export default Sidebar;
