import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function AddSupplier() {
  const [formData, setFormData] = useState({ supplier_name: "", contact_email: "", contact_phone: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!formData.supplier_name.trim() || !formData.contact_email.trim() || !formData.contact_phone.trim()) {
      setError("Vui lòng điền đủ thông tin nhà cung cấp");
      return;
    }

    setLoading(true);
    try {
      await client.post("/api/supplies/add/suppliers", formData);
      navigate("/supplies/suppliers/list");
    } catch (err) {
      setError(err.response?.data?.detail || "Thêm nhà cung cấp thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 560, margin: "0 auto", padding: 24 }}>
      <h2 style={{ marginBottom: 16 }}>Thêm nhà cung cấp</h2>
      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
        <input name="supplier_name" value={formData.supplier_name} onChange={handleChange} placeholder="Tên nhà cung cấp" required style={fieldStyle} />
        <input name="contact_email" type="email" value={formData.contact_email} onChange={handleChange} placeholder="Email" required style={fieldStyle} />
        <input name="contact_phone" value={formData.contact_phone} onChange={handleChange} placeholder="Số điện thoại" required style={fieldStyle} />
        <div style={{ display: "flex", gap: 12 }}>
          <button type="submit" disabled={loading} style={primaryBtn}>{loading ? "Đang lưu..." : "Lưu nhà cung cấp"}</button>
          <button type="button" onClick={() => navigate("/supplies/suppliers/list")} style={secondaryBtn}>Hủy</button>
        </div>
      </form>
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

const primaryBtn = {
  padding: "10px 16px",
  background: "#1f6feb",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  cursor: "pointer",
};

const secondaryBtn = {
  padding: "10px 16px",
  background: "#667085",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  cursor: "pointer",
};
