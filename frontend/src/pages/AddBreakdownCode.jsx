import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function AddBreakdownCode() {
  const [formData, setFormData] = useState({ description: "", how_to_handle: "", expected_downtime_minutes: "" });
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

    if (!formData.description.trim()) {
      setError("Vui lòng nhập mô tả mã lỗi");
      return;
    }

    setLoading(true);
    try {
      await client.post("/corrugating/breakdowns/breakdown-codes/add", {
        description: formData.description,
        how_to_handle: formData.how_to_handle || null,
        expected_downtime_minutes: formData.expected_downtime_minutes ? Number(formData.expected_downtime_minutes) : null,
      });
      navigate("/corrugating/breakdowns/codes/list");
    } catch (err) {
      setError(err.response?.data?.detail || "Thêm mã lỗi thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 560, margin: "0 auto", padding: 24 }}>
      <h2 style={{ marginBottom: 16 }}>Thêm mã lỗi breakdown</h2>
      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
        <input name="description" value={formData.description} onChange={handleChange} placeholder="Mô tả" required style={fieldStyle} />
        <input name="how_to_handle" value={formData.how_to_handle} onChange={handleChange} placeholder="Cách xử lý" style={fieldStyle} />
        <input name="expected_downtime_minutes" type="number" value={formData.expected_downtime_minutes} onChange={handleChange} placeholder="Dự kiến downtime (phút)" style={fieldStyle} />
        <div style={{ display: "flex", gap: 12 }}>
          <button type="submit" disabled={loading} style={primaryBtn}>{loading ? "Đang lưu..." : "Lưu mã lỗi"}</button>
          <button type="button" onClick={() => navigate("/corrugating/breakdowns/codes/list")} style={secondaryBtn}>Hủy</button>
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
