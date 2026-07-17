import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";
import "./OrderList.css";

export default function OrderList() {
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState({});
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(false);
  const [assigningPds, setAssigningPds] = useState(null);

  // Load customers for mapping
  useEffect(() => {
    client
      .get("/api/customers/list", { params: { limit: 1000 } })
      .then((res) => {
        const customerMap = {};
        res.data.forEach((c) => {
          customerMap[c.customer_id] = c.customer_name;
        });
        setCustomers(customerMap);
      })
      .catch((err) => console.error("Lỗi tải khách hàng", err));
  }, []);

  // Load orders
  useEffect(() => {
    setLoading(true);
    const timeout = setTimeout(() => {
      client
        .get("/api/orders/list", {
          params: { status: statusFilter || undefined },
        })
        .then((res) => setOrders(res.data))
        .catch((err) => setError(err.response?.data?.detail || "Lỗi tải dữ liệu"))
        .finally(() => setLoading(false));
    }, 400);

    return () => clearTimeout(timeout);
  }, [statusFilter]);

  const handleAssignPds = async (orderId) => {
    if (!window.confirm("Bạn chắc chắn muốn cấp PDS cho đơn hàng này?")) {
      return;
    }

    setAssigningPds(orderId);
    try {
      const res = await client.post(`/api/orders/assign-pds/${orderId}`);
      // Update order in list
      setOrders(orders.map((o) => (o.order_id === orderId ? res.data : o)));
      alert("Cấp PDS thành công!");
    } catch (err) {
      alert(err.response?.data?.detail || "Lỗi cấp PDS");
    } finally {
      setAssigningPds(null);
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      pending: "Chờ xử lý",
      in_progress: "Đang sản xuất",
      delivered: "Đã giao",
      cancelled: "Đã hủy",
    };
    return labels[status] || status;
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: "#f39c12",
      in_progress: "#3498db",
      delivered: "#27ae60",
      cancelled: "#e74c3c",
    };
    return colors[status] || "#95a5a6";
  };

  return (
    <div className="order-list-container">
      <div className="list-header">
        <h2>Danh sách đơn hàng</h2>
        <Link to="/orders/add" className="btn-add-order">
          + Thêm đơn hàng
        </Link>
      </div>

      <div className="filter-section">
        <div className="filter-group">
          <label>Lọc theo trạng thái:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-input"
          >
            <option value="">Tất cả</option>
            <option value="pending">Chờ xử lý</option>
            <option value="in_progress">Đang sản xuất</option>
            <option value="delivered">Đã giao</option>
            <option value="cancelled">Đã hủy</option>
          </select>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="table-wrapper">
        {loading ? (
          <div className="loading">Đang tải dữ liệu...</div>
        ) : orders.length === 0 ? (
          <div className="no-data">Không có đơn hàng nào</div>
        ) : (
          <table className="order-table">
            <thead>
              <tr>
                <th>Mã đơn hàng</th>
                <th>PDS</th>
                <th>Khách hàng</th>
                <th>Ngày đặt</th>
                <th>Số lượng</th>
                <th>Trạng thái</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.order_id} className="table-row">
                  <td className="cell-id">#{order.order_id}</td>
                  <td className="cell-pds">
                    {order.pds ? (
                      <span className="pds-badge">{order.pds}</span>
                    ) : (
                      <span className="pds-empty">-</span>
                    )}
                  </td>
                  <td className="cell-customer">
                    {customers[order.customer_id] || "N/A"}
                  </td>
                  <td className="cell-date">
                    {new Date(order.order_date).toLocaleDateString("vi-VN")}
                  </td>
                  <td className="cell-quantity">{order.quantity}</td>
                  <td className="cell-status">
                    <span
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(order.order_status) }}
                    >
                      {getStatusLabel(order.order_status)}
                    </span>
                  </td>
                  <td className="cell-actions">
                    {!order.pds && order.order_status === "pending" && (
                      <button
                        className="btn-assign-pds"
                        onClick={() => handleAssignPds(order.order_id)}
                        disabled={assigningPds === order.order_id}
                      >
                        {assigningPds === order.order_id ? "Cấp PDS..." : "Cấp PDS"}
                      </button>
                    )}
                    {order.pds && (
                      <button className="btn-view" disabled>
                        ✓ Đã cấp PDS
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="list-footer">
        <span className="order-count">Tổng cộng: {orders.length} đơn hàng</span>
      </div>
    </div>
  );
}
