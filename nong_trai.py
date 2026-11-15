# -*- coding: utf-8 -*-
"""
Trò chơi "Nông Trại Bồ Nông": trồng lúa, hồ tiêu, cà phê để nhận xu.

LUẬT CHƠI
  - Số ô đất theo gói: Miễn phí 1 ô · VIP Mùa Vàng 2 ô · Bội Thu / Đại Điền / Nhóm 3 ô (tối đa 3).
  - Cây lớn theo thời gian thật qua 4 giai đoạn: hạt → mầm → cây lớn → chín.
    Lúa 2 giờ · Hồ tiêu 4 giờ · Cà phê 8 giờ (khi được tưới đủ).
  - Tưới nước giúp cây lớn nhanh: mỗi lần tưới bớt 15% tổng thời gian trồng; 30 phút tưới được 1 lần,
    tối đa 3 lần cho mỗi cây. Không tưới cây vẫn lớn bình thường.
  - Ô đất: ô giữa luôn mở; ô bên trái mở bằng VIP Mùa Vàng; ô bên phải mở bằng VIP Bội Thu trở lên.
  - Thu hoạch: nông sản vào kho, được điểm kinh nghiệm và +1 xu (tối đa 5 xu thu hoạch/ngày).
  - Nhiệm vụ hằng ngày (gieo 2 · tưới 3 · thu hoạch 2): +3 xu.
  - Đoán giá phiên tới (tăng / đi ngang / giảm) 1 lần/ngày: đúng +3 xu (chấm theo giá thật).
  - Lên cấp: +20 xu.

CHỐNG GIAN LẬN: mọi thời gian tính bằng giờ máy chủ; mỗi phần thưởng xu có mã riêng (không cộng 2 lần);
xu cộng qua sổ xu chung (vi_xu.py) nên hiện trong Lịch sử giao dịch và hết hạn sau 30 ngày như xu tặng khác.
"""

from datetime import date, datetime, timedelta

import csdl
import vi_xu as vx

CAY = {
    "lua": {"ten": "Lúa", "gio": 2, "kn": 8, "bieu_tuong": "🌾", "nong_san": "Lúa"},
    "ho_tieu": {"ten": "Hồ tiêu", "gio": 4, "kn": 12, "bieu_tuong": "🌿", "nong_san": "Hồ tiêu"},
    "ca_phe": {"ten": "Cà phê", "gio": 8, "kn": 16, "bieu_tuong": "☕", "nong_san": "Cà phê"},
}
GIAI_DOAN = ["Hạt giống", "Nảy mầm", "Đang lớn", "Chín – thu hoạch được"]
SO_O_TOI_DA = 3
O_THEO_HANG = {0: 1, 1: 2, 2: 3, 3: 3}          # hạng gói -> số ô đất
# vị trí 0 = ô GIỮA (miễn phí) · 1 = ô TRÁI (Mùa Vàng) · 2 = ô PHẢI (Bội Thu); thứ tự vẽ trái -> phải:
THU_TU_VE = [1, 0, 2]
TUOI_BOT = 0.15                                 # mỗi lần tưới bớt 15% tổng thời gian
TUOI_TOI_DA = 3                                 # tối đa 3 lần tưới / cây
PHUT_CHO_TUOI = 30                              # 30 phút tưới được 1 lần
XU_THU_HOACH, TRAN_XU_THU_HOACH_NGAY = 1, 5
XU_NHIEM_VU, XU_DOAN_DUNG, XU_LEN_CAP = 3, 3, 20
NHIEM_VU = [("gieo", "Gieo hạt", 2), ("tuoi", "Tưới nước", 3), ("thu", "Thu hoạch", 2)]
KN_GIEO, KN_TUOI = 2, 1
CAP_TOI_DA = 30
NGUONG_DI_NGANG = 0.3                           # % thay đổi nhỏ hơn mức này = đi ngang


def _bay_gio() -> datetime:
    return vx._bay_gio()


def _iso(t: datetime) -> str:
    return t.isoformat(timespec="seconds")


def kn_can_cho_cap(cap: int) -> int:
    """Tổng kinh nghiệm cần để đạt cấp `cap` (cấp 1 = 0). Mỗi cấp cần nhiều hơn cấp trước."""
    return 40 * (cap - 1) * cap // 2


# ================================================================ CSDL
def _ket_noi():
    kn = vx._ket_noi()
    if csdl.mot_lan("nong_trai"):
        kn.executescript("""
        CREATE TABLE IF NOT EXISTS nt_o_dat (
            nguoi_dung_id INTEGER NOT NULL, vi_tri INTEGER NOT NULL,
            cay TEXT,                       -- NULL = đất trống
            tien_do REAL NOT NULL DEFAULT 0, -- 0..1 (1 = chín)
            da_tuoi INTEGER NOT NULL DEFAULT 0,  -- số lần đã tưới cây đang trồng
            cap_nhat_luc TEXT,
            gieo_luc TEXT,
            PRIMARY KEY (nguoi_dung_id, vi_tri));
        CREATE TABLE IF NOT EXISTS nt_kho (
            nguoi_dung_id INTEGER NOT NULL, cay TEXT NOT NULL, so_luong INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (nguoi_dung_id, cay));
        CREATE TABLE IF NOT EXISTS nt_nguoi_choi (
            nguoi_dung_id INTEGER PRIMARY KEY, kinh_nghiem INTEGER NOT NULL DEFAULT 0, cap INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS nt_dem (
            nguoi_dung_id INTEGER NOT NULL, ngay TEXT NOT NULL, loai TEXT NOT NULL, so INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (nguoi_dung_id, ngay, loai));
        CREATE TABLE IF NOT EXISTS nt_du_doan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nguoi_dung_id INTEGER NOT NULL, ngay_doan TEXT NOT NULL,
            nong_san TEXT NOT NULL, huong TEXT NOT NULL,       -- tang | ngang | giam
            ngay_gia_goc TEXT NOT NULL, gia_goc REAL NOT NULL,
            ket_qua TEXT,                                       -- NULL = chờ; dung | sai
            huong_that TEXT, ngay_gia_that TEXT, gia_that REAL,
            UNIQUE (nguoi_dung_id, ngay_doan));
        """)
        if "tuoi_luc" not in {r[1] for r in kn.execute("PRAGMA table_info(nt_o_dat)")}:
            kn.execute("ALTER TABLE nt_o_dat ADD COLUMN tuoi_luc TEXT")   # lần tưới gần nhất
        kn.commit()
        csdl.da_lam("nong_trai")
    return kn


def _tang_dem(kn, nd_id: int, loai: str, so: int = 1):
    kn.execute("INSERT INTO nt_dem (nguoi_dung_id, ngay, loai, so) VALUES (?,?,?,?) "
               "ON CONFLICT(nguoi_dung_id, ngay, loai) DO UPDATE SET so = so + ?",
               (nd_id, str(_bay_gio().date()), loai, so, so))


def _dem(kn, nd_id: int, loai: str) -> int:
    r = kn.execute("SELECT so FROM nt_dem WHERE nguoi_dung_id=? AND ngay=? AND loai=?",
                   (nd_id, str(_bay_gio().date()), loai)).fetchone()
    return r[0] if r else 0


def _cong_kn(kn, nd_id: int, diem: int) -> list:
    """Cộng kinh nghiệm; lên cấp thì thưởng xu. Trả về danh sách cấp mới đạt được."""
    kn.execute("INSERT OR IGNORE INTO nt_nguoi_choi (nguoi_dung_id) VALUES (?)", (nd_id,))
    r = kn.execute("SELECT kinh_nghiem, cap FROM nt_nguoi_choi WHERE nguoi_dung_id=?", (nd_id,)).fetchone()
    kinh_nghiem, cap = r["kinh_nghiem"] + diem, r["cap"]
    len_cap = []
    while cap < CAP_TOI_DA and kinh_nghiem >= kn_can_cho_cap(cap + 1):
        cap += 1
        len_cap.append(cap)
        vx._cong(kn, nd_id, XU_LEN_CAP, "tang", f"Nông trại: lên cấp {cap}", ma=f"nt_cap:{nd_id}:{cap}")
    kn.execute("UPDATE nt_nguoi_choi SET kinh_nghiem=?, cap=? WHERE nguoi_dung_id=?", (kinh_nghiem, cap, nd_id))
    return len_cap


# ================================================================ Cây lớn theo thời gian
def _cap_nhat_o(kn, nd_id: int, o) -> dict:
    """Cây lớn đều theo giờ máy chủ: tiến độ += thời gian trôi qua / tổng thời gian trồng."""
    d = dict(o)
    if d["cay"] and d["tien_do"] < 1:
        t = _bay_gio()
        troi = (t - datetime.fromisoformat(d["cap_nhat_luc"])).total_seconds()
        tien_do = min(d["tien_do"] + max(troi, 0) / (CAY[d["cay"]]["gio"] * 3600.0), 1.0)
        kn.execute("UPDATE nt_o_dat SET tien_do=?, cap_nhat_luc=? WHERE nguoi_dung_id=? AND vi_tri=?",
                   (tien_do, _iso(t), nd_id, d["vi_tri"]))
        d.update(tien_do=tien_do, cap_nhat_luc=_iso(t))
    return d


def _trang_thai_tuoi(d: dict):
    """(tưới được không, số giây phải chờ, lý do không tưới được)."""
    if not d["cay"] or d["tien_do"] >= 1:
        return False, 0, ""
    if d["da_tuoi"] >= TUOI_TOI_DA:
        return False, 0, "Đã tưới đủ 3 lần"
    if d.get("tuoi_luc"):
        cho = PHUT_CHO_TUOI * 60 - (_bay_gio() - datetime.fromisoformat(d["tuoi_luc"])).total_seconds()
        if cho > 0:
            return False, int(cho), "Đất còn ẩm"
    return True, 0, ""


def ruong(nd_id: int, hang: int) -> list:
    """3 ô đất (theo vị trí 0, 1, 2) kèm trạng thái để vẽ giao diện."""
    so_o = O_THEO_HANG.get(hang, 1)
    kq = []
    _ket_noi().close()
    with vx._GiaoDich() as kn:
        for vt in range(SO_O_TOI_DA):
            kn.execute("INSERT OR IGNORE INTO nt_o_dat (nguoi_dung_id, vi_tri) VALUES (?,?)", (nd_id, vt))
            d = _cap_nhat_o(kn, nd_id, kn.execute("SELECT * FROM nt_o_dat WHERE nguoi_dung_id=? AND vi_tri=?",
                                                  (nd_id, vt)).fetchone())
            d["mo"] = vt < so_o
            d["giai_doan"] = (3 if d["tien_do"] >= 1 else min(int(d["tien_do"] * 3 + 1e-9), 2)) if d["cay"] else None
            d["tuoi_duoc"], d["cho_tuoi_giay"], d["ly_do_tuoi"] = _trang_thai_tuoi(d)
            d["con_lai_giay"] = int((1 - d["tien_do"]) * CAY[d["cay"]]["gio"] * 3600) if d["cay"] else 0
            d["phut_bot"] = int(CAY[d["cay"]]["gio"] * 60 * TUOI_BOT) if d["cay"] else 0
            kq.append(d)
    return kq


# ================================================================ Hành động
def _lay_o(kn, nd_id, vi_tri, hang):
    if not (0 <= vi_tri < SO_O_TOI_DA):
        return None, "Ô đất không hợp lệ."
    if vi_tri >= O_THEO_HANG.get(hang, 1):
        return None, "Ô đất này đang khoá. Lên VIP để mở thêm ô."
    kn.execute("INSERT OR IGNORE INTO nt_o_dat (nguoi_dung_id, vi_tri) VALUES (?,?)", (nd_id, vi_tri))
    o = kn.execute("SELECT * FROM nt_o_dat WHERE nguoi_dung_id=? AND vi_tri=?", (nd_id, vi_tri)).fetchone()
    return _cap_nhat_o(kn, nd_id, o), None


def gieo(nd_id: int, vi_tri: int, cay: str, hang: int):
    if cay not in CAY:
        return False, "Loại cây không hợp lệ."
    _ket_noi().close()
    with vx._GiaoDich() as kn:
        o, loi = _lay_o(kn, nd_id, vi_tri, hang)
        if loi:
            return False, loi
        if o["cay"]:
            return False, "Ô này đang có cây rồi."
        t = _iso(_bay_gio())
        kn.execute("UPDATE nt_o_dat SET cay=?, tien_do=0, da_tuoi=0, tuoi_luc=NULL, cap_nhat_luc=?, gieo_luc=? "
                   "WHERE nguoi_dung_id=? AND vi_tri=?", (cay, t, t, nd_id, vi_tri))
        _tang_dem(kn, nd_id, "gieo")
        len_cap = _cong_kn(kn, nd_id, KN_GIEO)
    return True, f"Đã gieo {CAY[cay]['ten'].lower()} 🌱. Tưới nước để cây lớn nhanh hơn!" + _chu_len_cap(len_cap)


def tuoi(nd_id: int, vi_tri: int, hang: int):
    """Tưới nước: cây lớn nhanh thêm 15% tổng thời gian trồng (30 phút/lần, tối đa 3 lần/cây)."""
    _ket_noi().close()
    with vx._GiaoDich() as kn:
        o, loi = _lay_o(kn, nd_id, vi_tri, hang)
        if loi:
            return False, loi
        duoc, cho, ly_do = _trang_thai_tuoi(o)
        if not duoc:
            if not o["cay"] or o["tien_do"] >= 1:
                return False, "Ô này không cần tưới."
            return False, (f"{ly_do}, tưới lại sau {max(cho // 60, 1)} phút nữa nhé." if cho else f"{ly_do} cho cây này rồi.")
        tien_do = min(o["tien_do"] + TUOI_BOT, 1.0)
        kn.execute("UPDATE nt_o_dat SET tien_do=?, da_tuoi=da_tuoi+1, tuoi_luc=? WHERE nguoi_dung_id=? AND vi_tri=?",
                   (tien_do, _iso(_bay_gio()), nd_id, vi_tri))
        _tang_dem(kn, nd_id, "tuoi")
        len_cap = _cong_kn(kn, nd_id, KN_TUOI)
    phut = int(CAY[o["cay"]]["gio"] * 60 * TUOI_BOT)
    chu = "Cây đã chín, thu hoạch thôi!" if tien_do >= 1 else f"Cây lớn nhanh thêm {phut} phút."
    return True, f"💧 Đã tưới nước! {chu}" + _chu_len_cap(len_cap)


def thu_hoach(nd_id: int, vi_tri: int, hang: int):
    """Trả về (ok, thông báo, số xu nhận)."""
    _ket_noi().close()
    with vx._GiaoDich() as kn:
        o, loi = _lay_o(kn, nd_id, vi_tri, hang)
        if loi:
            return False, loi, 0
        if not o["cay"] or o["tien_do"] < 1:
            return False, "Cây chưa chín.", 0
        cay = o["cay"]
        kn.execute("UPDATE nt_o_dat SET cay=NULL, tien_do=0, da_tuoi=0, tuoi_luc=NULL, cap_nhat_luc=NULL, gieo_luc=NULL "
                   "WHERE nguoi_dung_id=? AND vi_tri=?", (nd_id, vi_tri))
        kn.execute("INSERT INTO nt_kho (nguoi_dung_id, cay, so_luong) VALUES (?,?,1) "
                   "ON CONFLICT(nguoi_dung_id, cay) DO UPDATE SET so_luong = so_luong + 1", (nd_id, cay))
        _tang_dem(kn, nd_id, "thu")
        xu = 0
        if _dem(kn, nd_id, "xu_thu") < TRAN_XU_THU_HOACH_NGAY:
            _tang_dem(kn, nd_id, "xu_thu", XU_THU_HOACH)
            ma = f"nt_thu:{nd_id}:{_bay_gio().date()}:{_dem(kn, nd_id, 'xu_thu')}"
            vx._cong(kn, nd_id, XU_THU_HOACH, "tang", f"Nông trại: thu hoạch {CAY[cay]['ten'].lower()}", ma=ma)
            xu = XU_THU_HOACH
        len_cap = _cong_kn(kn, nd_id, CAY[cay]["kn"])
    chu = f"🧺 Thu hoạch {CAY[cay]['ten'].lower()}! +{CAY[cay]['kn']} kinh nghiệm"
    chu += f", +{xu} xu." if xu else f". (Hôm nay đã nhận đủ {TRAN_XU_THU_HOACH_NGAY} xu thu hoạch.)"
    return True, chu + _chu_len_cap(len_cap), xu + XU_LEN_CAP * len(len_cap)


def _chu_len_cap(ds: list) -> str:
    return f" 🎉 Lên cấp {ds[-1]}! +{XU_LEN_CAP * len(ds)} xu." if ds else ""


# ================================================================ Nhiệm vụ hằng ngày
def nhiem_vu(nd_id: int) -> dict:
    with _ket_noi() as kn:
        ds = [{"ma": m, "ten": t, "can": c, "da": min(_dem(kn, nd_id, m), c)} for m, t, c in NHIEM_VU]
        da_nhan = bool(kn.execute("SELECT 1 FROM giao_dich_xu WHERE ma=?",
                                  (f"nt_nv:{nd_id}:{_bay_gio().date()}",)).fetchone())
    return {"ds": ds, "xong": all(x["da"] >= x["can"] for x in ds), "da_nhan": da_nhan,
            "xu_thu_hom_nay": _dem_doc(nd_id, "xu_thu")}


def _dem_doc(nd_id, loai):
    with _ket_noi() as kn:
        return _dem(kn, nd_id, loai)


def nhan_thuong_nhiem_vu(nd_id: int):
    nv = nhiem_vu(nd_id)
    if not nv["xong"]:
        return False, "Bạn chưa làm xong nhiệm vụ hôm nay."
    with vx._GiaoDich() as kn:
        ok = vx._cong(kn, nd_id, XU_NHIEM_VU, "tang", "Nông trại: hoàn thành nhiệm vụ ngày",
                      ma=f"nt_nv:{nd_id}:{_bay_gio().date()}")
    return (True, f"🎁 +{XU_NHIEM_VU} xu thưởng nhiệm vụ hôm nay!") if ok else (False, "Bạn đã nhận thưởng hôm nay rồi.")


# ================================================================ Đoán giá phiên tới
def _gia_trung_binh(df, nong_san: str):
    """{ngày: giá trung bình mọi giống/khu vực} của 1 loại nông sản (chỉ ngày có số liệu)."""
    p = df[df["nong_san"] == nong_san]
    return p.groupby("ngay")["gia"].mean().sort_index()


def _huong(goc: float, that: float) -> str:
    pt = (that - goc) / goc * 100
    return "ngang" if abs(pt) < NGUONG_DI_NGANG else ("tang" if pt > 0 else "giam")


def cham_du_doan(nd_id: int, df) -> list:
    """Chấm các lần đoán đã có giá phiên sau. Trả về danh sách kết quả vừa chấm."""
    ket_qua = []
    _ket_noi().close()
    with vx._GiaoDich() as kn:
        for d in kn.execute("SELECT * FROM nt_du_doan WHERE nguoi_dung_id=? AND ket_qua IS NULL", (nd_id,)).fetchall():
            gia = _gia_trung_binh(df, d["nong_san"])
            sau = gia[gia.index > datetime.fromisoformat(d["ngay_gia_goc"])]
            if sau.empty:
                continue
            ngay_that, gia_that = sau.index[0], float(sau.iloc[0])
            huong_that = _huong(d["gia_goc"], gia_that)
            dung = huong_that == d["huong"]
            kn.execute("UPDATE nt_du_doan SET ket_qua=?, huong_that=?, ngay_gia_that=?, gia_that=? WHERE id=?",
                       ("dung" if dung else "sai", huong_that, str(ngay_that)[:10], gia_that, d["id"]))
            if dung:
                vx._cong(kn, nd_id, XU_DOAN_DUNG, "tang", f"Nông trại: đoán đúng giá {d['nong_san'].lower()}",
                         ma=f"nt_doan:{d['id']}")
            ket_qua.append({**dict(d), "ket_qua": "dung" if dung else "sai", "huong_that": huong_that})
    return ket_qua


def doan_gia(nd_id: int, df, nong_san: str, huong: str):
    if huong not in ("tang", "ngang", "giam") or nong_san not in ("Lúa", "Cà phê", "Hồ tiêu"):
        return False, "Lựa chọn không hợp lệ."
    gia = _gia_trung_binh(df, nong_san)
    if gia.empty:
        return False, "Chưa có số liệu giá."
    _ket_noi().close()
    with vx._GiaoDich() as kn:
        if kn.execute("SELECT 1 FROM nt_du_doan WHERE nguoi_dung_id=? AND ngay_doan=?",
                      (nd_id, str(_bay_gio().date()))).fetchone():
            return False, "Hôm nay bạn đã đoán rồi, mai quay lại nhé."
        kn.execute("INSERT INTO nt_du_doan (nguoi_dung_id, ngay_doan, nong_san, huong, ngay_gia_goc, gia_goc) "
                   "VALUES (?,?,?,?,?,?)", (nd_id, str(_bay_gio().date()), nong_san, huong,
                                            str(gia.index[-1])[:10], float(gia.iloc[-1])))
    chu = {"tang": "tăng", "ngang": "đi ngang", "giam": "giảm"}[huong]
    return True, f"Đã ghi: giá {nong_san.lower()} phiên tới sẽ {chu}. Có giá mới là chấm ngay, đúng được +{XU_DOAN_DUNG} xu!"


def du_doan_gan_day(nd_id: int, so: int = 5) -> list:
    with _ket_noi() as kn:
        return [dict(r) for r in kn.execute("SELECT * FROM nt_du_doan WHERE nguoi_dung_id=? ORDER BY id DESC LIMIT ?",
                                            (nd_id, so))]


def da_doan_hom_nay(nd_id: int) -> bool:
    with _ket_noi() as kn:
        return bool(kn.execute("SELECT 1 FROM nt_du_doan WHERE nguoi_dung_id=? AND ngay_doan=?",
                               (nd_id, str(_bay_gio().date()))).fetchone())


# ================================================================ Thông tin người chơi
def nguoi_choi(nd_id: int) -> dict:
    with _ket_noi() as kn:
        kn.execute("INSERT OR IGNORE INTO nt_nguoi_choi (nguoi_dung_id) VALUES (?)", (nd_id,))
        r = kn.execute("SELECT kinh_nghiem, cap FROM nt_nguoi_choi WHERE nguoi_dung_id=?", (nd_id,)).fetchone()
        kho = {x["cay"]: x["so_luong"] for x in kn.execute("SELECT * FROM nt_kho WHERE nguoi_dung_id=?", (nd_id,))}
    cap, knh = r["cap"], r["kinh_nghiem"]
    dau, cuoi = kn_can_cho_cap(cap), kn_can_cho_cap(cap + 1)
    return {"cap": cap, "kinh_nghiem": knh, "kn_trong_cap": knh - dau, "kn_can": cuoi - dau,
            "kho": {k: kho.get(k, 0) for k in CAY}, "cap_toi_da": cap >= CAP_TOI_DA}
