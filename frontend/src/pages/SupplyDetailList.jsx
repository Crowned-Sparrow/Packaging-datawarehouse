import { useEffect, useState } from "react";
import client from "../api/client";

export default function SupplyDetailList() {
  const [details, setDetails] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({ supplier_id: "", material_id: "", quantity: "", unit_price: "", request_date: "", receive_date: "" });

  useEffect(() => {
    Promise.all([
      client.get("/api/supplies/list/suppliers", { params: { limit: 1000 } }),
      client.get("/api/materials/list", { params: { limit: 1000 } }),
      client.get("/api/supplies/list/supply_details", { params: { limit: 1000 } }),
    ])
      .then(([supplierRes, materialRes, detailRes]) => {
        setSuppliers(supplierRes.data);
        setMaterials(materialRes.data);
        setDetails(detailRes.data);
      })
      .catch((err) => setError(err.response?.data?.detail || "Lỗi tải dữ liệu"));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        supplier_id: Number(formData.supplier_id),
        material_id: Number(formData.material_id),
        quantity: Number(formData.quantity),
        unit_price: Number(formData.unit_price),
        request_date: formData.request_date,
        receive_date: formData.receive_date,
      };
      await client.post("/api/supplies/add/supply_details", payload);
      const res = await client.get("/api/supplies/list/supply_details", { params: { limit: 1000 } });
      setDetails(res.data);
      setFormData({ supplier_id: "", material_id: "", quantity: "", unit_price: "", request_date: "", receive_date: "" });
    } catch (err) {
      setError(err.response?.data?.detail || "Thêm chi tiết cung ứng thất bại");
    } finally {
      setLoading(false);
    }
  };

  const supplierMap = Object.fromEntries(suppliers.map((item) => [item.supplier_id, item.supplier_name]));
  const materialMap = Object.fromEntries(materials.map((item) => [item.material_id, item.material_name]));

  return (
    <div style={{ padding: 20 }}>
      <h2 style={{ marginBottom: 16 }}>Chi tiết cung ứng</h2>
      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}

      <form onSubmit={handleSubmit} style={{ background: "#fff", padding: 16, borderRadius: 12, boxShadow: "0 6px 20px rgba(0,0,0,0.08)", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12, marginBottom: 20 }}>
        <select name="supplier_id" value={formData.supplier_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn nhà cung cấp --</option>
          {suppliers.map((item) => (
            <option key={item.supplier_id} value={item.supplier_id}>{item.supplier_name}</option>
          ))}
        </select>
        <select name="material_id" value={formData.material_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn nguyên vật liệu --</option>
          {materials.map((item) => (
            <option key={item.material_id} value={item.material_id}>{item.material_name}</option>
          ))}
        </select>
        <input name="quantity" type="number" min="1" value={formData.quantity} onChange={handleChange} placeholder="Số lượng" required style={fieldStyle} />
        <input name="unit_price" type="number" min="0" step="0.01" value={formData.unit_price} onChange={handleChange} placeholder="Đơn giá" required style={fieldStyle} />
        <input name="request_date" type="date" value={formData.request_date} onChange={handleChange} required style={fieldStyle} />
        <input name="receive_date" type="date" value={formData.receive_date} onChange={handleChange} required style={fieldStyle} />
        <div style={{ gridColumn: "1 / -1" }}>
          <button type="submit" disabled={loading} style={primaryBtn}>{loading ? "Đang lưu..." : "Lưu chi tiết cung ứng"}</button>
        </div>
      </form>

      <div style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 6px 20px rgba(0,0,0,0.08)" }}>
        {details.length === 0 ? (
          <div style={{ padding: 24 }}>Không có chi tiết cung ứng nào</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "#f4f6fb" }}>
              <tr>
                <th style={thStyle}>Nhà cung cấp</th>
                <th style={thStyle}>Nguyên vật liệu</th>
                <th style={thStyle}>Số lượng</th>
                <th style={thStyle}>Đơn giá</th>
                <th style={thStyle}>Ngày yêu cầu</th>
                <th style={thStyle}>Ngày nhận</th>
              </tr>
            </thead>
            <tbody>
              {details.map((item) => (
                <tr key={item.supply_detail_id} style={{ borderTop: "1px solid #eef2f7" }}>
                  <td style={tdStyle}>{supplierMap[item.supplier_id] || item.supplier_id}</td>
                  <td style={tdStyle}>{materialMap[item.material_id] || item.material_id}</td>
                  <td style={tdStyle}>{item.quantity}</td>
                  <td style={tdStyle}>{item.unit_price}</td>
                  <td style={tdStyle}>{item.request_date}</td>
                  <td style={tdStyle}>{item.receive_date}</td>
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

const primaryBtn = {
  padding: "10px 16px",
  background: "#1f6feb",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  cursor: "pointer",
};
