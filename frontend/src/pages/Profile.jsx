import { useEffect, useState } from "react";
import client from "../api/client";
import "./Profile.css";

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get("/api/employees/me")
      .then((res) => setProfile(res.data))
      .catch((err) => setError(err.response?.data?.detail || "Lỗi tải hồ sơ"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading">Đang tải hồ sơ...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h2>Hồ sơ cá nhân</h2>
      </div>

      <div className="profile-card">
        <div className="profile-avatar">
          <div className="avatar-placeholder">
            {profile.employee_name.charAt(0).toUpperCase()}
          </div>
        </div>

        <div className="profile-content">
          <div className="profile-item">
            <label className="profile-label">Họ tên</label>
            <p className="profile-value">{profile.employee_name}</p>
          </div>

          <div className="profile-item">
            <label className="profile-label">Chức danh</label>
            <p className="profile-value">{profile.title}</p>
          </div>

          <div className="profile-item">
            <label className="profile-label">Email</label>
            <p className="profile-value">
              <a href={`mailto:${profile.contact_email}`}>{profile.contact_email}</a>
            </p>
          </div>

          <div className="profile-item">
            <label className="profile-label">Số điện thoại</label>
            <p className="profile-value">
              <a href={`tel:${profile.contact_phone}`}>{profile.contact_phone}</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}