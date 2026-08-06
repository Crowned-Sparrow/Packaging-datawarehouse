import { useMemo, useState } from "react";
import client from "../api/client";
import "./SQLAssistant.css";

const EXAMPLE_QUESTIONS = [
  "Top 10 đơn hàng có số lượng lớn nhất trong tháng này",
  "Liệt kê các máy corrugating đang ở trạng thái breakdown",
  "Thống kê số lần sự cố theo machine_id trong 7 ngày gần nhất",
];

export default function SQLAssistant() {
  const [question, setQuestion] = useState("");
  const [sql, setSql] = useState("");
  const [columns, setColumns] = useState([]);
  const [rows, setRows] = useState([]);
  const [truncated, setTruncated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const hasResult = useMemo(() => columns.length > 0, [columns]);

  const handleAskSql = async (event) => {
    event.preventDefault();
    const normalizedQuestion = question.trim();
    if (!normalizedQuestion) {
      setError("Vui lòng nhập câu hỏi trước khi gửi.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await client.post("/api/assistant/ask-sql", {
        question: normalizedQuestion,
      });
      setSql(response.data.sql);
      setColumns(response.data.columns || []);
      setRows(response.data.rows || []);
      setTruncated(Boolean(response.data.truncated));
    } catch (err) {
      setSql("");
      setColumns([]);
      setRows([]);
      setTruncated(false);
      setError(err.response?.data?.detail || "Không thể tạo SQL từ câu hỏi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sql-assistant-container">
      <div className="sql-assistant-header">
        <h2>Trợ lý SQL cho nhân viên</h2>
        <p>Nhập câu hỏi nghiệp vụ bằng tiếng Việt, hệ thống sẽ sinh SQL chỉ đọc và trả kết quả trực tiếp.</p>
      </div>

      <form className="sql-assistant-form" onSubmit={handleAskSql}>
        <label htmlFor="sql-question">Câu hỏi</label>
        <textarea
          id="sql-question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ví dụ: Cho tôi 20 đơn hàng pending mới nhất"
          rows={4}
          disabled={loading}
        />
        <div className="sql-assistant-actions">
          <button type="submit" disabled={loading}>
            {loading ? "Đang xử lý..." : "Sinh SQL"}
          </button>
        </div>
      </form>

      <div className="sql-assistant-examples">
        <span>Gợi ý nhanh:</span>
        <div className="example-list">
          {EXAMPLE_QUESTIONS.map((item) => (
            <button key={item} type="button" onClick={() => setQuestion(item)} disabled={loading}>
              {item}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="sql-assistant-error">{error}</div>}

      {sql && (
        <div className="sql-result-block">
          <h3>SQL được sinh</h3>
          <pre>{sql}</pre>
        </div>
      )}

      {hasResult && (
        <div className="sql-result-block">
          <h3>Kết quả truy vấn ({rows.length} dòng)</h3>
          <div className="sql-table-wrapper">
            <table className="sql-result-table">
              <thead>
                <tr>
                  {columns.map((column) => (
                    <th key={column}>{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length}>Không có dữ liệu phù hợp.</td>
                  </tr>
                ) : (
                  rows.map((row, index) => (
                    <tr key={index}>
                      {columns.map((column) => (
                        <td key={`${index}-${column}`}>{row[column] == null ? "-" : String(row[column])}</td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {truncated && <p className="sql-truncated-note">Kết quả đã được giới hạn tối đa 200 dòng.</p>}
        </div>
      )}
    </div>
  );
}
