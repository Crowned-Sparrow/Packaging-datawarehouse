import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

export default function SupplierList() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [nameFilter, setNameFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    const timeout = setTimeout(() => {
      client
        .get("/api/supplies/list/suppliers", { params: { name: nameFilter || undefined } })
        .then((res) => setSuppliers(res.data))
        .catch((err) => setError(err.response?.data?.detail || "Lỗi tải dữ liệu"))
        .finally(() => setLoading(false));
    }, 400);

    return () => clearTimeout(timeout);
  }, [nameFilter]);

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Danh sách nhà cung cấp</h2>
        <Link to="/supplies/suppliers/add" style={{ textDecoration: "none", color: "#fff", background: "#1f6feb", padding: "10px 16px", borderRadius: 6 }}>
          + Thêm nhà cung cấp
        </Link>
      </div>

      <div style={{ marginBottom: 16 }}>
        <input value={nameFilter} onChange={(e) => setNameFilter(e.target.value)} placeholder="Tìm theo tên nhà cung cấp" style={fieldStyle} />
      </div>

      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}

      <div style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 6px 20px rgba(0,0,0,0.08)" }}>
        {loading ? (
          <div style={{ padding: 24 }}>Đang tải dữ liệu...</div>
        ) : suppliers.length === 0 ? (
          <div style={{ padding: 24 }}>Không có nhà cung cấp nào</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "#f4f6fb" }}>
              <tr>
                <th style={thStyle}>Tên</th>
                <th style={thStyle}>Email</th>
                <th style={thStyle}>Số điện thoại</th>
              </tr>
            </thead>
            <tbody>
              {suppliers.map((item) => (
                <tr key={item.supplier_id} style={{ borderTop: "1px solid #eef2f7" }}>
                  <td style={tdStyle}>{item.supplier_name}</td>
                  <td style={tdStyle}>{item.contact_email}</td>
                  <td style={tdStyle}>{item.contact_phone}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

const fieldStyle = {
  width: "100%",
  padding: "10px 12px",
  border: "1px solid #d9e2f0",
  borderRadius: 8,
  boxSizing: "border-box",
};

const thStyle = {
  padding: "12px 16px",
  textAlign: "left",
  fontSize: 13,
  color: "#475467",
};

const tdStyle = {
  padding: "12px 16px",
  fontSize: 14,
  color: "#101828",
};
