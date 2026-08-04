import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

export default function ProductionLogList() {
  const [logs, setLogs] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    Promise.all([
      client.get("/api/employees/list", { params: { limit: 1000 } }),
      client.get("/corrugating/machines/list", { params: { limit: 1000 } }),
      client.get("/corrugating/logs/list", { params: { limit: 1000 } }),
    ])
      .then(([employeeRes, machineRes, logRes]) => {
        setEmployees(employeeRes.data);
        setMachines(machineRes.data);
        setLogs(logRes.data);
      })
      .catch((err) => setError(err.response?.data?.detail || "Lỗi tải dữ liệu"))
      .finally(() => setLoading(false));
  }, []);

  const employeeMap = Object.fromEntries(employees.map((item) => [item.employee_id, item.employee_name]));
  const machineMap = Object.fromEntries(machines.map((item) => [item.machine_id, item.machine_name]));

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Log sản xuất corrugating</h2>
        <Link to="/corrugating/logs/add" style={{ textDecoration: "none", color: "#fff", background: "#1f6feb", padding: "10px 16px", borderRadius: 6 }}>
          + Thêm log sản xuất
        </Link>
      </div>

      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}

      <div style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 6px 20px rgba(0,0,0,0.08)" }}>
        {loading ? (
          <div style={{ padding: 24 }}>Đang tải dữ liệu...</div>
        ) : logs.length === 0 ? (
          <div style={{ padding: 24 }}>Không có log sản xuất nào</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "#f4f6fb" }}>
              <tr>
                <th style={thStyle}>PDS</th>
                <th style={thStyle}>Máy</th>
                <th style={thStyle}>Leader</th>
                <th style={thStyle}>Operator</th>
                <th style={thStyle}>Bắt đầu</th>
                <th style={thStyle}>Kết thúc</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((item) => (
                <tr key={item.production_log_id} style={{ borderTop: "1px solid #eef2f7" }}>
                  <td style={tdStyle}>{item.pds}</td>
                  <td style={tdStyle}>{machineMap[item.machine_id] || item.machine_id}</td>
                  <td style={tdStyle}>{employeeMap[item.leader_id] || item.leader_id}</td>
                  <td style={tdStyle}>{employeeMap[item.operator_id] || item.operator_id}</td>
                  <td style={tdStyle}>{item.start_time ? new Date(item.start_time).toLocaleString("vi-VN") : "-"}</td>
                  <td style={tdStyle}>{item.end_time ? new Date(item.end_time).toLocaleString("vi-VN") : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

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
