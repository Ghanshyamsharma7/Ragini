// src/App.jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Login from "./pages/Login";
import Chat from "./pages/Chat";
import AuthCallback from "./pages/AuthCallback";
function App() {
  return (
    <AuthProvider>
      
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/chat" element={<Chat />} />

            <Route path="/auth/callback" element={<AuthCallback />} />

          </Routes>
        </BrowserRouter>
      
    </AuthProvider>
  );
}

export default App;

