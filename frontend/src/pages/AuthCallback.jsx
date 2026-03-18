import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
      localStorage.setItem("token", token);
      navigate("/chat");
    } else {
      navigate("/login");
    }
  }, []);

  return <div className="p-10 text-center">Logging you in...</div>;
}

export default AuthCallback;