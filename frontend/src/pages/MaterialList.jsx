import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

export default function MaterialList() {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({ code: "", name: "", type: "" });

  useEffect(() => {
    setLoading(true);
    const timeout = setTimeout(() => {
      client
        .get("/api/materials/list", {
          params: {
            material_code: filters.code || undefined,
            material_name: filters.name || undefined,
            material_type: filters.type || undefined,
          },
        })
        .then((res) => setMaterials(res.data))
        .catch((err) => setError(err.response?.data?.detail || "Lỗi tải dữ liệu"))
        .finally(() => setLoading(false));
    }, 400);

    return () => clearTimeout(timeout);
  }, [filters.code, filters.name, filters.type]);

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Danh sách nguyên vật liệu</h2>
        <Link to="/materials/add" style={{ textDecoration: "none", color: "#fff", background: "#1f6feb", padding: "10px 16px", borderRadius: 6 }}>
          + Thêm nguyên vật liệu
        </Link>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 12, marginBottom: 16 }}>
        <input value={filters.code} onChange={(e) => setFilters((prev) => ({ ...prev, code: e.target.value }))} placeholder="Mã vật liệu" style={fieldStyle} />
        <input value={filters.name} onChange={(e) => setFilters((prev) => ({ ...prev, name: e.target.value }))} placeholder="Tên vật liệu" style={fieldStyle} />
        <input value={filters.type} onChange={(e) => setFilters((prev) => ({ ...prev, type: e.target.value }))} placeholder="Loại vật liệu" style={fieldStyle} />
      </div>

      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}

      <div style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 6px 20px rgba(0,0,0,0.08)" }}>
        {loading ? (
          <div style={{ padding: 24 }}>Đang tải dữ liệu...</div>
        ) : materials.length === 0 ? (
          <div style={{ padding: 24 }}>Không có nguyên vật liệu nào</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "#f4f6fb" }}>
              <tr>
                <th style={thStyle}>Mã</th>
                <th style={thStyle}>Tên</th>
                <th style={thStyle}>Loại</th>
                <th style={thStyle}>Đơn vị</th>
              </tr>
            </thead>
            <tbody>
              {materials.map((item) => (
                <tr key={item.material_id} style={{ borderTop: "1px solid #eef2f7" }}>
                  <td style={tdStyle}>{item.material_code}</td>
                  <td style={tdStyle}>{item.material_name}</td>
                  <td style={tdStyle}>{item.material_type}</td>
                  <td style={tdStyle}>{item.unit}</td>
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
