// src/pages/Login.jsx
function Login() {
  const login = () => {
    window.location.href = "http://localhost:8000/auth/login";
  };

  return (
    <div className="login-root">
      <div className="login-card">
        <div className="login-logo">
          <span>T</span>
        </div>
        <h1 className="login-title">Tatvagyan</h1>
        <p className="login-sub">Your personal AI study assistant</p>

        <button onClick={login} className="login-google-btn">
          <img
            src="https://www.svgrepo.com/show/475656/google-color.svg"
            width="18"
            alt="Google"
          />
          Continue with Google
        </button>

        <p className="login-terms">
          By continuing, you agree to our{" "}
          <a href="#">Terms</a> and <a href="#">Privacy Policy</a>.
        </p>
      </div>
    </div>
  );
}

export default Login;
