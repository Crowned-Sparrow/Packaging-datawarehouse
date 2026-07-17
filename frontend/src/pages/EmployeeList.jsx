import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";
import "./EmployeeList.css";

export default function EmployeeList() {
  const [employees, setEmployees] = useState([]);
  const [error, setError] = useState("");
  const [nameFilter, setNameFilter] = useState("");
  const [titleFilter, setTitleFilter] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    const timeout = setTimeout(() => {
      client
        .get("/api/employees/list", {
          params: { name: nameFilter || undefined, title: titleFilter || undefined },
        })
        .then((res) => setEmployees(res.data))
        .catch((err) => setError(err.response?.data?.detail || "Lỗi tải dữ liệu"))
        .finally(() => setLoading(false));
    }, 400);

    return () => clearTimeout(timeout);
  }, [nameFilter, titleFilter]);

  return (
    <div className="employee-list-container">
      <div className="list-header">
        <h2>Danh sách nhân viên</h2>
        <Link to="/employees/add" className="btn-add-employee">
          + Thêm nhân viên
        </Link>
      </div>

      <div className="filter-section">
        <div className="filter-group">
          <label>Tìm theo tên:</label>
          <input
            type="text"
            placeholder="Nhập họ tên..."
            value={nameFilter}
            onChange={(e) => setNameFilter(e.target.value)}
            className="filter-input"
          />
        </div>
        <div className="filter-group">
          <label>Tìm theo chức danh:</label>
          <input
            type="text"
            placeholder="Nhập chức danh..."
            value={titleFilter}
            onChange={(e) => setTitleFilter(e.target.value)}
            className="filter-input"
          />
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="table-wrapper">
        {loading ? (
          <div className="loading">Đang tải dữ liệu...</div>
        ) : employees.length === 0 ? (
          <div className="no-data">Không có nhân viên nào</div>
        ) : (
          <table className="employee-table">
            <thead>
              <tr>
                <th>Tên</th>
                <th>Chức danh</th>
                <th>Email</th>
                <th>Số điện thoại</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((emp) => (
                <tr key={emp.employee_id} className="table-row">
                  <td className="cell-name">{emp.employee_name}</td>
                  <td className="cell-title">{emp.title}</td>
                  <td className="cell-email">
                    <a href={`mailto:${emp.contact_email}`}>{emp.contact_email}</a>
                  </td>
                  <td className="cell-phone">
                    <a href={`tel:${emp.contact_phone}`}>{emp.contact_phone}</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="list-footer">
        <span className="employee-count">Tổng cộng: {employees.length} nhân viên</span>
      </div>
    </div>
  );
}