import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import "./AddOrder.css";

export default function AddOrder() {
  const [customers, setCustomers] = useState([]);
  const [formData, setFormData] = useState({
    customer_id: "",
    order_date: new Date().toISOString().split("T")[0],
    delivery_date: "",
    quantity: "",
    order_note: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Load customers
  useEffect(() => {
    client
      .get("/api/customers/list", { params: { limit: 1000 } })
      .then((res) => {
        console.log("Customers loaded:", res.data);
        setCustomers(res.data);
      })
      .catch((err) => console.error("Lỗi tải khách hàng", err));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    console.log(`${name} changed to:`, value, "type:", typeof value);
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    console.log("Form data before submit:", formData);
    console.log("customer_id value:", formData.customer_id, "type:", typeof formData.customer_id);
    
    if (!formData.customer_id) {
      setError("Vui lòng chọn khách hàng");
      return;
    }
    if (!formData.order_date) {
      setError("Vui lòng chọn ngày đặt hàng");
      return;
    }
    if (!formData.quantity || parseInt(formData.quantity) <= 0) {
      setError("Vui lòng nhập số lượng > 0");
      return;
    }

    setLoading(true);
    try {
      const customerId = parseInt(formData.customer_id);
      console.log("Parsed customer_id:", customerId, "isNaN?", isNaN(customerId));
      
      const payload = {
        customer_id: customerId,
        order_date: formData.order_date,
        delivery_date: formData.delivery_date || null,
        quantity: parseInt(formData.quantity),
        order_note: formData.order_note || null,
      };
      
      // Check for NaN
      if (isNaN(payload.customer_id)) {
        setError("Vui lòng chọn khách hàng hợp lệ");
        setLoading(false);
        return;
      }
      
      console.log("Sending order data:", payload);
      const res = await client.post("/api/orders/add", payload);
      console.log("Response:", res.data);
      navigate("/orders/list");
    } catch (err) {
      console.error("Error details:", err.response?.data);
      setError(err.response?.data?.detail || "Thêm đơn hàng thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "20px" }}>
      <h2>Thêm đơn hàng mới</h2>

      {error && <p style={{ color: "red", marginBottom: "15px" }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>
            Khách hàng *
          </label>
          <select
            name="customer_id"
            value={formData.customer_id}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
            required
          >
            <option value="">-- Chọn khách hàng --</option>
            {customers.map((c) => (
             <option key={c.customer_id} value={String(c.customer_id)}>
                {c.customer_name}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>
            Ngày đặt hàng *
          </label>
          <input
            type="date"
            name="order_date"
            value={formData.order_date}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
            required
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>
            Ngày giao hàng
          </label>
          <input
            type="date"
            name="delivery_date"
            value={formData.delivery_date}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>
            Số lượng *
          </label>
          <input
            type="number"
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", boxSizing: "border-box" }}
            min="1"
            required
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>
            Ghi chú
          </label>
          <textarea
            name="order_note"
            value={formData.order_note}
            onChange={handleChange}
            style={{
              width: "100%",
              padding: "8px",
              boxSizing: "border-box",
              minHeight: "100px",
            }}
          />
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "10px 20px",
              backgroundColor: "#8e44ad",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Đang thêm..." : "Thêm đơn hàng"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/orders/list")}
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
