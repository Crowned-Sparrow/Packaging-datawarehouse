import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

export default function BreakdownCodeList() {
  const [codes, setCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [descriptionFilter, setDescriptionFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    const timeout = setTimeout(() => {
      client
        .get("/corrugating/breakdowns/breakdown-codes/list", { params: { description: descriptionFilter || undefined } })
        .then((res) => setCodes(res.data))
        .catch((err) => setError(err.response?.data?.detail || "Lỗi tải dữ liệu"))
        .finally(() => setLoading(false));
    }, 400);

    return () => clearTimeout(timeout);
  }, [descriptionFilter]);

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Mã lỗi breakdown</h2>
        <Link to="/corrugating/breakdowns/codes/add" style={{ textDecoration: "none", color: "#fff", background: "#1f6feb", padding: "10px 16px", borderRadius: 6 }}>
          + Thêm mã lỗi
        </Link>
      </div>

      <div style={{ marginBottom: 16 }}>
        <input value={descriptionFilter} onChange={(e) => setDescriptionFilter(e.target.value)} placeholder="Tìm theo mô tả" style={fieldStyle} />
      </div>

      {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}

      <div style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 6px 20px rgba(0,0,0,0.08)" }}>
        {loading ? (
          <div style={{ padding: 24 }}>Đang tải dữ liệu...</div>
        ) : codes.length === 0 ? (
          <div style={{ padding: 24 }}>Không có mã lỗi nào</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "#f4f6fb" }}>
              <tr>
                <th style={thStyle}>Mã</th>
                <th style={thStyle}>Mô tả</th>
                <th style={thStyle}>Cách xử lý</th>
                <th style={thStyle}>Dự kiến downtime (phút)</th>
              </tr>
            </thead>
            <tbody>
              {codes.map((item) => (
                <tr key={item.breakdown_code} style={{ borderTop: "1px solid #eef2f7" }}>
                  <td style={tdStyle}>{item.breakdown_code}</td>
                  <td style={tdStyle}>{item.description}</td>
                  <td style={tdStyle}>{item.how_to_handle || "-"}</td>
                  <td style={tdStyle}>{item.expected_downtime_minutes ?? "-"}</td>
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
