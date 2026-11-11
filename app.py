import math
import os
import sqlite3
from datetime import date, datetime, timedelta

from flask import Flask, flash, get_flashed_messages, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "hang-van-tai-key"
DB_PATH = os.path.join(os.path.dirname(__file__), "hang_van_tai.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS HeSo (
            DoPhucTap INTEGER PRIMARY KEY,
            LuongPhuXe INTEGER NOT NULL,
            HeSoKm REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Xe (
            MaXe INTEGER PRIMARY KEY AUTOINCREMENT,
            BienSo TEXT NOT NULL UNIQUE,
            MauXe TEXT,
            HangSanXuat TEXT,
            DoiXe INTEGER,
            Model TEXT,
            SoGhe INTEGER NOT NULL,
            SoNamSuDung INTEGER,
            NgayBaoDuongCuoi DATE
        );

        CREATE TABLE IF NOT EXISTS TaiXe (
            MaTX INTEGER PRIMARY KEY AUTOINCREMENT,
            HoTen TEXT NOT NULL,
            CMT TEXT NOT NULL UNIQUE,
            MaSoBangLai TEXT NOT NULL UNIQUE,
            LoaiBangLai TEXT,
            DiaChi TEXT,
            NgaySinh DATE,
            ThamNien INTEGER
        );

        CREATE TABLE IF NOT EXISTS Tuyen (
            MaTuyen INTEGER PRIMARY KEY AUTOINCREMENT,
            DiemDau TEXT NOT NULL,
            DiemCuoi TEXT NOT NULL,
            DoDai REAL NOT NULL,
            DoPhucTap INTEGER NOT NULL,
            FOREIGN KEY (DoPhucTap) REFERENCES HeSo(DoPhucTap)
        );

        CREATE TABLE IF NOT EXISTS Chuyen (
            MaChuyen INTEGER PRIMARY KEY AUTOINCREMENT,
            MaTuyen INTEGER NOT NULL,
            MaXe INTEGER NOT NULL,
            MaLaiXe INTEGER NOT NULL,
            MaPhuXe INTEGER NOT NULL,
            NgayKhoiHanh DATETIME NOT NULL,
            SoKhach INTEGER NOT NULL,
            GiaVe INTEGER NOT NULL,
            FOREIGN KEY (MaTuyen) REFERENCES Tuyen(MaTuyen),
            FOREIGN KEY (MaXe) REFERENCES Xe(MaXe),
            FOREIGN KEY (MaLaiXe) REFERENCES TaiXe(MaTX),
            FOREIGN KEY (MaPhuXe) REFERENCES TaiXe(MaTX)
        );
        """
    )

    conn.executemany(
        "INSERT OR IGNORE INTO HeSo (DoPhucTap, LuongPhuXe, HeSoKm) VALUES (?, ?, ?)",
        [(1, 200000, 1.0), (2, 260000, 1.5), (3, 340000, 2.0)],
    )

    conn.executemany(
        "INSERT OR IGNORE INTO Xe (MaXe, BienSo, MauXe, HangSanXuat, DoiXe, Model, SoGhe, SoNamSuDung, NgayBaoDuongCuoi) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "29B-123.45", "Trắng", "Hyundai", 2020, "Universe", 45, 6, "2026-08-10"),
            (2, "29B-234.56", "Xanh", "Thaco", 2019, "Garden", 40, 7, "2026-05-20"),
            (3, "30F-345.67", "Đỏ", "Samco", 2021, "Felix", 29, 5, "2026-09-15"),
            (4, "30F-456.78", "Trắng", "Hyundai", 2018, "County", 29, 8, "2025-09-01"),
        ],
    )

    conn.executemany(
        "INSERT OR IGNORE INTO TaiXe (MaTX, HoTen, CMT, MaSoBangLai, LoaiBangLai, DiaChi, NgaySinh, ThamNien) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "Nguyễn Văn An", "001085012345", "010085001234", "E", "Hà Nội", "1985-04-12", 16),
            (2, "Trần Văn Bình", "001088023456", "010088002345", "FC", "Hà Nội", "1988-09-23", 14),
            (3, "Lê Minh Cường", "034090034567", "034090003456", "E", "Thái Bình", "1990-01-05", 12),
            (4, "Phạm Quốc Dũng", "001092045678", "010092004567", "D", "Hà Nội", "1992-11-30", 9),
            (5, "Hoàng Văn Em", "038086056789", "038086005678", "FC", "Thanh Hóa", "1986-07-19", 17),
            (6, "Vũ Thành Phong", "001095067890", "010095006789", "D", "Hà Nội", "1995-02-14", 7),
        ],
    )

    conn.executemany(
        "INSERT OR IGNORE INTO Tuyen (MaTuyen, DiemDau, DiemCuoi, DoDai, DoPhucTap) VALUES (?, ?, ?, ?, ?)",
        [
            (1, "Hà Nội", "Hải Phòng", 120, 1),
            (2, "Hà Nội", "Vinh", 300, 2),
            (3, "Hà Nội", "Sa Pa", 320, 3),
            (4, "Hà Nội", "Đà Nẵng", 770, 2),
        ],
    )

    conn.executemany(
        "INSERT OR IGNORE INTO Chuyen (MaChuyen, MaTuyen, MaXe, MaLaiXe, MaPhuXe, NgayKhoiHanh, SoKhach, GiaVe) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1, 1, 1, 1, 2, "2026-10-02 06:00:00", 40, 120000),
            (2, 2, 2, 3, 4, "2026-10-03 07:00:00", 35, 250000),
            (3, 3, 3, 5, 6, "2026-10-05 20:00:00", 25, 280000),
            (4, 4, 4, 5, 6, "2026-10-06 18:00:00", 25, 450000),
            (5, 1, 1, 2, 1, "2026-10-08 06:30:00", 42, 120000),
            (6, 1, 4, 4, 3, "2026-10-09 09:00:00", 22, 120000),
            (7, 3, 3, 6, 5, "2026-10-10 17:00:00", 20, 280000),
            (8, 2, 1, 1, 3, "2026-10-12 07:00:00", 43, 250000),
        ],
    )

    conn.commit()
    conn.close()


def get_count(table_name):
    conn = get_db_connection()
    count = conn.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()["count"]
    conn.close()
    return count


def get_driver_payroll(month_filter=None):
    conn = get_db_connection()
    if month_filter:
        month_parts = month_filter.split("-")
        if len(month_parts) == 2:
            year, month = map(int, month_parts)
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        else:
            month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = datetime.now()
    else:
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = datetime.now()

    month_start_str = month_start.strftime("%Y-%m-%d %H:%M:%S")
    month_end_str = month_end.strftime("%Y-%m-%d %H:%M:%S")

    rows = conn.execute(
        """
        SELECT tx.MaTX, tx.HoTen,
               IFNULL((SELECT SUM(2 * hs.LuongPhuXe)
                       FROM Chuyen c
                       JOIN Tuyen tu ON c.MaTuyen = tu.MaTuyen
                       JOIN HeSo hs ON tu.DoPhucTap = hs.DoPhucTap
                       WHERE c.MaLaiXe = tx.MaTX
                         AND c.NgayKhoiHanh >= ?
                         AND c.NgayKhoiHanh <= ?), 0)
               + IFNULL((SELECT SUM(hs.LuongPhuXe)
                         FROM Chuyen c
                         JOIN Tuyen tu ON c.MaTuyen = tu.MaTuyen
                         JOIN HeSo hs ON tu.DoPhucTap = hs.DoPhucTap
                         WHERE c.MaPhuXe = tx.MaTX
                           AND c.NgayKhoiHanh >= ?
                           AND c.NgayKhoiHanh <= ?), 0) AS Luong
        FROM TaiXe tx
        ORDER BY tx.HoTen
        """,
        (month_start_str, month_end_str, month_start_str, month_end_str),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_vehicle_revenue(start_date, end_date):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT x.MaXe, x.BienSo,
               IFNULL(SUM(c.SoKhach * c.GiaVe), 0) AS DoanhThu
        FROM Xe x
        LEFT JOIN Chuyen c ON x.MaXe = c.MaXe
            AND c.NgayKhoiHanh >= ?
            AND c.NgayKhoiHanh < ?
        GROUP BY x.MaXe, x.BienSo
        ORDER BY DoanhThu DESC
        """,
        (start_date, end_date),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_vehicle_maintenance():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT x.MaXe, x.BienSo, x.NgayBaoDuongCuoi,
               COALESCE(SUM(t.DoDai * hs.HeSoKm), 0) AS KmLamViec
        FROM Xe x
        LEFT JOIN Chuyen c ON x.MaXe = c.MaXe
            AND c.NgayKhoiHanh > x.NgayBaoDuongCuoi
            AND c.NgayKhoiHanh <= datetime('now')
        LEFT JOIN Tuyen t ON c.MaTuyen = t.MaTuyen
        LEFT JOIN HeSo hs ON t.DoPhucTap = hs.DoPhucTap
        GROUP BY x.MaXe, x.BienSo, x.NgayBaoDuongCuoi
        ORDER BY x.MaXe
        """
    ).fetchall()
    conn.close()

    result = []
    today = date.today()
    for row in rows:
        last_date = date.fromisoformat(row["NgayBaoDuongCuoi"])
        km = float(row["KmLamViec"])
        reduce_days = math.floor(km / 100)
        next_date = last_date + timedelta(days=max(0, 360 - reduce_days))
        status = "Quá hạn" if next_date < today else "Đúng hạn"
        result.append(
            {
                "MaXe": row["MaXe"],
                "BienSo": row["BienSo"],
                "NgayBaoDuongCuoi": row["NgayBaoDuongCuoi"],
                "KmLamViec": round(km, 1),
                "NgayBaoDuongTiep": next_date.isoformat(),
                "TrangThai": status,
            }
        )
    return result


def get_all_routes():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT t.MaTuyen, t.DiemDau, t.DiemCuoi, t.DoDai, t.DoPhucTap, hs.LuongPhuXe FROM Tuyen t JOIN HeSo hs ON t.DoPhucTap = hs.DoPhucTap ORDER BY t.MaTuyen"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_drivers():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM TaiXe ORDER BY HoTen").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_buses():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM Xe ORDER BY MaXe").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_trips(route_id=None, start_date=None, end_date=None, driver_id=None, bus_id=None):
    conn = get_db_connection()
    query = """
        SELECT c.MaChuyen, t.DiemDau, t.DiemCuoi, x.BienSo, lx.HoTen AS LaiXe, px.HoTen AS PhuXe, c.SoKhach, c.GiaVe, c.NgayKhoiHanh
        FROM Chuyen c
        JOIN Tuyen t ON c.MaTuyen = t.MaTuyen
        JOIN Xe x ON c.MaXe = x.MaXe
        JOIN TaiXe lx ON c.MaLaiXe = lx.MaTX
        JOIN TaiXe px ON c.MaPhuXe = px.MaTX
        WHERE 1 = 1
    """
    params = []

    if route_id:
        query += " AND c.MaTuyen = ?"
        params.append(int(route_id))
    if driver_id:
        query += " AND (c.MaLaiXe = ? OR c.MaPhuXe = ?)"
        params.extend([int(driver_id), int(driver_id)])
    if bus_id:
        query += " AND c.MaXe = ?"
        params.append(int(bus_id))
    if start_date:
        query += " AND date(c.NgayKhoiHanh) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date(c.NgayKhoiHanh) <= ?"
        params.append(end_date)

    query += " ORDER BY c.NgayKhoiHanh DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        route = request.form.get("route")
        if route == "bus":
            bien_so = request.form["bien_so"].strip()
            mau_xe = request.form["mau_xe"].strip()
            hang = request.form["hang_san_xuat"].strip()
            doi_xe = request.form["doi_xe"].strip()
            model = request.form["model"].strip()
            so_ghe = request.form["so_ghe"].strip()
            so_nam = request.form["so_nam_su_dung"].strip()
            ngay = request.form["ngay_bao_duong"].strip()
            if not bien_so:
                flash("Biển số không được để trống.")
            else:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO Xe (BienSo, MauXe, HangSanXuat, DoiXe, Model, SoGhe, SoNamSuDung, NgayBaoDuongCuoi) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (bien_so, mau_xe or None, hang or None, int(doi_xe) if doi_xe else None, model or None, int(so_ghe), int(so_nam) if so_nam else None, ngay or None),
                )
                conn.commit()
                conn.close()
                flash("Đã thêm xe mới.")
        elif route == "driver":
            ten = request.form["ten"].strip()
            cmt = request.form["cmt"].strip()
            bang_lai = request.form["bang_lai"].strip()
            loai = request.form["loai_bang_lai"].strip()
            dia_chi = request.form["dia_chi"].strip()
            ngay_sinh = request.form["ngay_sinh"].strip()
            tham_nien = request.form["tham_nien"].strip()
            if not ten or not cmt or not bang_lai:
                flash("Tên, CMT và mã bằng lái là bắt buộc.")
            else:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO TaiXe (HoTen, CMT, MaSoBangLai, LoaiBangLai, DiaChi, NgaySinh, ThamNien) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (ten, cmt, bang_lai, loai or None, dia_chi or None, ngay_sinh or None, int(tham_nien) if tham_nien else None),
                )
                conn.commit()
                conn.close()
                flash("Đã thêm tài xế mới.")
        elif route == "route":
            diem_dau = request.form["diem_dau"].strip()
            diem_cuoi = request.form["diem_cuoi"].strip()
            do_dai = request.form["do_dai"].strip()
            do_phuc_tap = request.form["do_phuc_tap"].strip()
            if not diem_dau or not diem_cuoi or not do_dai:
                flash("Điểm đầu, điểm cuối và độ dài là bắt buộc.")
            else:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO Tuyen (DiemDau, DiemCuoi, DoDai, DoPhucTap) VALUES (?, ?, ?, ?)",
                    (diem_dau, diem_cuoi, float(do_dai), int(do_phuc_tap)),
                )
                conn.commit()
                conn.close()
                flash("Đã thêm tuyến mới.")
        elif route == "trip":
            ma_tuyen = request.form["ma_tuyen"].strip()
            ma_xe = request.form["ma_xe"].strip()
            ma_lai_xe = request.form["ma_lai_xe"].strip()
            ma_phu_xe = request.form["ma_phu_xe"].strip()
            ngay = request.form["ngay_khoi_hanh"].strip()
            so_khach = request.form["so_khach"].strip()
            gia_ve = request.form["gia_ve"].strip()
            conn = get_db_connection()
            xe = conn.execute("SELECT SoGhe FROM Xe WHERE MaXe = ?", (int(ma_xe),)).fetchone()
            if not xe:
                flash("Xe không tồn tại.")
            elif int(ma_lai_xe) == int(ma_phu_xe):
                flash("Lái xe và phụ xe phải khác nhau.")
            elif int(so_khach) > int(xe["SoGhe"]) - 2:
                flash("Số khách vượt quá số chỗ ngồi cho phép (số ghế - 2).")
            else:
                conn.execute(
                    "INSERT INTO Chuyen (MaTuyen, MaXe, MaLaiXe, MaPhuXe, NgayKhoiHanh, SoKhach, GiaVe) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (int(ma_tuyen), int(ma_xe), int(ma_lai_xe), int(ma_phu_xe), ngay, int(so_khach), int(gia_ve)),
                )
                conn.commit()
                flash("Đã thêm chuyến xe mới.")
            conn.close()
        return redirect(url_for("index"))

    start_date = request.args.get("start_date") or "2026-10-01"
    end_date = request.args.get("end_date") or "2026-10-31"
    end_date_sql = (date.fromisoformat(end_date) + timedelta(days=1)).isoformat() if end_date else "2026-10-31"

    trip_route = request.args.get("trip_route") or ""
    trip_start = request.args.get("trip_start") or ""
    trip_end = request.args.get("trip_end") or ""
    trip_driver = request.args.get("trip_driver") or ""
    trip_bus = request.args.get("trip_bus") or ""
    payroll_month = request.args.get("payroll_month") or datetime.now().strftime("%Y-%m")

    counts = {
        "Xe": get_count("Xe"),
        "TaiXe": get_count("TaiXe"),
        "Tuyen": get_count("Tuyen"),
        "Chuyen": get_count("Chuyen"),
        "HeSo": get_count("HeSo"),
    }
    payroll = get_driver_payroll(payroll_month)
    revenue = get_vehicle_revenue(start_date, end_date_sql)
    maintenance = get_vehicle_maintenance()
    overdue = [item for item in maintenance if item["TrangThai"] == "Quá hạn"]
    routes = get_all_routes()
    drivers = get_all_drivers()
    buses = get_all_buses()
    trips = get_all_trips(
        route_id=int(trip_route) if trip_route else None,
        start_date=trip_start or None,
        end_date=trip_end or None,
        driver_id=int(trip_driver) if trip_driver else None,
        bus_id=int(trip_bus) if trip_bus else None,
    )
    total_revenue = sum(item["DoanhThu"] for item in revenue)
    total_passengers = sum(item["SoKhach"] for item in trips)
    trip_summary = {
        "count": len(trips),
        "passengers": total_passengers,
        "avg_passengers": round(total_passengers / len(trips), 1) if trips else 0,
        "revenue": sum(item["GiaVe"] * item["SoKhach"] for item in trips),
    }

    return render_template(
        "index.html",
        counts=counts,
        payroll=payroll,
        revenue=revenue,
        maintenance=maintenance,
        overdue=overdue,
        routes=routes,
        drivers=drivers,
        buses=buses,
        trips=trips,
        start_date=start_date,
        end_date=end_date,
        trip_route=trip_route,
        trip_start=trip_start,
        trip_end=trip_end,
        trip_driver=trip_driver,
        trip_bus=trip_bus,
        payroll_month=payroll_month,
        total_revenue=total_revenue,
        overdue_count=len(overdue),
        trip_summary=trip_summary,
        messages=get_flashed_messages(),
    )


init_db()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
