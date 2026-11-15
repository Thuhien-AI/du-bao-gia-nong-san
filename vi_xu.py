# -*- coding: utf-8 -*-
"""
Ví xu & gói VIP của Bồ Nông (giai đoạn 1 — CHẾ ĐỘ THỬ, chưa thu tiền thật).

Ý TƯỞNG CHÍNH
  - Xu KHÔNG bán bằng tiền. Xu chỉ được TẶNG (đăng ký, điểm danh, xu tặng hằng tháng của VIP).
  - Xu tặng hết hạn sau 30 ngày. Khi tiêu, xu sắp hết hạn được dùng trước.
  - Xu dùng để mở khoá có thời hạn: dự báo 7/30 ngày (30 xu / 7 ngày), lịch sử giá dài
    (50 xu / 30 ngày), tải bảng dự báo Excel (20 xu / lần, dùng trong 24 giờ).
  - Tiền chỉ dùng để mua VIP: Mùa Vàng, Bội Thu, Đại Điền, Nhóm (5 tài khoản).
  - VIP cũng đổi được bằng xu: 500 xu = Mùa Vàng (30 ngày), 1.300 xu = Bội Thu (3 tháng).

LƯU TRỮ (cùng file data/nguoi_dung.db với tài khoản):
  - giao_dich_xu   : SỔ CÁI — mọi lần cộng/trừ xu. Chỉ thêm dòng, không sửa, không xoá.
  - lo_xu          : từng "lô" xu được tặng, còn lại bao nhiêu, hết hạn khi nào.
  - mo_khoa        : ai đang được xem gì, đến khi nào.
  - goi_vip        : các kỳ VIP (mua, đổi xu, dùng thử).
  - thanh_vien_nhom: email các thành viên của gói VIP Nhóm.
  - don_thanh_toan : đơn mua VIP (chế độ thử: bấm "Giả lập đã thanh toán").
"""

import math
import secrets
import sqlite3
from datetime import datetime, timedelta

import csdl
import xac_thuc as xt

# ================================================================ Bảng giá (sửa ở đây là đổi toàn app)
DONG_MOI_XU = 100                 # 1 xu tương đương 100 đồng (để ghi giá cho dễ hiểu)
HAN_XU_TANG = 30                  # xu tặng dùng được 30 ngày
XU_DANG_KY = 50
XU_DIEM_DANH, XU_DIEM_DANH_NGAY_7, TRAN_DIEM_DANH_THANG = 2, 10, 60
CHE_DO_THU = True                 # True = chưa thu tiền thật, có nút "Giả lập đã thanh toán"
PHUT_GIU_DON = 15

# tính năng mở bằng xu: (số xu, số ngày dùng được, tên hiển thị)
GIA_MO_KHOA = {
    "du_bao": (30, 7, "Dự báo 7 ngày"),
    "du_bao_30": (50, 7, "Dự báo 7 & 30 ngày"),
    "lich_su": (50, 30, "Biểu đồ lịch sử giá dài ngày"),
    "excel": (20, 1, "Tải bảng dự báo (Excel)"),      # không còn bán (đã gộp vào Xuất báo cáo); giữ để đọc lịch sử cũ
}

# HẠNG GÓI: 0 Miễn phí · 1 Mùa Vàng · 2 Bội Thu · 3 Đại Điền (Nhóm = Đại Điền)
HANG_GOI = {"mua_vang": 1, "boi_thu": 2, "dai_dien": 3, "nhom": 3}
TEN_HANG = {0: "Miễn phí", 1: "VIP Mùa Vàng", 2: "VIP Bội Thu", 3: "VIP Đại Điền"}
# hạng tối thiểu để dùng từng tính năng
HANG_TOI_THIEU = {
    "du_bao_7": 1, "du_bao_30": 2,
    "thong_bao": 1, "ai": 2, "canh_bao": 2, "bao_cao": 3,
    "lich_su": 1, "the_gioi": 1,
}
# tính năng nào mở được bằng lần mở khoá xu nào
MO_BANG_XU = {"du_bao_7": ("du_bao", "du_bao_30"),
              "du_bao_30": ("du_bao_30",), "lich_su": ("lich_su",)}
SO_CANH_BAO_TOI_DA = 10

# gói VIP: tên, số ngày, giá (đồng), xu tặng mỗi 30 ngày, số tài khoản
GOI_VIP = {
    "mua_vang": {"ten": "VIP Mùa Vàng", "ky": "30 ngày", "so_ngay": 30, "gia": 49_000, "xu_thang": 100, "so_tk": 1},
    "boi_thu": {"ten": "VIP Bội Thu", "ky": "3 tháng", "so_ngay": 90, "gia": 129_000, "xu_thang": 150, "so_tk": 1},
    "dai_dien": {"ten": "VIP Đại Điền", "ky": "12 tháng", "so_ngay": 365, "gia": 449_000, "xu_thang": 200, "so_tk": 1},
    "nhom": {"ten": "VIP Nhóm", "ky": "12 tháng · 5 tài khoản", "so_ngay": 365, "gia": 1_688_000, "xu_thang": 200, "so_tk": 5},
}
DOI_XU_LAY_VIP = {"mua_vang": 500, "boi_thu": 1300}   # gói -> số xu cần
SO_NGAY_DUNG_THU = 7
NGUONG_GOI_Y_VIP = 400            # chi trên 400 xu trong 30 ngày -> gợi ý lên VIP


def _bay_gio() -> datetime:
    return datetime.now().replace(microsecond=0)


def _iso(t: datetime) -> str:
    return t.isoformat(timespec="seconds")


def tien(so_dong: int) -> str:
    return f"{so_dong:,.0f} đ".replace(",", ".")


# ================================================================ Cơ sở dữ liệu
def _ket_noi():
    kn = xt._ket_noi()          # mở cùng file nguoi_dung.db, bảo đảm bảng tài khoản đã có
    if csdl.mot_lan("vi_xu"):
        kn.executescript("""
        CREATE TABLE IF NOT EXISTS giao_dich_xu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nguoi_dung_id INTEGER NOT NULL,
            so_xu INTEGER NOT NULL,
            loai TEXT NOT NULL,              -- tang | chi | hoan | het_han
            ly_do TEXT NOT NULL,
            ma TEXT UNIQUE,                  -- chống cộng 2 lần (vd. diem_danh:7:2026-11-14)
            tao_luc TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS lo_xu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nguoi_dung_id INTEGER NOT NULL,
            so_xu_goc INTEGER NOT NULL,
            con_lai INTEGER NOT NULL,
            het_han_luc TEXT NOT NULL,
            tao_luc TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS mo_khoa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nguoi_dung_id INTEGER NOT NULL,
            tinh_nang TEXT NOT NULL,
            khoa TEXT NOT NULL,              -- vd. "Lúa|Lúa tươi IR 50404|An Giang"
            so_xu INTEGER NOT NULL,
            bat_dau TEXT NOT NULL,
            het_han_luc TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS goi_vip (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nguoi_dung_id INTEGER NOT NULL,
            loai_goi TEXT NOT NULL,
            bat_dau TEXT NOT NULL,
            ket_thuc TEXT NOT NULL,
            tu_gia_han INTEGER NOT NULL DEFAULT 0,
            nguon TEXT NOT NULL,             -- tien | xu | dung_thu
            xu_thang INTEGER NOT NULL DEFAULT 0,
            tao_luc TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS thanh_vien_nhom (
            goi_vip_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            them_luc TEXT NOT NULL,
            PRIMARY KEY (goi_vip_id, email));
        CREATE TABLE IF NOT EXISTS canh_bao_gia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nguoi_dung_id INTEGER NOT NULL,
            nong_san TEXT NOT NULL, loai TEXT NOT NULL, khu_vuc TEXT NOT NULL,
            kieu TEXT NOT NULL,              -- tren (giá >= ngưỡng) | duoi (giá <= ngưỡng)
            nguong REAL NOT NULL,
            tao_luc TEXT NOT NULL,
            lan_bao_cuoi TEXT);              -- ngày giá đã báo gần nhất (mỗi phiên giá chỉ báo 1 lần)
        CREATE TABLE IF NOT EXISTS luot_hoi_ai (
            nguoi_dung_id INTEGER NOT NULL,
            ngay TEXT NOT NULL,
            so_luot INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (nguoi_dung_id, ngay));
        CREATE TABLE IF NOT EXISTS don_thanh_toan (
            ma_don TEXT PRIMARY KEY,
            nguoi_dung_id INTEGER NOT NULL,
            san_pham TEXT NOT NULL,
            so_tien INTEGER NOT NULL,
            cong TEXT NOT NULL,
            trang_thai TEXT NOT NULL,        -- cho | thanh_cong | het_han | huy
            ma_giao_dich_cong TEXT UNIQUE,
            tao_luc TEXT NOT NULL,
            het_han_luc TEXT NOT NULL,
            xong_luc TEXT);
        """)
        kn.commit()
        csdl.da_lam("vi_xu")
    return kn


# ================================================================ Xu: cộng, trừ, số dư
def _cong(kn, nd_id: int, so_xu: int, loai: str, ly_do: str, ma: str = None, han_ngay: int = HAN_XU_TANG) -> bool:
    """Cộng xu (tạo 1 lô mới). Có 'ma' thì mỗi mã chỉ cộng được 1 lần. Trả về True nếu đã cộng."""
    if so_xu <= 0:
        return False
    t = _bay_gio()
    try:
        kn.execute("INSERT INTO giao_dich_xu (nguoi_dung_id, so_xu, loai, ly_do, ma, tao_luc) VALUES (?,?,?,?,?,?)",
                   (nd_id, so_xu, loai, ly_do, ma, _iso(t)))
    except sqlite3.IntegrityError:          # mã này đã cộng rồi
        return False
    kn.execute("INSERT INTO lo_xu (nguoi_dung_id, so_xu_goc, con_lai, het_han_luc, tao_luc) VALUES (?,?,?,?,?)",
               (nd_id, so_xu, so_xu, _iso(t + timedelta(days=han_ngay)), _iso(t)))
    return True


def _so_du(kn, nd_id: int) -> int:
    return kn.execute("SELECT COALESCE(SUM(con_lai),0) FROM lo_xu WHERE nguoi_dung_id=? AND het_han_luc>?",
                      (nd_id, _iso(_bay_gio()))).fetchone()[0]


def _chi(kn, nd_id: int, so_xu: int, ly_do: str) -> bool:
    """Trừ xu, dùng lô sắp hết hạn trước. Phải gọi trong giao dịch BEGIN IMMEDIATE."""
    if _so_du(kn, nd_id) < so_xu:
        return False
    can = so_xu
    for lo in kn.execute("SELECT id, con_lai FROM lo_xu WHERE nguoi_dung_id=? AND con_lai>0 AND het_han_luc>? "
                         "ORDER BY het_han_luc", (nd_id, _iso(_bay_gio()))).fetchall():
        lay = min(can, lo["con_lai"])
        kn.execute("UPDATE lo_xu SET con_lai=con_lai-? WHERE id=?", (lay, lo["id"]))
        can -= lay
        if can == 0:
            break
    kn.execute("INSERT INTO giao_dich_xu (nguoi_dung_id, so_xu, loai, ly_do, tao_luc) VALUES (?,?,?,?,?)",
               (nd_id, -so_xu, "chi", ly_do, _iso(_bay_gio())))
    return True


class _GiaoDich:
    """Khoá CSDL trong lúc trừ xu: bấm 2 lần liền không bị trừ 2 lần, không bao giờ âm xu."""

    def __enter__(self):
        self.kn = _ket_noi()
        self.kn.isolation_level = None
        self.kn.execute("BEGIN IMMEDIATE")
        return self.kn

    def __exit__(self, loai_loi, *_):
        self.kn.execute("ROLLBACK" if loai_loi else "COMMIT")
        self.kn.close()


def so_du(nd_id: int) -> int:
    with _ket_noi() as kn:
        return _so_du(kn, nd_id)


def xu_sap_het_han(nd_id: int, so_ngay: int = 7):
    """(số xu, ngày hết hạn sớm nhất) của các lô sẽ hết hạn trong vài ngày tới."""
    t = _bay_gio()
    with _ket_noi() as kn:
        r = kn.execute("SELECT COALESCE(SUM(con_lai),0), MIN(het_han_luc) FROM lo_xu WHERE nguoi_dung_id=? "
                       "AND con_lai>0 AND het_han_luc>? AND het_han_luc<=?",
                       (nd_id, _iso(t), _iso(t + timedelta(days=so_ngay)))).fetchone()
    return r[0], (datetime.fromisoformat(r[1]) if r[1] else None)


def xu_da_chi(nd_id: int, so_ngay: int = 30) -> int:
    with _ket_noi() as kn:
        return -kn.execute("SELECT COALESCE(SUM(so_xu),0) FROM giao_dich_xu WHERE nguoi_dung_id=? AND loai='chi' "
                           "AND tao_luc>?", (nd_id, _iso(_bay_gio() - timedelta(days=so_ngay)))).fetchone()[0]


def lich_su(nd_id: int, loc: str = None, gioi_han: int = 300) -> list:
    """Lịch sử xu + đơn thanh toán, mới nhất trước. loc: None | 'tang' | 'chi' | 'don'."""
    with _ket_noi() as kn:
        dong = []
        if loc in (None, "tang", "chi"):
            dk = {"tang": "AND loai IN ('tang','hoan')", "chi": "AND loai IN ('chi','het_han')"}.get(loc, "")
            for r in kn.execute(f"SELECT * FROM giao_dich_xu WHERE nguoi_dung_id=? {dk} ORDER BY id DESC LIMIT ?",
                                (nd_id, gioi_han)):
                dong.append({"luc": r["tao_luc"], "noi_dung": r["ly_do"], "xu": r["so_xu"], "tien": None,
                             "trang_thai": {"tang": "Được tặng", "hoan": "Hoàn xu", "chi": "Đã dùng",
                                            "het_han": "Hết hạn"}.get(r["loai"], r["loai"])})
        if loc in (None, "don"):
            for r in kn.execute("SELECT * FROM don_thanh_toan WHERE nguoi_dung_id=? ORDER BY tao_luc DESC LIMIT ?",
                                (nd_id, gioi_han)):
                dong.append({"luc": r["tao_luc"], "noi_dung": f"Mua {GOI_VIP[r['san_pham']]['ten']} · đơn {r['ma_don']}",
                             "xu": None, "tien": r["so_tien"],
                             "trang_thai": {"cho": "Chờ thanh toán", "thanh_cong": "Thành công",
                                            "het_han": "Hết hạn", "huy": "Đã huỷ"}[r["trang_thai"]]})
    return sorted(dong, key=lambda d: d["luc"], reverse=True)


# ================================================================ Đồng bộ mỗi lần mở trang
def dong_bo(nd_id: int):
    """
    Gọi mỗi khi người dùng mở trang:
      - tặng 50 xu chào mừng (cả tài khoản tạo trước khi có ví xu),
      - ghi sổ những lô xu vừa hết hạn,
      - cộng xu tặng hằng tháng của VIP,
      - đánh dấu các đơn thanh toán quá 15 phút là hết hạn.
    """
    t = _bay_gio()
    with _GiaoDich() as kn:
        _cong(kn, nd_id, XU_DANG_KY, "tang", "Quà tạo tài khoản", ma=f"dang_ky:{nd_id}")
        for lo in kn.execute("SELECT id, con_lai FROM lo_xu WHERE nguoi_dung_id=? AND con_lai>0 AND het_han_luc<=?",
                             (nd_id, _iso(t))).fetchall():
            kn.execute("UPDATE lo_xu SET con_lai=0 WHERE id=?", (lo["id"],))
            kn.execute("INSERT INTO giao_dich_xu (nguoi_dung_id, so_xu, loai, ly_do, tao_luc) VALUES (?,?,?,?,?)",
                       (nd_id, -lo["con_lai"], "het_han", "Xu tặng hết hạn sau 30 ngày", _iso(t)))
        for g in _cac_goi_dang_huong(kn, nd_id):
            if g["xu_thang"] <= 0:
                continue
            bat_dau = datetime.fromisoformat(g["bat_dau"])
            so_ky = int((t - bat_dau).total_seconds() // (30 * 86400))
            for k in range(so_ky + 1):
                if bat_dau + timedelta(days=30 * k) < datetime.fromisoformat(g["ket_thuc"]):
                    _cong(kn, nd_id, g["xu_thang"], "tang", f"Xu tặng tháng {k + 1} · {GOI_VIP[g['loai_goi']]['ten']}",
                          ma=f"vip_tang:{g['id']}:{k}:{nd_id}")
        kn.execute("UPDATE don_thanh_toan SET trang_thai='het_han' WHERE nguoi_dung_id=? AND trang_thai='cho' "
                   "AND het_han_luc<=?", (nd_id, _iso(t)))


def diem_danh(nd_id: int):
    """Điểm danh hằng ngày: 2 xu, ngày thứ 7 liên tiếp 10 xu, tối đa 60 xu/tháng. Trả về (số xu, thông báo)."""
    hom_nay = _bay_gio().date()
    with _GiaoDich() as kn:
        if kn.execute("SELECT 1 FROM giao_dich_xu WHERE ma=?", (f"diem_danh:{nd_id}:{hom_nay}",)).fetchone():
            return 0, "Hôm nay bạn đã điểm danh rồi. Mai quay lại nhé!"
        chuoi = 1
        while kn.execute("SELECT 1 FROM giao_dich_xu WHERE ma=?",
                         (f"diem_danh:{nd_id}:{hom_nay - timedelta(days=chuoi)}",)).fetchone():
            chuoi += 1
        da_nhan = kn.execute("SELECT COALESCE(SUM(so_xu),0) FROM giao_dich_xu WHERE nguoi_dung_id=? "
                             "AND ma LIKE ?", (nd_id, f"diem_danh:{nd_id}:{hom_nay:%Y-%m}-%")).fetchone()[0]
        so = min(XU_DIEM_DANH_NGAY_7 if chuoi % 7 == 0 else XU_DIEM_DANH, TRAN_DIEM_DANH_THANG - da_nhan)
        if so <= 0:
            return 0, f"Tháng này bạn đã nhận đủ {TRAN_DIEM_DANH_THANG} xu điểm danh."
        _cong(kn, nd_id, so, "tang", f"Điểm danh ngày {hom_nay:%d/%m} (chuỗi {chuoi} ngày)",
              ma=f"diem_danh:{nd_id}:{hom_nay}")
    return so, f"+{so} xu! Bạn đã điểm danh {chuoi} ngày liên tiếp."


def chuoi_diem_danh(nd_id: int):
    """(đã điểm danh hôm nay?, số ngày liên tiếp)."""
    hom_nay = _bay_gio().date()
    with _ket_noi() as kn:
        co = lambda d: kn.execute("SELECT 1 FROM giao_dich_xu WHERE ma=?", (f"diem_danh:{nd_id}:{d}",)).fetchone()
        hom_nay_co = bool(co(hom_nay))
        bat_dau = hom_nay if hom_nay_co else hom_nay - timedelta(days=1)
        n = 0
        while co(bat_dau - timedelta(days=n)):
            n += 1
    return hom_nay_co, n


# ================================================================ VIP
def _cac_goi_dang_huong(kn, nd_id: int) -> list:
    """Các gói VIP còn hạn mà người này được hưởng (của mình, hoặc là thành viên một gói Nhóm)."""
    t = _iso(_bay_gio())
    email = kn.execute("SELECT email FROM nguoi_dung WHERE id=?", (nd_id,)).fetchone()
    email = email["email"] if email else ""
    return [dict(r) for r in kn.execute(
        "SELECT g.* FROM goi_vip g WHERE g.bat_dau<=? AND g.ket_thuc>? AND (g.nguoi_dung_id=? OR (g.loai_goi='nhom' "
        "AND EXISTS (SELECT 1 FROM thanh_vien_nhom t WHERE t.goi_vip_id=g.id AND t.email=?))) ORDER BY g.ket_thuc",
        (t, t, nd_id, email))]


def thong_tin_vip(nd_id: int):
    """None nếu không phải VIP; ngược lại dict: ten, ket_thuc (datetime), loai_goi, la_thanh_vien, dung_thu."""
    with _ket_noi() as kn:
        cac_goi = _cac_goi_dang_huong(kn, nd_id)
    if not cac_goi:
        return None
    # gói hạng cao nhất đang hưởng; cùng hạng thì lấy gói hết hạn muộn nhất
    cuoi = max(cac_goi, key=lambda g: (HANG_GOI[g["loai_goi"]], g["ket_thuc"]))
    return {"ten": GOI_VIP[cuoi["loai_goi"]]["ten"] + (" (dùng thử)" if cuoi["nguon"] == "dung_thu" else ""),
            "hang": HANG_GOI[cuoi["loai_goi"]],
            "loai_goi": cuoi["loai_goi"], "ket_thuc": datetime.fromisoformat(cuoi["ket_thuc"]),
            "la_thanh_vien": cuoi["nguoi_dung_id"] != nd_id, "dung_thu": cuoi["nguon"] == "dung_thu",
            "tu_gia_han": bool(cuoi["tu_gia_han"]) and cuoi["nguoi_dung_id"] == nd_id, "goi_id": cuoi["id"]}


def la_vip(nd_id: int) -> bool:
    return thong_tin_vip(nd_id) is not None


def hang_vip(nd_id: int) -> int:
    v = thong_tin_vip(nd_id)
    return v["hang"] if v else 0


def _kich_hoat_vip(kn, nd_id: int, loai_goi: str, so_ngay: int, nguon: str, xu_thang: int) -> datetime:
    """Thêm một kỳ VIP. Gói 1 người nối tiếp sau kỳ đang có; gói Nhóm bắt đầu ngay."""
    t = _bay_gio()
    bat_dau = t
    # cùng gói -> nối tiếp sau kỳ đang có; gói khác (vd. nâng hạng) -> bắt đầu ngay, chạy song song
    cuoi = kn.execute("SELECT MAX(ket_thuc) FROM goi_vip WHERE nguoi_dung_id=? AND loai_goi=? AND nguon!='dung_thu' "
                      "AND ket_thuc>?", (nd_id, loai_goi, _iso(t))).fetchone()[0]
    if cuoi:
        bat_dau = datetime.fromisoformat(cuoi)
    ket_thuc = bat_dau + timedelta(days=so_ngay)
    kn.execute("INSERT INTO goi_vip (nguoi_dung_id, loai_goi, bat_dau, ket_thuc, nguon, xu_thang, tao_luc) "
               "VALUES (?,?,?,?,?,?,?)", (nd_id, loai_goi, _iso(bat_dau), _iso(ket_thuc), nguon, xu_thang, _iso(t)))
    # đang mở khoá bằng xu mà gói mới đã bao gồm -> hoàn lại xu của những ngày chưa dùng
    hang_moi = HANG_GOI[loai_goi]
    bao_gom = {"du_bao": 1, "du_bao_30": 2, "lich_su": 1}
    for mk in kn.execute("SELECT * FROM mo_khoa WHERE nguoi_dung_id=? AND het_han_luc>? AND tinh_nang!='excel'",
                         (nd_id, _iso(t))).fetchall():
        if hang_moi < bao_gom.get(mk["tinh_nang"], 99):
            continue
        bd, kt = datetime.fromisoformat(mk["bat_dau"]), datetime.fromisoformat(mk["het_han_luc"])
        hoan = math.floor(mk["so_xu"] * (kt - t).total_seconds() / max((kt - bd).total_seconds(), 1))
        kn.execute("UPDATE mo_khoa SET het_han_luc=? WHERE id=?", (_iso(t), mk["id"]))
        _cong(kn, nd_id, hoan, "hoan", f"Hoàn xu ngày chưa dùng · {GIA_MO_KHOA[mk['tinh_nang']][2]}")
    return ket_thuc


def dung_thu(nd_id: int):
    """Dùng thử VIP 7 ngày, mỗi tài khoản 1 lần. Trả về (ok, thông báo)."""
    with _GiaoDich() as kn:
        if kn.execute("SELECT 1 FROM goi_vip WHERE nguoi_dung_id=? AND nguon='dung_thu'", (nd_id,)).fetchone():
            return False, "Tài khoản này đã dùng thử VIP rồi."
        if _cac_goi_dang_huong(kn, nd_id):
            return False, "Bạn đang là VIP, không cần dùng thử."
        kt = _kich_hoat_vip(kn, nd_id, "mua_vang", SO_NGAY_DUNG_THU, "dung_thu", 0)
    return True, f"Đã bật VIP dùng thử đến {kt:%H:%M %d/%m/%Y}. Hết hạn tự về gói Miễn phí, không trừ tiền."


def da_dung_thu(nd_id: int) -> bool:
    with _ket_noi() as kn:
        return bool(kn.execute("SELECT 1 FROM goi_vip WHERE nguoi_dung_id=? AND nguon='dung_thu'",
                               (nd_id,)).fetchone())


def doi_xu_lay_vip(nd_id: int, loai_goi: str):
    """Đổi 500 xu -> Mùa Vàng, 1.300 xu -> Bội Thu. Trả về (ok, thông báo)."""
    if loai_goi not in DOI_XU_LAY_VIP:
        return False, "Gói này không đổi bằng xu được."
    goi, can = GOI_VIP[loai_goi], DOI_XU_LAY_VIP[loai_goi]
    with _GiaoDich() as kn:
        if not _chi(kn, nd_id, can, f"Đổi xu lấy {goi['ten']} ({goi['ky']})"):
            return False, f"Bạn cần {can} xu, hiện có {_so_du(kn, nd_id)} xu."
        kt = _kich_hoat_vip(kn, nd_id, loai_goi, goi["so_ngay"], "xu", 0)
    return True, f"Đã đổi {can} xu lấy {goi['ten']}. VIP dùng được đến {kt:%d/%m/%Y}."


def dat_tu_gia_han(nd_id: int, bat: bool):
    with _ket_noi() as kn:
        kn.execute("UPDATE goi_vip SET tu_gia_han=? WHERE nguoi_dung_id=? AND nguon='tien' AND ket_thuc>?",
                   (1 if bat else 0, nd_id, _iso(_bay_gio())))


# ---------------------------------------------------------------- VIP Nhóm
def goi_nhom_cua(nd_id: int):
    """Gói Nhóm còn hạn mà người này là CHỦ (người mua). None nếu không có."""
    with _ket_noi() as kn:
        r = kn.execute("SELECT * FROM goi_vip WHERE nguoi_dung_id=? AND loai_goi='nhom' AND ket_thuc>? "
                       "ORDER BY ket_thuc DESC LIMIT 1", (nd_id, _iso(_bay_gio()))).fetchone()
        if not r:
            return None
        tv = [dict(x) for x in kn.execute(
            "SELECT t.email, t.them_luc, n.ho_ten FROM thanh_vien_nhom t LEFT JOIN nguoi_dung n ON n.email=t.email "
            "WHERE t.goi_vip_id=? ORDER BY t.them_luc", (r["id"],))]
    return {"id": r["id"], "ket_thuc": datetime.fromisoformat(r["ket_thuc"]), "thanh_vien": tv}


def them_thanh_vien(nd_id: int, email: str):
    email = (email or "").strip().lower()
    if not xt.MAU_EMAIL.match(email):
        return False, "Email chưa đúng định dạng."
    nhom = goi_nhom_cua(nd_id)
    if not nhom:
        return False, "Bạn chưa có gói VIP Nhóm còn hạn."
    with _ket_noi() as kn:
        if kn.execute("SELECT email FROM nguoi_dung WHERE id=?", (nd_id,)).fetchone()["email"] == email:
            return False, "Đây là email của bạn — bạn đã có VIP trong gói rồi."
        if len(nhom["thanh_vien"]) >= GOI_VIP["nhom"]["so_tk"] - 1:
            return False, f"Gói Nhóm chỉ thêm được {GOI_VIP['nhom']['so_tk'] - 1} người."
        try:
            kn.execute("INSERT INTO thanh_vien_nhom (goi_vip_id, email, them_luc) VALUES (?,?,?)",
                       (nhom["id"], email, _iso(_bay_gio())))
        except sqlite3.IntegrityError:
            return False, "Email này đã có trong nhóm."
        da_co_tk = kn.execute("SELECT 1 FROM nguoi_dung WHERE email=?", (email,)).fetchone()
    return True, (f"Đã thêm {email}." if da_co_tk else
                  f"Đã thêm {email}. Khi người này tạo tài khoản bằng email đó sẽ tự có VIP.")


def bo_thanh_vien(nd_id: int, email: str):
    nhom = goi_nhom_cua(nd_id)
    if nhom:
        with _ket_noi() as kn:
            kn.execute("DELETE FROM thanh_vien_nhom WHERE goi_vip_id=? AND email=?", (nhom["id"], email))


# ================================================================ Mở khoá bằng xu & quyền xem
def khoa_du_bao(nong_san: str, loai: str, khu_vuc: str) -> str:
    return f"{nong_san}|{loai}|{khu_vuc}"


def mo_khoa_con_han(nd_id: int, tinh_nang: str, khoa: str):
    """Ngày hết hạn (datetime) nếu đang được mở khoá; không thì None."""
    with _ket_noi() as kn:
        r = kn.execute("SELECT MAX(het_han_luc) FROM mo_khoa WHERE nguoi_dung_id=? AND tinh_nang=? AND khoa=? "
                       "AND het_han_luc>?", (nd_id, tinh_nang, khoa, _iso(_bay_gio()))).fetchone()[0]
    return datetime.fromisoformat(r) if r else None


def co_quyen(nd_id: int, tinh_nang: str, khoa: str = "", hang: int = None) -> bool:
    """Đủ hạng gói -> được dùng. Không thì xem có đang mở khoá bằng xu không."""
    hang = hang_vip(nd_id) if hang is None else hang
    if hang >= HANG_TOI_THIEU.get(tinh_nang, 1):
        return True
    return any(mo_khoa_con_han(nd_id, mk, khoa) for mk in MO_BANG_XU.get(tinh_nang, ()))


def han_mo_bang_xu(nd_id: int, tinh_nang: str, khoa: str = ""):
    """Ngày hết hạn muộn nhất của các lần mở bằng xu áp dụng cho tính năng này (None nếu không có)."""
    cac = [mo_khoa_con_han(nd_id, mk, khoa) for mk in MO_BANG_XU.get(tinh_nang, ())]
    cac = [x for x in cac if x]
    return max(cac) if cac else None


def mo_khoa(nd_id: int, tinh_nang: str, khoa: str):
    """Trả xu để mở khoá. Trả về (ok, thông báo)."""
    so_xu, so_ngay, ten = GIA_MO_KHOA[tinh_nang]
    with _GiaoDich() as kn:
        t = _bay_gio()
        if kn.execute("SELECT 1 FROM mo_khoa WHERE nguoi_dung_id=? AND tinh_nang=? AND khoa=? AND het_han_luc>?",
                      (nd_id, tinh_nang, khoa, _iso(t))).fetchone():
            return True, "Bạn đang được xem mục này rồi."
        mo_ta = khoa.replace("|", " · ")
        if not _chi(kn, nd_id, so_xu, f"Mở khoá «{ten}» · {mo_ta}"):
            return False, f"Bạn cần {so_xu} xu, hiện chỉ có {_so_du(kn, nd_id)} xu."
        het_han = t + timedelta(days=so_ngay)
        kn.execute("INSERT INTO mo_khoa (nguoi_dung_id, tinh_nang, khoa, so_xu, bat_dau, het_han_luc) "
                   "VALUES (?,?,?,?,?,?)", (nd_id, tinh_nang, khoa, so_xu, _iso(t), _iso(het_han)))
    return True, f"Đã mở khoá «{ten}» đến {het_han:%H:%M %d/%m/%Y} (−{so_xu} xu)."


def cac_mo_khoa_con_han(nd_id: int) -> list:
    with _ket_noi() as kn:
        return [{"ten": GIA_MO_KHOA[r["tinh_nang"]][2], "khoa": r["khoa"].replace("|", " · "),
                 "het_han": datetime.fromisoformat(r["het_han_luc"])}
                for r in kn.execute("SELECT * FROM mo_khoa WHERE nguoi_dung_id=? AND het_han_luc>? "
                                    "ORDER BY het_han_luc", (nd_id, _iso(_bay_gio())))]


# ================================================================ Đơn thanh toán (chế độ thử)
def tao_don(nd_id: int, loai_goi: str) -> dict:
    t = _bay_gio()
    ma = "BN" + secrets.token_hex(3).upper()
    with _ket_noi() as kn:
        kn.execute("UPDATE don_thanh_toan SET trang_thai='huy' WHERE nguoi_dung_id=? AND trang_thai='cho'", (nd_id,))
        kn.execute("INSERT INTO don_thanh_toan (ma_don, nguoi_dung_id, san_pham, so_tien, cong, trang_thai, tao_luc, "
                   "het_han_luc) VALUES (?,?,?,?,?,?,?,?)",
                   (ma, nd_id, loai_goi, GOI_VIP[loai_goi]["gia"], "thu" if CHE_DO_THU else "vietqr", "cho",
                    _iso(t), _iso(t + timedelta(minutes=PHUT_GIU_DON))))
    return lay_don(ma)


def lay_don(ma_don: str):
    with _ket_noi() as kn:
        r = kn.execute("SELECT * FROM don_thanh_toan WHERE ma_don=?", (ma_don,)).fetchone()
    if not r:
        return None
    d = dict(r)
    d["het_han_luc"] = datetime.fromisoformat(d["het_han_luc"])
    if d["trang_thai"] == "cho" and d["het_han_luc"] <= _bay_gio():
        d["trang_thai"] = "het_han"
    return d


def xac_nhan_thanh_toan(ma_don: str, ma_giao_dich_cong: str):
    """
    Đánh dấu đơn đã trả tiền và bật VIP. Chế độ thử: gọi từ nút "Giả lập đã thanh toán".
    Sau này nối cổng thật: chỉ gọi hàm này sau khi đã kiểm tra chữ ký + đúng số tiền.
    """
    with _GiaoDich() as kn:
        d = kn.execute("SELECT * FROM don_thanh_toan WHERE ma_don=?", (ma_don,)).fetchone()
        if not d or d["trang_thai"] != "cho":
            return False, "Đơn này không còn chờ thanh toán."
        if datetime.fromisoformat(d["het_han_luc"]) <= _bay_gio():
            kn.execute("UPDATE don_thanh_toan SET trang_thai='het_han' WHERE ma_don=?", (ma_don,))
            return False, "Đơn đã quá 15 phút. Hãy tạo đơn mới."
        kn.execute("UPDATE don_thanh_toan SET trang_thai='thanh_cong', ma_giao_dich_cong=?, xong_luc=? WHERE ma_don=?",
                   (ma_giao_dich_cong, _iso(_bay_gio()), ma_don))
        goi = GOI_VIP[d["san_pham"]]
        kt = _kich_hoat_vip(kn, d["nguoi_dung_id"], d["san_pham"], goi["so_ngay"], "tien", goi["xu_thang"])
    dong_bo(d["nguoi_dung_id"])        # cộng ngay xu tặng tháng đầu
    return True, f"Thanh toán thành công! {goi['ten']} dùng được đến {kt:%d/%m/%Y}."


def huy_don(ma_don: str):
    with _ket_noi() as kn:
        kn.execute("UPDATE don_thanh_toan SET trang_thai='huy' WHERE ma_don=? AND trang_thai='cho'", (ma_don,))


# ================================================================ Cảnh báo giá tuỳ chọn (Bội Thu trở lên)
def them_canh_bao(nd_id: int, nong_san: str, loai: str, khu_vuc: str, kieu: str, nguong: float):
    if kieu not in ("tren", "duoi") or not nguong or nguong <= 0:
        return False, "Ngưỡng giá chưa hợp lệ."
    with _ket_noi() as kn:
        if kn.execute("SELECT COUNT(*) FROM canh_bao_gia WHERE nguoi_dung_id=?", (nd_id,)).fetchone()[0] >= SO_CANH_BAO_TOI_DA:
            return False, f"Bạn đã đặt đủ {SO_CANH_BAO_TOI_DA} cảnh báo. Hãy xoá bớt."
        kn.execute("INSERT INTO canh_bao_gia (nguoi_dung_id, nong_san, loai, khu_vuc, kieu, nguong, tao_luc) "
                   "VALUES (?,?,?,?,?,?,?)", (nd_id, nong_san, loai, khu_vuc, kieu, float(nguong), _iso(_bay_gio())))
    chu = "lên từ" if kieu == "tren" else "xuống còn"
    return True, f"Đã đặt cảnh báo: báo khi giá {loai} · {khu_vuc} {chu} {nguong:,.0f} đ/kg.".replace(",", ".")


def ds_canh_bao(nd_id: int) -> list:
    with _ket_noi() as kn:
        return [dict(r) for r in kn.execute("SELECT * FROM canh_bao_gia WHERE nguoi_dung_id=? ORDER BY id", (nd_id,))]


def xoa_canh_bao(nd_id: int, cb_id: int):
    with _ket_noi() as kn:
        kn.execute("DELETE FROM canh_bao_gia WHERE id=? AND nguoi_dung_id=?", (cb_id, nd_id))


def kiem_tra_canh_bao(nd_id: int, gia_moi_nhat) -> list:
    """
    gia_moi_nhat(nong_san, loai, khu_vuc) -> (ngày, giá) hoặc None.
    Trả về các cảnh báo vừa chạm ngưỡng ở phiên giá MỚI (mỗi phiên chỉ báo 1 lần).
    """
    ket_qua = []
    with _ket_noi() as kn:
        for cb in kn.execute("SELECT * FROM canh_bao_gia WHERE nguoi_dung_id=?", (nd_id,)).fetchall():
            g = gia_moi_nhat(cb["nong_san"], cb["loai"], cb["khu_vuc"])
            if not g:
                continue
            ngay, gia = g
            cham = gia >= cb["nguong"] if cb["kieu"] == "tren" else gia <= cb["nguong"]
            if cham and cb["lan_bao_cuoi"] != str(ngay)[:10]:
                kn.execute("UPDATE canh_bao_gia SET lan_bao_cuoi=? WHERE id=?", (str(ngay)[:10], cb["id"]))
                ket_qua.append({**dict(cb), "gia": gia, "ngay": ngay})
    return ket_qua


# ================================================================ Lượt hỏi Trợ lý AI mỗi ngày
def so_luot_hoi_hom_nay(nd_id: int) -> int:
    with _ket_noi() as kn:
        r = kn.execute("SELECT so_luot FROM luot_hoi_ai WHERE nguoi_dung_id=? AND ngay=?",
                       (nd_id, str(_bay_gio().date()))).fetchone()
    return r[0] if r else 0


def tang_luot_hoi(nd_id: int):
    with _ket_noi() as kn:
        kn.execute("INSERT INTO luot_hoi_ai (nguoi_dung_id, ngay, so_luot) VALUES (?,?,1) "
                   "ON CONFLICT(nguoi_dung_id, ngay) DO UPDATE SET so_luot=so_luot+1",
                   (nd_id, str(_bay_gio().date())))
