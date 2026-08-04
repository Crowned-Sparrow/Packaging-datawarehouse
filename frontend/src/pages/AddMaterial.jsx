import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function AddMaterial() {
  const [formData, setFormData] = useState({ material_code: "", material_name: "", material_type: "", unit: "" });
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

    if (!formData.material_code.trim() || !formData.material_name.trim() || !formData.material_type.trim() || !formData.unit.trim()) {
      setError("Vui lòng điền đầy đủ thông tin nguyên vật liệu");
      return;
    }

    setLoading(true);
    try {
      await client.post("/api/materials/add", formData);
      navigate("/materials/list");
    } catch (err) {
      setError(err.response?.data?.detail || "Thêm nguyên vật liệu thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 560, margin: "0 auto", padding: 24 }}>
      <h2 style={{ marginBottom: 16 }}>Thêm nguyên vật liệu</h2>
      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
        <input name="material_code" value={formData.material_code} onChange={handleChange} placeholder="Mã vật liệu" required style={fieldStyle} />
        <input name="material_name" value={formData.material_name} onChange={handleChange} placeholder="Tên vật liệu" required style={fieldStyle} />
        <input name="material_type" value={formData.material_type} onChange={handleChange} placeholder="Loại vật liệu" required style={fieldStyle} />
        <input name="unit" value={formData.unit} onChange={handleChange} placeholder="Đơn vị" required style={fieldStyle} />
        <div style={{ display: "flex", gap: 12 }}>
          <button type="submit" disabled={loading} style={primaryBtn}>{loading ? "Đang lưu..." : "Lưu nguyên vật liệu"}</button>
          <button type="button" onClick={() => navigate("/materials/list")} style={secondaryBtn}>Hủy</button>
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
