CREATE OR REPLACE PROCEDURE sp_init_database()
LANGUAGE plpgsql AS $$
BEGIN

-- ── Extensions ────────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Tables ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS machine_report (
    machine_id          SERIAL PRIMARY KEY,
    machine_name        VARCHAR(100) NOT NULL,
    machine_type        VARCHAR(50),
    status              VARCHAR(50)  NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'inactive', 'maintenance')),
    created_at          TIMESTAMP    NOT NULL DEFAULT NOW()
);

END;
$$;

-- ── Procedure: refresh tổng kết session từ cuon ───────────────────────────────
CREATE OR REPLACE PROCEDURE sp_refresh_session_totals(p_session_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE production_session SET
        tong_ky_san_xuat  = (SELECT COALESCE(SUM(so_ky_san_xuat), 0)
                             FROM cuon WHERE session_id = p_session_id),
        tong_tam_cat_duoc = (SELECT COALESCE(SUM(so_tam_cat_duoc), 0)
                             FROM cuon WHERE session_id = p_session_id),
        tong_phe_lieu     = (SELECT COALESCE(SUM(phe_lieu_dc + phe_lieu_rm + phe_lieu_sx + phe_lieu_ong_loi), 0)
                             FROM cuon WHERE session_id = p_session_id)
    WHERE id = p_session_id;
END;
$$;