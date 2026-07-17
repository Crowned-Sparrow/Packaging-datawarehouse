import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function AddEmployee() {
  const [formData, setFormData] = useState({
    employee_name: "",
    title: "",
    contact_email: "",
    contact_phone: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.employee_name.trim()) {
      setError("Vui lòng nhập họ tên");
      return;
    }
    if (!formData.title.trim()) {
      setError("Vui lòng nhập chức danh");
      return;
    }
    if (!formData.contact_email.trim()) {
      setError("Vui lòng nhập email");
      return;
    }
    if (!formData.contact_phone.trim()) {
      setError("Vui lòng nhập số điện thoại");
      return;
    }
    if (!formData.password.trim()) {
      setError("Vui lòng nhập mật khẩu");
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError("Mật khẩu không khớp");
      return;
    }

    setLoading(true);
    try {
      await client.post("/api/employees/add", {
        employee_name: formData.employee_name,
        title: formData.title,
        contact_email: formData.contact_email,
        contact_phone: formData.contact_phone,
        password: formData.password,
      });
      navigate("/employees/list");
    } catch (err) {
      setError(err.response?.data?.detail || "Thêm nhân viên thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto", padding: "20px" }}>
      <h2>Thêm nhân viên mới</h2>

      {error && <p style={{ color: "red", marginBottom: "15px" }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>Họ tên *</label>
          <input
            type="text"
            name="employee_name"
            value={formData.employee_name}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
            required
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>Chức danh *</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
            required
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>Email *</label>
          <input
            type="email"
            name="contact_email"
            value={formData.contact_email}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
            required
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>Số điện thoại *</label>
          <input
            type="tel"
            name="contact_phone"
            value={formData.contact_phone}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
            required
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>Mật khẩu *</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
            required
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>Xác nhận mật khẩu *</label>
          <input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
            required
          />
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "10px 20px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Đang thêm..." : "Thêm nhân viên"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/employees/list")}
            style={{
              padding: "10px 20px",
              backgroundColor: "#6c757d",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Hủy
          </button>
        </div>
      </form>
    </div>
  );
}