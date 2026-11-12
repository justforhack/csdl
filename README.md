## Hướng dẫn

`app.py` dùng SQLite, chạy cổng ở 5000; `app2.py` dùng MySQL (cần cài và khởi động MySQL Server trước khi chạy), chạy ở cổng 5001

## Cài đặt
```bash
pip install -r requirements.txt
```

## Cấu hình và chạy MySQL

Đặt thông tin kết nối MySQL trong biến môi trường (ví dụ macOS/Linux):

```bash
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD='mat_khau_mysql'
export MYSQL_DATABASE=HangVanTai
python app2.py
```

`MYSQL_DATABASE` mặc định là `HangVanTai`. Tài khoản MySQL cần quyền tạo database và bảng. Khi khởi động, app tự tạo database, cấu trúc bảng và dữ liệu mẫu nếu chưa có.
