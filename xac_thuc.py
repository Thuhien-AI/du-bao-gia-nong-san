# -*- coding: utf-8 -*-
"""
Đăng ký / đăng nhập cho ứng dụng.

LƯU TRỮ: file data/nguoi_dung.db (SQLite – cơ sở dữ liệu nằm gọn trong 1 file, có sẵn trong Python).
  - Bảng nguoi_dung : họ tên, email, mật khẩu ĐÃ MÃ HOÁ, ngày tạo.
  - Bảng phien      : "vé đăng nhập" để giữ đăng nhập 30 ngày khi tải lại trang.

BẢO MẬT MẬT KHẨU: không bao giờ lưu mật khẩu gốc. Mật khẩu được trộn với một chuỗi ngẫu nhiên
riêng cho từng người ("muối") rồi băm 200.000 lần bằng PBKDF2-SHA256 (chuẩn được khuyến nghị).
Khi đăng nhập, chương trình băm lại mật khẩu vừa nhập và so sánh kết quả.
"""

import hashlib
import hmac
import re
import secrets
import sqlite3

import csdl
from datetime import datetime, timedelta
from pathlib import Path

FILE_CSDL = Path(__file__).parent / "data" / "nguoi_dung.db"
SO_LAN_BAM = 200_000
SO_NGAY_GIU_DANG_NHAP = 30
MAU_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ================================================================ Cơ sở dữ liệu
def _ket_noi():
    kn = csdl.ket_noi(FILE_CSDL)      # Turso (trên mạng) nếu đã cấu hình, không thì file trên máy
    if csdl.mot_lan("xac_thuc"):           # tạo bảng chỉ 1 lần mỗi lần chạy web
        kn.execute("""CREATE TABLE IF NOT EXISTS nguoi_dung (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ho_ten TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        muoi TEXT NOT NULL,
                        mat_khau_bam TEXT NOT NULL,
                        ngay_tao TEXT NOT NULL,
                        lan_dang_nhap_cuoi TEXT)""")
        # cột hồ sơ cá nhân (thêm sau) -> tự bổ sung vào CSDL cũ nếu chưa có
        da_co = {r[1] for r in kn.execute("PRAGMA table_info(nguoi_dung)")}
        for cot, kieu in [("anh", "BLOB"), ("so_dien_thoai", "TEXT"), ("tinh", "TEXT"),
                          ("vai_tro", "TEXT"), ("cay_trong", "TEXT")]:
            if cot not in da_co:
                kn.execute(f"ALTER TABLE nguoi_dung ADD COLUMN {cot} {kieu}")
        kn.execute("""CREATE TABLE IF NOT EXISTS phien (
                        ve TEXT PRIMARY KEY,
                        nguoi_dung_id INTEGER NOT NULL,
                        het_han TEXT NOT NULL)""")
        kn.commit()
        csdl.da_lam("xac_thuc")
    return kn


def _bam(mat_khau: str, muoi: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", mat_khau.encode("utf-8"), bytes.fromhex(muoi),
                               SO_LAN_BAM).hex()


# ================================================================ Kiểm tra thông tin nhập
def kiem_tra_dang_ky(ho_ten: str, email: str, mat_khau: str, nhap_lai: str) -> list:
    """Trả về danh sách lỗi (rỗng = hợp lệ)."""
    loi = []
    if len(ho_ten.strip()) < 2:
        loi.append("Vui lòng nhập họ tên.")
    if not MAU_EMAIL.match(email.strip()):
        loi.append("Email chưa đúng định dạng (ví dụ: ten@gmail.com).")
    if len(mat_khau) < 8:
        loi.append("Mật khẩu cần ít nhất 8 ký tự.")
    elif not (re.search(r"[A-Za-z]", mat_khau) and re.search(r"\d", mat_khau)):
        loi.append("Mật khẩu cần có cả chữ và số.")
    if mat_khau != nhap_lai:
        loi.append("Hai lần nhập mật khẩu không giống nhau.")
    return loi


# ================================================================ Đăng ký / đăng nhập
def dang_ky(ho_ten: str, email: str, mat_khau: str, nhap_lai: str):
    """Trả về (True, thông báo) hoặc (False, [các lỗi])."""
    loi = kiem_tra_dang_ky(ho_ten, email, mat_khau, nhap_lai)
    if loi:
        return False, loi
    email = email.strip().lower()
    muoi = secrets.token_hex(16)
    with _ket_noi() as kn:
        if kn.execute("SELECT 1 FROM nguoi_dung WHERE email = ?", (email,)).fetchone():
            return False, ["Email này đã được đăng ký. Bạn hãy đăng nhập."]
        kn.execute("INSERT INTO nguoi_dung (ho_ten, email, muoi, mat_khau_bam, ngay_tao) "
                   "VALUES (?, ?, ?, ?, ?)",
                   (ho_ten.strip(), email, muoi, _bam(mat_khau, muoi),
                    datetime.now().isoformat(timespec="seconds")))
    return True, "Đăng ký thành công! Bạn hãy đăng nhập."


def dang_nhap(email: str, mat_khau: str):
    """Đúng -> thông tin người dùng (dict); sai -> None."""
    email = (email or "").strip().lower()
    with _ket_noi() as kn:
        nd = kn.execute("SELECT * FROM nguoi_dung WHERE email = ?", (email,)).fetchone()
        if nd is None:
            _bam(mat_khau or "", secrets.token_hex(16))   # tốn thời gian như nhau, khó dò email
            return None
        if not hmac.compare_digest(_bam(mat_khau or "", nd["muoi"]), nd["mat_khau_bam"]):
            return None
        kn.execute("UPDATE nguoi_dung SET lan_dang_nhap_cuoi = ? WHERE id = ?",
                   (datetime.now().isoformat(timespec="seconds"), nd["id"]))
    return {"id": nd["id"], "ho_ten": nd["ho_ten"], "email": nd["email"]}


# ================================================================ Giữ đăng nhập (vé)
def tao_ve(nguoi_dung_id: int) -> str:
    ve = secrets.token_urlsafe(32)
    het_han = datetime.now() + timedelta(days=SO_NGAY_GIU_DANG_NHAP)
    with _ket_noi() as kn:
        kn.execute("DELETE FROM phien WHERE het_han < ?", (datetime.now().isoformat(),))
        kn.execute("INSERT INTO phien (ve, nguoi_dung_id, het_han) VALUES (?, ?, ?)",
                   (ve, nguoi_dung_id, het_han.isoformat(timespec="seconds")))
    return ve


def nguoi_dung_tu_ve(ve: str):
    """Vé còn hạn -> thông tin người dùng; không thì None."""
    if not isinstance(ve, str) or not ve or len(ve) > 200:
        return None
    with _ket_noi() as kn:
        nd = kn.execute("""SELECT n.id, n.ho_ten, n.email FROM phien p
                           JOIN nguoi_dung n ON n.id = p.nguoi_dung_id
                           WHERE p.ve = ? AND p.het_han > ?""",
                        (ve, datetime.now().isoformat())).fetchone()
    return dict(nd) if nd else None


def xoa_ve(ve: str):
    if ve:
        with _ket_noi() as kn:
            kn.execute("DELETE FROM phien WHERE ve = ?", (ve,))


def so_nguoi_dung() -> int:
    with _ket_noi() as kn:
        return kn.execute("SELECT COUNT(*) FROM nguoi_dung").fetchone()[0]


# ================================================================ Hồ sơ cá nhân
MAU_SDT = re.compile(r"^(\+?84|0)\d{9,10}$")
VAI_TRO = ["Nông dân", "Thương lái / đại lý", "Hợp tác xã", "Doanh nghiệp", "Sinh viên / nghiên cứu", "Khác"]
CAY_TRONG = ["Lúa", "Cà phê", "Hồ tiêu", "Khác"]
CO_ANH = 256                       # ảnh đại diện lưu cỡ 256×256
DUNG_LUONG_ANH_TOI_DA = 5 * 1024 * 1024


def lay_ho_so(nguoi_dung_id: int) -> dict:
    with _ket_noi() as kn:
        r = kn.execute("SELECT id, ho_ten, email, ngay_tao, anh, so_dien_thoai, tinh, vai_tro, cay_trong "
                       "FROM nguoi_dung WHERE id = ?", (nguoi_dung_id,)).fetchone()
    if not r:
        return {}
    d = dict(r)
    d["cay_trong"] = [x for x in (d.get("cay_trong") or "").split(",") if x]
    return d


def cap_nhat_ho_so(nguoi_dung_id: int, ho_ten: str, so_dien_thoai: str, tinh: str, vai_tro: str, cay_trong: list):
    """Trả về (True, thông báo) hoặc (False, [lỗi])."""
    loi = []
    ho_ten, so_dien_thoai, tinh = (ho_ten or "").strip(), (so_dien_thoai or "").strip().replace(" ", ""), (tinh or "").strip()
    if len(ho_ten) < 2 or len(ho_ten) > 60:
        loi.append("Họ tên cần từ 2 đến 60 ký tự.")
    if so_dien_thoai and not MAU_SDT.match(so_dien_thoai):
        loi.append("Số điện thoại chưa đúng (ví dụ: 0912345678).")
    if len(tinh) > 60:
        loi.append("Tên tỉnh/thành quá dài.")
    if loi:
        return False, loi
    with _ket_noi() as kn:
        kn.execute("UPDATE nguoi_dung SET ho_ten=?, so_dien_thoai=?, tinh=?, vai_tro=?, cay_trong=? WHERE id=?",
                   (ho_ten, so_dien_thoai or None, tinh or None, vai_tro if vai_tro in VAI_TRO else None,
                    ",".join(c for c in cay_trong if c in CAY_TRONG) or None, nguoi_dung_id))
    return True, "Đã lưu thông tin cá nhân."


def luu_anh(nguoi_dung_id: int, du_lieu: bytes):
    """Kiểm tra file ảnh, cắt vuông giữa ảnh, thu về 256×256 rồi lưu. Trả về (True/False, thông báo)."""
    import io
    from PIL import Image, ImageOps
    if not du_lieu:
        return False, "Chưa chọn ảnh."
    if len(du_lieu) > DUNG_LUONG_ANH_TOI_DA:
        return False, "Ảnh lớn quá 5 MB, hãy chọn ảnh nhỏ hơn."
    try:
        anh = Image.open(io.BytesIO(du_lieu))
        anh.verify()                                  # kiểm tra đúng là file ảnh
        anh = Image.open(io.BytesIO(du_lieu))
        anh = ImageOps.exif_transpose(anh)            # ảnh chụp điện thoại: xoay đúng chiều
        anh = ImageOps.fit(anh.convert("RGB"), (CO_ANH, CO_ANH), Image.LANCZOS)
    except Exception:
        return False, "File này không phải ảnh hợp lệ (dùng JPG, PNG hoặc WEBP)."
    bo_dem = io.BytesIO()
    anh.save(bo_dem, format="JPEG", quality=88)
    with _ket_noi() as kn:
        kn.execute("UPDATE nguoi_dung SET anh=? WHERE id=?", (bo_dem.getvalue(), nguoi_dung_id))
    return True, "Đã đổi ảnh đại diện."


def xoa_anh(nguoi_dung_id: int):
    with _ket_noi() as kn:
        kn.execute("UPDATE nguoi_dung SET anh=NULL WHERE id=?", (nguoi_dung_id,))


def doi_email(nguoi_dung_id: int, email_moi: str, mat_khau: str):
    email_moi = (email_moi or "").strip().lower()
    if not MAU_EMAIL.match(email_moi):
        return False, "Email chưa đúng định dạng (ví dụ: ten@gmail.com)."
    with _ket_noi() as kn:
        nd = kn.execute("SELECT * FROM nguoi_dung WHERE id=?", (nguoi_dung_id,)).fetchone()
        if not nd or not hmac.compare_digest(_bam(mat_khau or "", nd["muoi"]), nd["mat_khau_bam"]):
            return False, "Mật khẩu hiện tại chưa đúng."
        if email_moi == nd["email"]:
            return False, "Đây đã là email của bạn."
        if kn.execute("SELECT 1 FROM nguoi_dung WHERE email=?", (email_moi,)).fetchone():
            return False, "Email này đã có tài khoản khác dùng."
        kn.execute("UPDATE nguoi_dung SET email=? WHERE id=?", (email_moi, nguoi_dung_id))
    return True, f"Đã đổi email đăng nhập thành {email_moi}."


def doi_mat_khau(nguoi_dung_id: int, mat_khau_cu: str, mat_khau_moi: str, nhap_lai: str, ve_giu_lai: str = None):
    """Đổi mật khẩu; các thiết bị khác đang đăng nhập sẽ bị đăng xuất (trừ phiên hiện tại)."""
    with _ket_noi() as kn:
        nd = kn.execute("SELECT * FROM nguoi_dung WHERE id=?", (nguoi_dung_id,)).fetchone()
        if not nd or not hmac.compare_digest(_bam(mat_khau_cu or "", nd["muoi"]), nd["mat_khau_bam"]):
            return False, ["Mật khẩu hiện tại chưa đúng."]
        loi = [x for x in kiem_tra_dang_ky(nd["ho_ten"], nd["email"], mat_khau_moi or "", nhap_lai or "")]
        if mat_khau_moi == mat_khau_cu:
            loi.append("Mật khẩu mới phải khác mật khẩu cũ.")
        if loi:
            return False, loi
        muoi = secrets.token_hex(16)
        kn.execute("UPDATE nguoi_dung SET muoi=?, mat_khau_bam=? WHERE id=?",
                   (muoi, _bam(mat_khau_moi, muoi), nguoi_dung_id))
        kn.execute("DELETE FROM phien WHERE nguoi_dung_id=? AND ve != ?", (nguoi_dung_id, ve_giu_lai or ""))
    return True, ["Đã đổi mật khẩu. Các thiết bị khác đã được đăng xuất."]


# ================================================================ Tài khoản quản trị diễn đàn
# Đăng nhập bằng tên "admin". Chỉ lưu mật khẩu ĐÃ BĂM (muối cố định bên dưới), không lưu mật khẩu gốc.
# Nên đổi mật khẩu này trong Trang cá nhân trước khi đưa web lên mạng.
EMAIL_QUAN_TRI = "admin"
_MUOI_QT = "6f1c2b9e8a4d7035c1e2f9a8b7d6c5e4"
_BAM_QT = "9b5d15b7602fa7c08e73e3707d6a0948aac43619dcc64a79da026b0cdc52f2de"


def dam_bao_quan_tri():
    """Tạo tài khoản 'admin' nếu chưa có (chạy mỗi lần mở web, rất nhẹ)."""
    with _ket_noi() as kn:
        if not kn.execute("SELECT 1 FROM nguoi_dung WHERE email = ?", (EMAIL_QUAN_TRI,)).fetchone():
            kn.execute("INSERT INTO nguoi_dung (ho_ten, email, muoi, mat_khau_bam, ngay_tao) VALUES (?, ?, ?, ?, ?)",
                       ("Quản trị Bồ Nông", EMAIL_QUAN_TRI, _MUOI_QT, _BAM_QT,
                        datetime.now().isoformat(timespec="seconds")))


def la_quan_tri(nguoi_dung_id: int) -> bool:
    with _ket_noi() as kn:
        r = kn.execute("SELECT email FROM nguoi_dung WHERE id = ?", (nguoi_dung_id,)).fetchone()
    return bool(r) and r["email"] == EMAIL_QUAN_TRI
