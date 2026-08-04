import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function AddMachine() {
  const [formData, setFormData] = useState({ machine_name: "", lead_operator_id: "", flute_type: "A" });
  const [employees, setEmployees] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    client.get("/api/employees/list", { params: { limit: 1000 } }).then((res) => setEmployees(res.data)).catch(() => setEmployees([]));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!formData.machine_name.trim() || !formData.lead_operator_id) {
      setError("Vui lòng chọn máy và người phụ trách");
      return;
    }

    setLoading(true);
    try {
      await client.post("/corrugating/machines/add", {
        machine_name: formData.machine_name,
        lead_operator_id: Number(formData.lead_operator_id),
        flute_type: formData.flute_type,
      });
      navigate("/corrugating/machines/list");
    } catch (err) {
      setError(err.response?.data?.detail || "Thêm máy thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 560, margin: "0 auto", padding: 24 }}>
      <h2 style={{ marginBottom: 16 }}>Thêm máy corrugating</h2>
      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
        <input name="machine_name" value={formData.machine_name} onChange={handleChange} placeholder="Tên máy" required style={fieldStyle} />
        <select name="lead_operator_id" value={formData.lead_operator_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn người phụ trách --</option>
          {employees.map((item) => (
            <option key={item.employee_id} value={item.employee_id}>{item.employee_name}</option>
          ))}
        </select>
        <select name="flute_type" value={formData.flute_type} onChange={handleChange} style={fieldStyle}>
          <option value="A">A</option>
          <option value="B">B</option>
          <option value="C">C</option>
          <option value="E">E</option>
          <option value="F">F</option>
        </select>
        <div style={{ display: "flex", gap: 12 }}>
          <button type="submit" disabled={loading} style={primaryBtn}>{loading ? "Đang lưu..." : "Lưu máy"}</button>
          <button type="button" onClick={() => navigate("/corrugating/machines/list")} style={secondaryBtn}>Hủy</button>
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
