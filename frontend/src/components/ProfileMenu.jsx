// src/components/ProfileMenu.jsx
import { useContext, useState, useEffect, useRef } from "react";
import { AuthContext } from "../context/AuthContext";

function ProfileMenu() {
  const { user } = useContext(AuthContext);
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef(null);

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setShowMenu(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const logout = () => {
    window.location.href = "http://localhost:8000/auth/logout";
  };

  if (!user) return null;

  return (
    <div className="profile-menu" ref={menuRef}>
      <button
        className="profile-trigger"
        onClick={() => setShowMenu((v) => !v)}
      >
        <img
          src={user.picture}
          alt={user.name}
          className="profile-avatar"
          referrerPolicy="no-referrer"
        />
        <div className="profile-info">
          <span className="profile-name">{user.name}</span>
          <span className="profile-email">{user.email}</span>
        </div>
      </button>

      {showMenu && (
        <div className="profile-dropdown">
          <button onClick={logout} className="profile-logout">
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}

export default ProfileMenu;
