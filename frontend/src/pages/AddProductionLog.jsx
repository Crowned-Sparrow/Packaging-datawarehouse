import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function AddProductionLog() {
  const [formData, setFormData] = useState({ leader_id: "", manager_id: "", operator_id: "", supervisor_id: "", start_time: "", pds: "", log_note: "", machine_id: "", product_id: "" });
  const [employees, setEmployees] = useState([]);
  const [machines, setMachines] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      client.get("/api/employees/list", { params: { limit: 1000 } }),
      client.get("/corrugating/machines/list", { params: { limit: 1000 } }),
    ])
      .then(([employeeRes, machineRes]) => {
        setEmployees(employeeRes.data);
        setMachines(machineRes.data);
      })
      .catch(() => {
        setEmployees([]);
        setMachines([]);
      });
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!formData.start_time || !formData.pds || !formData.machine_id || !formData.product_id || !formData.leader_id || !formData.manager_id || !formData.operator_id || !formData.supervisor_id) {
      setError("Vui lòng điền đầy đủ thông tin log sản xuất");
      return;
    }

    setLoading(true);
    try {
      await client.post("/corrugating/logs/add", {
        leader_id: Number(formData.leader_id),
        manager_id: Number(formData.manager_id),
        operator_id: Number(formData.operator_id),
        supervisor_id: Number(formData.supervisor_id),
        start_time: new Date(formData.start_time).toISOString(),
        pds: formData.pds,
        log_note: formData.log_note || null,
        machine_id: Number(formData.machine_id),
        product_id: Number(formData.product_id),
      });
      navigate("/corrugating/logs/list");
    } catch (err) {
      setError(err.response?.data?.detail || "Thêm log sản xuất thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: 24 }}>
      <h2 style={{ marginBottom: 16 }}>Thêm log sản xuất</h2>
      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}
      <form onSubmit={handleSubmit} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
        <input name="pds" value={formData.pds} onChange={handleChange} placeholder="PDS" required style={fieldStyle} />
        <select name="machine_id" value={formData.machine_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn máy --</option>
          {machines.map((item) => (
            <option key={item.machine_id} value={item.machine_id}>{item.machine_name}</option>
          ))}
        </select>
        <input name="product_id" type="number" value={formData.product_id} onChange={handleChange} placeholder="Product ID" required style={fieldStyle} />
        <input name="start_time" type="datetime-local" value={formData.start_time} onChange={handleChange} required style={fieldStyle} />
        <select name="leader_id" value={formData.leader_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn Leader --</option>
          {employees.map((item) => (
            <option key={item.employee_id} value={item.employee_id}>{item.employee_name}</option>
          ))}
        </select>
        <select name="operator_id" value={formData.operator_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn Operator --</option>
          {employees.map((item) => (
            <option key={item.employee_id} value={item.employee_id}>{item.employee_name}</option>
          ))}
        </select>
        <select name="manager_id" value={formData.manager_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn Manager --</option>
          {employees.map((item) => (
            <option key={item.employee_id} value={item.employee_id}>{item.employee_name}</option>
          ))}
        </select>
        <select name="supervisor_id" value={formData.supervisor_id} onChange={handleChange} required style={fieldStyle}>
          <option value="">-- Chọn Supervisor --</option>
          {employees.map((item) => (
            <option key={item.employee_id} value={item.employee_id}>{item.employee_name}</option>
          ))}
        </select>
        <textarea name="log_note" value={formData.log_note} onChange={handleChange} placeholder="Ghi chú" style={{ ...fieldStyle, minHeight: 96, gridColumn: "1 / -1" }} />
        <div style={{ gridColumn: "1 / -1", display: "flex", gap: 12 }}>
          <button type="submit" disabled={loading} style={primaryBtn}>{loading ? "Đang lưu..." : "Lưu log"}</button>
          <button type="button" onClick={() => navigate("/corrugating/logs/list")} style={secondaryBtn}>Hủy</button>
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
