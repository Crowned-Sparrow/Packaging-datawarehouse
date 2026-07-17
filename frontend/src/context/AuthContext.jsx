// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);

  // Khi app vừa mở, kiểm tra xem đã có token cũ trong localStorage chưa
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const savedName = localStorage.getItem("employee_name");
    const savedTitle = localStorage.getItem("employee_title");

    if (token && savedName) {
      setEmployee({ name: savedName, title: savedTitle });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const res = await client.post("/api/auth/login", { email, password });
    const { access_token, employee_name, title } = res.data;

    localStorage.setItem("access_token", access_token);
    localStorage.setItem("employee_name", employee_name);
    localStorage.setItem("employee_title", title);

    setEmployee({ name: employee_name, title });
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("employee_name");
    localStorage.removeItem("employee_title");
    setEmployee(null);
  };

  return (
    <AuthContext.Provider value={{ employee, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// custom hook để dùng gọn hơn: const { employee, login, logout } = useAuth();
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth phải được gọi bên trong <AuthProvider>");
  }
  return context;
}