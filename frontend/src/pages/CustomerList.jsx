import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";
import "./CustomerList.css";

export default function CustomerList() {
  const [customers, setCustomers] = useState([]);
  const [error, setError] = useState("");
  const [nameFilter, setNameFilter] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    const timeout = setTimeout(() => {
      client
        .get("/api/customers/list", {
          params: { name: nameFilter || undefined },
        })
        .then((res) => setCustomers(res.data))
        .catch((err) => setError(err.response?.data?.detail || "Lỗi tải dữ liệu"))
        .finally(() => setLoading(false));
    }, 400);

    return () => clearTimeout(timeout);
  }, [nameFilter]);

  return (
    <div className="customer-list-container">
      <div className="list-header">
        <h2>Danh sách khách hàng</h2>
        <Link to="/customers/add" className="btn-add-customer">
          + Thêm khách hàng
        </Link>
      </div>

      <div className="filter-section">
        <div className="filter-group">
          <label>Tìm theo tên:</label>
          <input
            type="text"
            placeholder="Nhập tên khách hàng..."
            value={nameFilter}
            onChange={(e) => setNameFilter(e.target.value)}
            className="filter-input"
          />
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="table-wrapper">
        {loading ? (
          <div className="loading">Đang tải dữ liệu...</div>
        ) : customers.length === 0 ? (
          <div className="no-data">Không có khách hàng nào</div>
        ) : (
          <table className="customer-table">
            <thead>
              <tr>
                <th>Tên khách hàng</th>
                <th>Email</th>
                <th>Số điện thoại</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.customer_id} className="table-row">
                  <td className="cell-name">{customer.customer_name}</td>
                  <td className="cell-email">
                    <a href={`mailto:${customer.contact_email}`}>{customer.contact_email}</a>
                  </td>
                  <td className="cell-phone">
                    <a href={`tel:${customer.contact_phone}`}>{customer.contact_phone}</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="list-footer">
        <span className="customer-count">Tổng cộng: {customers.length} khách hàng</span>
      </div>
    </div>
  );
}
