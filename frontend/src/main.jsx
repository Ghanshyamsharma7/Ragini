import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import "./app.css";

import { AuthProvider } from "./context/AuthContext";


// Force #root to never exceed viewport — overrides all CSS conflicts
const root = document.getElementById("root");
root.style.height = "100vh";
root.style.maxHeight = "100vh";
root.style.overflow = "hidden";
root.style.display = "flex";
root.style.flexDirection = "column";


ReactDOM.createRoot(document.getElementById("root")).render(
  <AuthProvider>
    <App />
  </AuthProvider>
);

