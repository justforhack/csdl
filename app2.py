import math
import os
import re
from datetime import date, datetime, timedelta

from flask import Flask, flash, get_flashed_messages, redirect, render_template, request, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = "hang-van-tai-key"
DB_NAME = os.environ.get("MYSQL_DATABASE", "HangVanTai")
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "charset": "utf8mb4",
}


class DatabaseConnection:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=()):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params)
        return cursor

    def executemany(self, query, params):
        cursor = self.connection.cursor()
        cursor.executemany(query, params)
        return cursor

    def execute_script(self, script):
        cursor = self.connection.cursor()
        for statement in script.split(";"):
            if statement.strip():
                cursor.execute(statement)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


def get_db_connection():
    return DatabaseConnection(mysql.connector.connect(database=DB_NAME, **DB_CONFIG))


def init_db():
    if not re.fullmatch(r"[A-Za-z0-9_]+", DB_NAME):
        raise ValueError("MYSQL_DATABASE chỉ được chứa chữ, số và dấu gạch dưới.")
    server = mysql.connector.connect(**DB_CONFIG)
    server.cursor().execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4")
    server.close()

    conn = get_db_connection()
    conn.execute_script(
        """
        CREATE TABLE IF NOT EXISTS HeSo (
            DoPhucTap INT PRIMARY KEY,
            LuongPhuXe INT NOT NULL,
            HeSoKm DOUBLE NOT NULL
        )
        """
    )
    conn.execute_script(
        """

        CREATE TABLE IF NOT EXISTS Xe (
            MaXe INT PRIMARY KEY AUTO_INCREMENT,
            BienSo VARCHAR(15) NOT NULL UNIQUE,
            MauXe VARCHAR(30),
            HangSanXuat VARCHAR(50),
            DoiXe INT,
            Model VARCHAR(50),
            SoGhe INT NOT NULL,
            SoNamSuDung INT,
            NgayBaoDuongCuoi DATE
        )
        """
    )
    conn.execute_script(
        """

        CREATE TABLE IF NOT EXISTS TaiXe (
            MaTX INT PRIMARY KEY AUTO_INCREMENT,
            HoTen VARCHAR(100) NOT NULL,
            CMT VARCHAR(12) NOT NULL UNIQUE,
            MaSoBangLai VARCHAR(20) NOT NULL UNIQUE,
            LoaiBangLai VARCHAR(5),
            DiaChi VARCHAR(200),
            NgaySinh DATE,
            ThamNien INT
        )
        """
    )
    conn.execute_script(
        """

        CREATE TABLE IF NOT EXISTS Tuyen (
            MaTuyen INT PRIMARY KEY AUTO_INCREMENT,
            DiemDau VARCHAR(100) NOT NULL,
            DiemCuoi VARCHAR(100) NOT NULL,
            DoDai DOUBLE NOT NULL,
            DoPhucTap INT NOT NULL,
            FOREIGN KEY (DoPhucTap) REFERENCES HeSo(DoPhucTap)
        )
        """
    )
    conn.execute_script(
        """

        CREATE TABLE IF NOT EXISTS Chuyen (
            MaChuyen INT PRIMARY KEY AUTO_INCREMENT,
            MaTuyen INT NOT NULL,
            MaXe INT NOT NULL,
            MaLaiXe INT NOT NULL,
            MaPhuXe INT NOT NULL,
            NgayKhoiHanh DATETIME NOT NULL,
            SoKhach INT NOT NULL,
            GiaVe INT NOT NULL,
            FOREIGN KEY (MaTuyen) REFERENCES Tuyen(MaTuyen),
            FOREIGN KEY (MaXe) REFERENCES Xe(MaXe),
            FOREIGN KEY (MaLaiXe) REFERENCES TaiXe(MaTX),
            FOREIGN KEY (MaPhuXe) REFERENCES TaiXe(MaTX)
        )
        """
    )

    conn.executemany(
        "INSERT IGNORE INTO HeSo (DoPhucTap, LuongPhuXe, HeSoKm) VALUES (%s, %s, %s)",
        [(1, 200000, 1.0), (2, 260000, 1.5), (3, 340000, 2.0)],
    )

    conn.executemany(
        "INSERT IGNORE INTO Xe (MaXe, BienSo, MauXe, HangSanXuat, DoiXe, Model, SoGhe, SoNamSuDung, NgayBaoDuongCuoi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        [
            (1, "29B-123.45", "Trắng", "Hyundai", 2020, "Universe", 45, 6, "2026-08-10"),
            (2, "29B-234.56", "Xanh", "Thaco", 2019, "Garden", 40, 7, "2026-05-20"),
            (3, "30F-345.67", "Đỏ", "Samco", 2021, "Felix", 29, 5, "2026-09-15"),
            (4, "30F-456.78", "Trắng", "Hyundai", 2018, "County", 29, 8, "2025-09-01"),
            (5, "29B-567.89", "Vàng", "Thaco", 2022, "TB120S", 47, 4, "2026-07-01"),
            (6, "15B-678.90", "Bạc", "Isuzu", 2017, "Samco", 34, 9, "2025-10-10"),
        ],
    )

    conn.executemany(
        "INSERT IGNORE INTO TaiXe (MaTX, HoTen, CMT, MaSoBangLai, LoaiBangLai, DiaChi, NgaySinh, ThamNien) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        [
            (1, "Nguyễn Văn An", "001085012345", "010085001234", "E", "Hà Nội", "1985-04-12", 16),
            (2, "Trần Văn Bình", "001088023456", "010088002345", "FC", "Hà Nội", "1988-09-23", 14),
            (3, "Lê Minh Cường", "034090034567", "034090003456", "E", "Thái Bình", "1990-01-05", 12),
            (4, "Phạm Quốc Dũng", "001092045678", "010092004567", "D", "Hà Nội", "1992-11-30", 9),
            (5, "Hoàng Văn Em", "038086056789", "038086005678", "FC", "Thanh Hóa", "1986-07-19", 17),
            (6, "Vũ Thành Phong", "001095067890", "010095006789", "D", "Hà Nội", "1995-02-14", 7),
            (7, "Đặng Hữu Giang", "030087078901", "030087007890", "E", "Hải Dương", "1987-12-02", 15),
            (8, "Bùi Đức Hải", "001091089012", "010091008901", "D", "Hà Nội", "1991-06-28", 10),
        ],
    )

    conn.executemany(
        "INSERT IGNORE INTO Tuyen (MaTuyen, DiemDau, DiemCuoi, DoDai, DoPhucTap) VALUES (%s, %s, %s, %s, %s)",
        [
            (1, "Hà Nội", "Hải Phòng", 120, 1),
            (2, "Hà Nội", "Vinh", 300, 2),
            (3, "Hà Nội", "Sa Pa", 320, 3),
            (4, "Hà Nội", "Đà Nẵng", 770, 2),
            (5, "Hà Nội", "Điện Biên", 470, 3),
            (6, "Hà Nội", "Lạng Sơn", 155, 1),
        ],
    )

    conn.executemany(
        "INSERT IGNORE INTO Chuyen (MaChuyen, MaTuyen, MaXe, MaLaiXe, MaPhuXe, NgayKhoiHanh, SoKhach, GiaVe) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        [
            (1, 1, 1, 1, 2, "2026-10-02 06:00:00", 40, 120000),
            (2, 2, 2, 3, 4, "2026-10-03 07:00:00", 35, 250000),
            (3, 3, 3, 5, 6, "2026-10-05 20:00:00", 25, 280000),
            (4, 4, 5, 7, 8, "2026-10-06 18:00:00", 44, 450000),
            (5, 6, 1, 2, 1, "2026-10-08 06:30:00", 42, 100000),
            (6, 1, 4, 4, 3, "2026-10-09 09:00:00", 22, 120000),
            (7, 5, 6, 6, 5, "2026-10-10 17:00:00", 30, 380000),
            (8, 2, 1, 1, 3, "2026-10-12 07:00:00", 43, 250000),
            (9, 3, 2, 3, 7, "2026-10-14 21:00:00", 37, 280000),
            (10, 4, 5, 8, 7, "2026-10-15 18:00:00", 45, 450000),
            (11, 6, 3, 5, 2, "2026-10-16 08:00:00", 27, 100000),
            (12, 1, 6, 6, 8, "2026-10-17 06:00:00", 32, 120000),
            (13, 5, 4, 4, 6, "2026-10-18 16:00:00", 20, 380000),
            (14, 2, 1, 1, 2, "2026-10-19 05:30:00", 38, 250000),
            (15, 1, 2, 3, 4, "2026-09-20 06:00:00", 38, 120000),
            (16, 4, 5, 7, 8, "2026-09-25 18:00:00", 40, 450000),
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
                         AND c.NgayKhoiHanh >= %s
                         AND c.NgayKhoiHanh <= %s), 0)
               + IFNULL((SELECT SUM(hs.LuongPhuXe)
                         FROM Chuyen c
                         JOIN Tuyen tu ON c.MaTuyen = tu.MaTuyen
                         JOIN HeSo hs ON tu.DoPhucTap = hs.DoPhucTap
                         WHERE c.MaPhuXe = tx.MaTX
                           AND c.NgayKhoiHanh >= %s
                           AND c.NgayKhoiHanh <= %s), 0) AS Luong
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
            AND c.NgayKhoiHanh >= %s
            AND c.NgayKhoiHanh < %s
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
            AND c.NgayKhoiHanh <= NOW()
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
        last_date = row["NgayBaoDuongCuoi"]
        if isinstance(last_date, datetime):
            last_date = last_date.date()
        elif isinstance(last_date, str):
            last_date = date.fromisoformat(last_date)
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
        query += " AND c.MaTuyen = %s"
        params.append(int(route_id))
    if driver_id:
        query += " AND (c.MaLaiXe = %s OR c.MaPhuXe = %s)"
        params.extend([int(driver_id), int(driver_id)])
    if bus_id:
        query += " AND c.MaXe = %s"
        params.append(int(bus_id))
    if start_date:
        query += " AND DATE(c.NgayKhoiHanh) >= %s"
        params.append(start_date)
    if end_date:
        query += " AND DATE(c.NgayKhoiHanh) <= %s"
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
                    "INSERT INTO Xe (BienSo, MauXe, HangSanXuat, DoiXe, Model, SoGhe, SoNamSuDung, NgayBaoDuongCuoi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
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
                    "INSERT INTO TaiXe (HoTen, CMT, MaSoBangLai, LoaiBangLai, DiaChi, NgaySinh, ThamNien) VALUES (%s, %s, %s, %s, %s, %s, %s)",
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
                    "INSERT INTO Tuyen (DiemDau, DiemCuoi, DoDai, DoPhucTap) VALUES (%s, %s, %s, %s)",
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
            xe = conn.execute("SELECT SoGhe FROM Xe WHERE MaXe = %s", (int(ma_xe),)).fetchone()
            if not xe:
                flash("Xe không tồn tại.")
            elif int(ma_lai_xe) == int(ma_phu_xe):
                flash("Lái xe và phụ xe phải khác nhau.")
            elif int(so_khach) > int(xe["SoGhe"]) - 2:
                flash("Số khách vượt quá số chỗ ngồi cho phép (số ghế - 2).")
            else:
                conn.execute(
                    "INSERT INTO Chuyen (MaTuyen, MaXe, MaLaiXe, MaPhuXe, NgayKhoiHanh, SoKhach, GiaVe) VALUES (%s, %s, %s, %s, %s, %s, %s)",
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
    app.run(debug=True, host="0.0.0.0", port=5001)
