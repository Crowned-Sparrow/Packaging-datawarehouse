import { useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Sidebar.css";

// Cấu trúc menu dạng nhóm -> sau này thêm chức năng mới chỉ cần thêm vào đây
const MENU = [
  {
    key: "employee",
    label: "Nhân viên",
    items: [
      { path: "/employees/profile", label: "Hồ sơ cá nhân" },
      { path: "/employees/list", label: "Danh sách nhân viên" },
      { path: "/employees/add", label: "Thêm nhân viên" },
    ],
  },
  {
    key: "customer",
    label: "Khách hàng",
    items: [
      { path: "/customers/list", label: "Danh sách khách hàng" },
      { path: "/customers/add", label: "Thêm khách hàng" },
    ],
  },
  {
    key: "order",
    label: "Đơn hàng",
    items: [
      { path: "/orders/list", label: "Danh sách đơn hàng" },
      { path: "/orders/add", label: "Thêm đơn hàng" },
    ],
  },
  {
    key: "material",
    label: "Nguyên vật liệu",
    items: [
      { path: "/materials/list", label: "Danh sách nguyên vật liệu" },
      { path: "/materials/add", label: "Thêm nguyên vật liệu" },
    ],
  },
  {
    key: "supply",
    label: "Cung ứng",
    items: [
      { path: "/supplies/suppliers/list", label: "Danh sách nhà cung cấp" },
      { path: "/supplies/suppliers/add", label: "Thêm nhà cung cấp" },
      { path: "/supplies/details/list", label: "Chi tiết cung ứng" },
    ],
  },
  {
    key: "corrugating",
    label: "Corrugating",
    items: [
      { path: "/corrugating/machines/list", label: "Danh sách máy" },
      { path: "/corrugating/machines/add", label: "Thêm máy" },
      { path: "/corrugating/logs/list", label: "Log sản xuất" },
      { path: "/corrugating/logs/add", label: "Thêm log sản xuất" },
      { path: "/corrugating/breakdowns/codes/list", label: "Mã lỗi breakdown" },
      { path: "/corrugating/breakdowns/logs/list", label: "Log sự cố máy" },
    ],
  },
];

export default function Sidebar() {
  const [openGroups, setOpenGroups] = useState(
    Object.fromEntries(MENU.map((g) => [g.key, true]))
  );
  const { employee, logout } = useAuth();

  const toggleGroup = (key) =>
    setOpenGroups((prev) => ({ ...prev, [key]: !prev[key] }));

  return (
    <aside className="sidebar">
      <div className="sidebar-header">VS Packaging</div>

      <nav className="sidebar-nav">
        {MENU.map((group) => (
          <div key={group.key} className="sidebar-group">
            <button className="sidebar-group-toggle" onClick={() => toggleGroup(group.key)}>
              <span>{group.label}</span>
              <span className={`chevron ${openGroups[group.key] ? "open" : ""}`}>›</span>
            </button>

            {openGroups[group.key] && (
              <div className="sidebar-group-items">
                {group.items.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
                  >
                    {item.label}
                  </NavLink>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-user-name">{employee?.name}</div>
          <div className="sidebar-user-title">{employee?.title}</div>
        </div>
        <button className="sidebar-logout" onClick={logout}>Đăng xuất</button>
      </div>
    </aside>
  );
}