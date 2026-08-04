import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function AddBreakdownLog() {
  const [formData, setFormData] = useState({ machine_id: "", supervisor_id: "", breakdown_code: "", pds: "", breakdown_time: "", breakdown_note: "" });
  const [machines, setMachines] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [codes, setCodes] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      client.get("/corrugating/machines/list", { params: { limit: 1000 } }),
      client.get("/api/employees/list", { params: { limit: 1000 } }),
      client.get("/corrugating/breakdowns/breakdown-codes/list", { params: { limit: 1000 } }),
    ])
      .then(([machineRes, employeeRes, codeRes]) => {
        setMachines(machineRes.data);
        setEmployees(employeeRes.data);
        setCodes(codeRes.data);
      })
      .catch(() => {
        setMachines([]);
        setEmployees([]);
        setCodes([]);
      });
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!formData.machine_id || !formData.supervisor_id || !formData.breakdown_code || !formData.pds || !formData.breakdown_time) {
      setError("Vui lòng điền đầy đủ thông tin log sự cố");
      return;
    }

    setLoading(true);
    try {
      await client.post("/corrugating/breakdowns/breakdown-logs/add", {
        machine_id: Number(formData.machine_id),
        supervisor_id: Number(formData.supervisor_id),
        breakdown_code: Number(formData.breakdown_code),
        pds: formData.pds,
        breakdown_time: new Date(formData.breakdown_time).toISOString(),
        breakdown_note: formData.breakdown_note || null,
      });
      navigate("/corrugating/breakdowns/logs/list");
    } catch (err) {
      setError(err.response?.data?.detail || "Thêm log sự cố thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: 24 }}>
      <h2 style={{ marginBottom: 16 }}>Thêm log sự cố máy</h2>
      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}
      <form onSubmit={handleSubmit} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
        <select name="machine_id" value={formData.machine_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn máy --</option>
          {machines.map((item) => (
            <option key={item.machine_id} value={item.machine_id}>{item.machine_name}</option>
          ))}
        </select>
        <select name="supervisor_id" value={formData.supervisor_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn Supervisor --</option>
          {employees.map((item) => (
            <option key={item.employee_id} value={item.employee_id}>{item.employee_name}</option>
          ))}
        </select>
        <select name="breakdown_code" value={formData.breakdown_code} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn mã lỗi --</option>
          {codes.map((item) => (
            <option key={item.breakdown_code} value={item.breakdown_code}>{item.description}</option>
          ))}
        </select>
        <input name="pds" value={formData.pds} onChange={handleChange} placeholder="PDS" required style={fieldStyle} />
        <input name="breakdown_time" type="datetime-local" value={formData.breakdown_time} onChange={handleChange} required style={fieldStyle} />
        <textarea name="breakdown_note" value={formData.breakdown_note} onChange={handleChange} placeholder="Ghi chú" style={{ ...fieldStyle, minHeight: 96, gridColumn: "1 / -1" }} />
        <div style={{ gridColumn: "1 / -1", display: "flex", gap: 12 }}>
          <button type="submit" disabled={loading} style={primaryBtn}>{loading ? "Đang lưu..." : "Lưu log"}</button>
          <button type="button" onClick={() => navigate("/corrugating/breakdowns/logs/list")} style={secondaryBtn}>Hủy</button>
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
