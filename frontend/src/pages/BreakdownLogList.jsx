import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

export default function BreakdownLogList() {
  const [logs, setLogs] = useState([]);
  const [machines, setMachines] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [codes, setCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    Promise.all([
      client.get("/corrugating/machines/list", { params: { limit: 1000 } }),
      client.get("/api/employees/list", { params: { limit: 1000 } }),
      client.get("/corrugating/breakdowns/breakdown-codes/list", { params: { limit: 1000 } }),
      client.get("/corrugating/breakdowns/breakdown-logs/list", { params: { limit: 1000 } }),
    ])
      .then(([machineRes, employeeRes, codeRes, logRes]) => {
        setMachines(machineRes.data);
        setEmployees(employeeRes.data);
        setCodes(codeRes.data);
        setLogs(logRes.data);
      })
      .catch((err) => setError(err.response?.data?.detail || "Lỗi tải dữ liệu"))
      .finally(() => setLoading(false));
  }, []);

  const machineMap = Object.fromEntries(machines.map((item) => [item.machine_id, item.machine_name]));
  const employeeMap = Object.fromEntries(employees.map((item) => [item.employee_id, item.employee_name]));
  const codeMap = Object.fromEntries(codes.map((item) => [item.breakdown_code, item.description]));

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Log sự cố máy</h2>
        <Link to="/corrugating/breakdowns/logs/add" style={{ textDecoration: "none", color: "#fff", background: "#1f6feb", padding: "10px 16px", borderRadius: 6 }}>
          + Thêm log sự cố
        </Link>
      </div>

      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}

      <div style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 6px 20px rgba(0,0,0,0.08)" }}>
        {loading ? (
          <div style={{ padding: 24 }}>Đang tải dữ liệu...</div>
        ) : logs.length === 0 ? (
          <div style={{ padding: 24 }}>Không có log sự cố nào</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "#f4f6fb" }}>
              <tr>
                <th style={thStyle}>Máy</th>
                <th style={thStyle}>Supervisor</th>
                <th style={thStyle}>Mã lỗi</th>
                <th style={thStyle}>Thời gian hỏng</th>
                <th style={thStyle}>Thời gian phục hồi</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((item) => (
                <tr key={item.breakdown_log_id} style={{ borderTop: "1px solid #eef2f7" }}>
                  <td style={tdStyle}>{machineMap[item.machine_id] || item.machine_id}</td>
                  <td style={tdStyle}>{employeeMap[item.supervisor_id] || item.supervisor_id}</td>
                  <td style={tdStyle}>{codeMap[item.breakdown_code] || item.breakdown_code}</td>
                  <td style={tdStyle}>{item.breakdown_time ? new Date(item.breakdown_time).toLocaleString("vi-VN") : "-"}</td>
                  <td style={tdStyle}>{item.recovery_time ? new Date(item.recovery_time).toLocaleString("vi-VN") : "-"}</td>
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
