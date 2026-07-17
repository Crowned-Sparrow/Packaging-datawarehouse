// src/components/ProtectedRoute.jsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute() {
  const { employee, loading } = useAuth();

  if (loading) return <p>Đang tải...</p>;
  if (!employee) return <Navigate to="/login" replace />;

  return <Outlet />;
}