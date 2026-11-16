# Hỗ trợ khách hàng: phiếu hỏi đáp / báo lỗi / khiếu nại / góp ý.
# Khách gửi trong app -> phiếu về tài khoản Quản trị. Phiếu nhận qua email thì quản trị tự tạo lại ở đây.
# Giờ tính theo giờ Việt Nam (UTC+7) để đúng cả khi app chạy trên Streamlit Cloud (máy chủ giờ UTC).

from datetime import datetime, timedelta, timezone

import csdl
import dien_dan as dd

EMAIL_HO_TRO = "bonong.nongtri@gmail.com"
GIO_MO, GIO_DONG = 8, 17                 # 8:00–17:00
NGAY_LAM = {0, 1, 2, 3, 4, 5}            # thứ Hai .. thứ Bảy
TRAN_NGAY = 5                            # phiếu / ngày / tài khoản
ANH_TOI_DA = 3
NGAY_TU_DONG = 3                         # đã trả lời mà khách im lặng 3 ngày -> tự đóng

LOAI = ["Câu hỏi", "Báo lỗi", "Khiếu nại", "Góp ý"]
PHAN_APP = ["Giá & dự báo", "Tài khoản / đăng nhập", "Ví xu & VIP", "Nông trại", "Diễn đàn",
            "Chợ nông nghiệp", "Đại lý thu mua", "Trợ lý", "Khác"]
UU_TIEN = ["Khẩn", "Cao", "Thường", "Thấp"]
GIO_HAN = {"Khẩn": 4, "Cao": 9, "Thường": 9, "Thấp": 18}      # giờ làm việc (9 giờ = 1 ngày làm việc)
TRANG_THAI = {"moi": "Mới", "dang_xu_ly": "Đang xử lý", "da_tra_loi": "Đã trả lời", "da_dong": "Đã đóng"}

MAU_CAU = {
    "Trả lời câu hỏi cách dùng": "Chào {ten}, để [việc cần làm] anh/chị làm như sau: 1) [bước 1] 2) [bước 2]. "
                                 "Nếu vẫn chưa được, anh/chị trả lời ngay phiếu này, em hướng dẫn tiếp ạ.",
    "Nhận khiếu nại, cần kiểm tra": "Chào {ten}, Bồ Nông xin lỗi vì [sự việc]. Em đã chuyển cho nhóm kỹ thuật kiểm tra "
                                    "và sẽ báo lại trước [ngày, giờ]. Trong lúc chờ, anh/chị có thể [cách tạm thời].",
    "Đã sửa xong": "Chào {ten}, lỗi [mô tả ngắn] đã được sửa. Anh/chị tải lại trang và thử giúp em. "
                   "Cảm ơn anh/chị đã báo để Bồ Nông tốt hơn.",
    "Khiếu nại giá dự báo sai": "Chào {ten}, dự báo của Bồ Nông tính từ giá các ngày trước nên chỉ để tham khảo; giá thật "
                                "còn tuỳ thời tiết, thị trường và chất lượng hàng. Em đã ghi lại trường hợp này để nhóm "
                                "cải thiện. Trước khi bán, anh/chị nên gọi hỏi 2–3 đại lý trong mục Đại lý thu mua.",
    "Chưa làm được / góp ý": "Cảm ơn {ten} đã góp ý. Hiện Bồ Nông chưa [làm được việc này] vì [lý do ngắn]. "
                             "Em đã ghi vào danh sách góp ý và sẽ báo anh/chị khi có.",
}

HOI_DAP = [
    ("Làm sao đổi mật khẩu hoặc email?",
     "Bấm vào tên của bạn ở góc trên bên phải để mở Trang cá nhân, rồi mở phần đổi mật khẩu hoặc đổi email."),
    ("Tôi quên mật khẩu thì làm sao?",
     f"App chưa có chức năng tự lấy lại mật khẩu. Bạn gửi email tới {EMAIL_HO_TRO} từ đúng email đã đăng ký, "
     "ghi họ tên – nhân viên sẽ hỗ trợ đặt lại."),
    ("Kiếm xu bằng cách nào?",
     "Vào trang Ví xu bấm Điểm danh mỗi ngày (2 xu, ngày thứ 7 liên tiếp được 10 xu, tối đa 60 xu mỗi tháng). "
     "Bạn cũng nhận xu khi thu hoạch ở Nông trại."),
    ("Có những gói VIP nào?",
     "Có 4 gói: Mùa Vàng (30 ngày), Bội Thu (3 tháng), Đại Điền (12 tháng) và VIP Nhóm (12 tháng, 5 tài khoản). "
     "Xem giá và quyền lợi ở trang Gói VIP."),
    ("Giá trong app lấy từ đâu?",
     "Giá được tổng hợp từ các nguồn công khai và ghi nguồn kèm từng dòng số liệu. Đây là giá tham khảo theo vùng, "
     "giá thật tại đại lý có thể chênh tuỳ độ khô, chất lượng hàng."),
    ("Dự báo giá có chắc đúng không?",
     "Không. Dự báo tính từ diễn biến giá các ngày trước nên chỉ để tham khảo. Trước khi bán, bạn nên gọi hỏi "
     "2–3 đại lý trong mục Đại lý thu mua của Diễn đàn."),
    ("Đặt hàng ở Chợ nông nghiệp có giao thật không?",
     "Chưa. Chợ đang ở chế độ thử: giá là giá mẫu, đơn hàng chưa thu tiền và chưa giao hàng thật."),
    ("Thấy thông tin đại lý hoặc bài viết sai thì báo ở đâu?",
     "Bấm 🚩 Báo sai dưới thẻ đại lý, hoặc nút báo cáo dưới bài viết. Quản trị sẽ kiểm tra."),
]


# ---------------------------------------------------------------- thời gian
def bay_gio() -> datetime:
    """Giờ Việt Nam hiện tại (không kèm múi giờ)."""
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=7)


def _iso(t: datetime) -> str:
    return t.isoformat(timespec="seconds")


def trong_gio_lam(t: datetime = None) -> bool:
    t = t or bay_gio()
    return t.weekday() in NGAY_LAM and GIO_MO <= t.hour < GIO_DONG


def _gio_mo_ke_tiep(t: datetime) -> datetime:
    """Thời điểm bắt đầu làm việc gần nhất kể từ t (chính t nếu đang trong giờ)."""
    for _ in range(10):
        mo = t.replace(hour=GIO_MO, minute=0, second=0, microsecond=0)
        dong = t.replace(hour=GIO_DONG, minute=0, second=0, microsecond=0)
        if t.weekday() in NGAY_LAM:
            if t < mo:
                return mo
            if t < dong:
                return t
        t = (t + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return t


def cong_gio_lam(t: datetime, so_gio: float) -> datetime:
    """t + so_gio giờ LÀM VIỆC (bỏ qua ngoài giờ và Chủ nhật)."""
    con = timedelta(hours=so_gio)
    t = _gio_mo_ke_tiep(t)
    while con > timedelta(0):
        dong = t.replace(hour=GIO_DONG, minute=0, second=0, microsecond=0)
        if t + con <= dong:
            return t + con
        con -= dong - t
        t = _gio_mo_ke_tiep(dong + timedelta(seconds=1))
    return t


def gio_lam_giua(a: datetime, b: datetime) -> float:
    """Số giờ làm việc từ a đến b."""
    if b <= a:
        return 0.0
    tong, t = 0.0, _gio_mo_ke_tiep(a)
    while t < b:
        dong = t.replace(hour=GIO_DONG, minute=0, second=0, microsecond=0)
        tong += (min(dong, b) - t).total_seconds() / 3600
        t = _gio_mo_ke_tiep(dong + timedelta(seconds=1))
    return tong


def uu_tien_mac_dinh(loai: str, phan: str) -> str:
    if loai == "Khiếu nại":
        return "Khẩn" if phan in ("Ví xu & VIP", "Chợ nông nghiệp") else "Cao"
    if loai == "Báo lỗi":
        return "Cao"
    return "Thấp" if loai == "Góp ý" else "Thường"


# ---------------------------------------------------------------- CSDL
def _ket_noi():
    kn = dd._ket_noi()
    if csdl.mot_lan("ho_tro"):
        kn.executescript("""
        CREATE TABLE IF NOT EXISTS ht_phieu (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ma TEXT, nguoi_dung_id INTEGER, ten_lh TEXT NOT NULL DEFAULT '',
            lien_he TEXT NOT NULL DEFAULT '', kenh TEXT NOT NULL DEFAULT 'app', loai TEXT NOT NULL, phan TEXT NOT NULL,
            tieu_de TEXT NOT NULL, uu_tien TEXT NOT NULL, trang_thai TEXT NOT NULL DEFAULT 'moi',
            han_phan_hoi TEXT NOT NULL, tao_luc TEXT NOT NULL, cap_nhat_luc TEXT NOT NULL, phan_hoi_dau_luc TEXT,
            dong_luc TEXT, sao INTEGER, nhan_xet TEXT, kh_chua_doc INTEGER NOT NULL DEFAULT 0,
            qt_chua_doc INTEGER NOT NULL DEFAULT 1, so_lan_tra_loi INTEGER NOT NULL DEFAULT 0);
        CREATE INDEX IF NOT EXISTS ht_phieu_nd ON ht_phieu (nguoi_dung_id);
        CREATE TABLE IF NOT EXISTS ht_tin (
            id INTEGER PRIMARY KEY AUTOINCREMENT, phieu_id INTEGER NOT NULL, ben TEXT NOT NULL,
            noi_dung TEXT NOT NULL, noi_bo INTEGER NOT NULL DEFAULT 0, tao_luc TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS ht_tin_phieu ON ht_tin (phieu_id);
        CREATE TABLE IF NOT EXISTS ht_anh (
            id INTEGER PRIMARY KEY AUTOINCREMENT, phieu_id INTEGER NOT NULL, du_lieu BLOB NOT NULL, tao_luc TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS ht_cai_dat (khoa TEXT PRIMARY KEY, gia_tri TEXT NOT NULL DEFAULT '');
        """)
        kn.commit()
        csdl.da_lam("ho_tro")
    return kn


def _phieu(r) -> dict:
    p = dict(r)
    for k in ("han_phan_hoi", "tao_luc", "cap_nhat_luc", "phan_hoi_dau_luc", "dong_luc"):
        p[k] = datetime.fromisoformat(p[k]) if p.get(k) else None
    p["ten_tt"] = TRANG_THAI.get(p["trang_thai"], p["trang_thai"])
    p["qua_han"] = p["phan_hoi_dau_luc"] is None and p["trang_thai"] != "da_dong" and bay_gio() > p["han_phan_hoi"]
    return p


def _tu_dong_dong(kn):
    """Phiếu đã trả lời mà khách không nhắn thêm NGAY_TU_DONG ngày -> đóng."""
    moc = _iso(bay_gio() - timedelta(days=NGAY_TU_DONG))
    kn.execute("UPDATE ht_phieu SET trang_thai = 'da_dong', dong_luc = ? WHERE trang_thai = 'da_tra_loi' "
               "AND cap_nhat_luc < ?", (_iso(bay_gio()), moc))


# ---------------------------------------------------------------- khách hàng
def gui_phieu(nd_id, ho_ten, loai, phan, tieu_de, noi_dung, lien_he="", cac_anh=(), kenh="app", la_qt=False):
    """Tạo phiếu. Trả về (ok, thông báo, mã phiếu)."""
    tieu_de, noi_dung, lien_he = (tieu_de or "").strip(), (noi_dung or "").strip(), (lien_he or "").strip()
    if loai not in LOAI or phan not in PHAN_APP:
        return False, "Chọn loại yêu cầu và phần của app nhé.", None
    if len(tieu_de) < 4:
        return False, "Tiêu đề ngắn quá – ghi vài chữ cho biết vấn đề là gì.", None
    if len(noi_dung) < 10:
        return False, "Mô tả thêm một chút (ít nhất 10 ký tự) để nhân viên hiểu và giúp nhanh hơn.", None
    if len(cac_anh) > ANH_TOI_DA:
        return False, f"Tối đa {ANH_TOI_DA} ảnh mỗi phiếu.", None
    try:
        anh = [dd._anh_gon(a) for a in cac_anh]
    except ValueError as loi:
        return False, str(loi), None
    now = bay_gio()
    uu = uu_tien_mac_dinh(loai, phan)
    with _ket_noi() as kn:
        if nd_id and not la_qt:
            da_gui = kn.execute("SELECT COUNT(*) FROM ht_phieu WHERE nguoi_dung_id = ? AND tao_luc >= ?",
                                (nd_id, _iso(now.replace(hour=0, minute=0, second=0)))).fetchone()[0]
            if da_gui >= TRAN_NGAY:
                return False, (f"Hôm nay bạn đã gửi {TRAN_NGAY} yêu cầu. Việc gấp xin gửi email tới {EMAIL_HO_TRO}."), None
        pid = kn.execute(
            "INSERT INTO ht_phieu (nguoi_dung_id, ten_lh, lien_he, kenh, loai, phan, tieu_de, uu_tien, han_phan_hoi, "
            "tao_luc, cap_nhat_luc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nd_id, (ho_ten or "").strip()[:80], lien_he[:120], kenh, loai, phan, dd.loc_tu(tieu_de[:120]), uu,
             _iso(cong_gio_lam(now, GIO_HAN[uu])), _iso(now), _iso(now))).lastrowid
        ma = f"HT-{pid:04d}"
        kn.execute("UPDATE ht_phieu SET ma = ? WHERE id = ?", (ma, pid))
        kn.execute("INSERT INTO ht_tin (phieu_id, ben, noi_dung, tao_luc) VALUES (?, 'kh', ?, ?)",
                   (pid, dd.loc_tu(noi_dung[:3000]), _iso(now)))
        for a in anh:
            kn.execute("INSERT INTO ht_anh (phieu_id, du_lieu, tao_luc) VALUES (?, ?, ?)", (pid, a, _iso(now)))
    return True, xac_nhan(ma, uu, now), ma


def xac_nhan(ma, uu, luc=None) -> str:
    han = cong_gio_lam(luc or bay_gio(), GIO_HAN[uu])
    hom_nay = (luc or bay_gio()).date()
    khi = (f"{han:%H:%M} hôm nay" if han.date() == hom_nay
           else f"{han:%H:%M} ngày mai" if han.date() == hom_nay + timedelta(days=1) else f"{han:%H:%M} ngày {han:%d/%m}")
    return (f"Bồ Nông đã nhận yêu cầu của bạn, mã phiếu {ma}. Chúng tôi sẽ trả lời trước {khi}. "
            "Bạn xem trạng thái ở mục Yêu cầu của tôi bên dưới.")


def ds_phieu_cua(nd_id) -> list:
    with _ket_noi() as kn:
        _tu_dong_dong(kn)
        return [_phieu(r) for r in kn.execute("SELECT * FROM ht_phieu WHERE nguoi_dung_id = ? ORDER BY id DESC",
                                              (nd_id,))]


def so_chua_doc(nd_id) -> int:
    try:
        with _ket_noi() as kn:
            return kn.execute("SELECT COUNT(*) FROM ht_phieu WHERE nguoi_dung_id = ? AND kh_chua_doc = 1",
                              (nd_id,)).fetchone()[0]
    except Exception:
        return 0


def lay_phieu(pid, nd_id=None):
    """nd_id: chỉ trả phiếu nếu đúng chủ (None = quản trị xem)."""
    with _ket_noi() as kn:
        r = kn.execute("SELECT * FROM ht_phieu WHERE id = ?", (pid,)).fetchone()
    if not r or (nd_id is not None and r["nguoi_dung_id"] != nd_id):
        return None
    return _phieu(r)


def tin_cua_phieu(pid, xem_noi_bo=False) -> list:
    with _ket_noi() as kn:
        rows = [dict(r) for r in kn.execute("SELECT * FROM ht_tin WHERE phieu_id = ? ORDER BY id", (pid,))]
    for r in rows:
        r["tao_luc"] = datetime.fromisoformat(r["tao_luc"])
    return [r for r in rows if xem_noi_bo or not r["noi_bo"]]


def anh_cua_phieu(pid) -> list:
    with _ket_noi() as kn:
        return [bytes(r[0]) for r in kn.execute("SELECT du_lieu FROM ht_anh WHERE phieu_id = ? ORDER BY id", (pid,))]


def danh_dau_da_doc(pid, ben):
    cot = "kh_chua_doc" if ben == "kh" else "qt_chua_doc"
    with _ket_noi() as kn:
        kn.execute(f"UPDATE ht_phieu SET {cot} = 0 WHERE id = ?", (pid,))


def khach_nhan_tiep(nd_id, pid, noi_dung):
    p = lay_phieu(pid, nd_id)
    noi_dung = (noi_dung or "").strip()
    if not p:
        return False, "Không tìm thấy phiếu."
    if p["trang_thai"] == "da_dong":
        return False, "Phiếu đã đóng. Bạn gửi yêu cầu mới nhé."
    if len(noi_dung) < 2:
        return False, "Bạn chưa nhập nội dung."
    now = _iso(bay_gio())
    with _ket_noi() as kn:
        kn.execute("INSERT INTO ht_tin (phieu_id, ben, noi_dung, tao_luc) VALUES (?, 'kh', ?, ?)",
                   (pid, dd.loc_tu(noi_dung[:3000]), now))
        kn.execute("UPDATE ht_phieu SET qt_chua_doc = 1, cap_nhat_luc = ?, trang_thai = CASE WHEN trang_thai = "
                   "'da_tra_loi' THEN 'dang_xu_ly' ELSE trang_thai END WHERE id = ?", (now, pid))
    return True, "Đã gửi, nhân viên sẽ trả lời trong phiếu này."


def khach_dong_va_cham(nd_id, pid, sao, nhan_xet=""):
    p = lay_phieu(pid, nd_id)
    if not p:
        return False, "Không tìm thấy phiếu."
    try:
        sao = int(sao)
        assert 1 <= sao <= 5
    except Exception:
        return False, "Chọn từ 1 đến 5 sao nhé."
    with _ket_noi() as kn:
        kn.execute("UPDATE ht_phieu SET sao = ?, nhan_xet = ?, trang_thai = 'da_dong', dong_luc = COALESCE(dong_luc, ?) "
                   "WHERE id = ?", (sao, dd.loc_tu((nhan_xet or "").strip()[:300]), _iso(bay_gio()), pid))
    return True, "Cảm ơn bạn đã đánh giá! Phiếu đã đóng."


# ---------------------------------------------------------------- quản trị
def ds_phieu_qt(loc="can_xu_ly") -> list:
    dk = {"can_xu_ly": "trang_thai IN ('moi', 'dang_xu_ly')", "da_tra_loi": "trang_thai = 'da_tra_loi'",
          "da_dong": "trang_thai = 'da_dong'"}.get(loc, "1 = 1")
    with _ket_noi() as kn:
        _tu_dong_dong(kn)
        rows = [_phieu(r) for r in kn.execute(f"SELECT * FROM ht_phieu WHERE {dk} ORDER BY id DESC LIMIT 200")]
    if loc == "can_xu_ly":
        rows.sort(key=lambda p: (not p["qua_han"], UU_TIEN.index(p["uu_tien"]), p["han_phan_hoi"]))
    return rows


def so_can_xu_ly() -> int:
    try:
        with _ket_noi() as kn:
            return kn.execute("SELECT COUNT(*) FROM ht_phieu WHERE trang_thai IN ('moi', 'dang_xu_ly') "
                              "OR qt_chua_doc = 1 AND trang_thai != 'da_dong'").fetchone()[0]
    except Exception:
        return 0


def qt_tra_loi(pid, noi_dung, noi_bo=False, trang_thai=None, uu_tien=None):
    p = lay_phieu(pid)
    noi_dung = (noi_dung or "").strip()
    if not p:
        return False, "Không tìm thấy phiếu."
    now = bay_gio()
    with _ket_noi() as kn:
        if noi_dung:
            kn.execute("INSERT INTO ht_tin (phieu_id, ben, noi_dung, noi_bo, tao_luc) VALUES (?, 'qt', ?, ?, ?)",
                       (pid, noi_dung[:3000], 1 if noi_bo else 0, _iso(now)))
        if noi_dung and not noi_bo:
            tt = trang_thai or "da_tra_loi"
            kn.execute("UPDATE ht_phieu SET trang_thai = ?, kh_chua_doc = 1, qt_chua_doc = 0, cap_nhat_luc = ?, "
                       "so_lan_tra_loi = so_lan_tra_loi + 1, phan_hoi_dau_luc = COALESCE(phan_hoi_dau_luc, ?) "
                       "WHERE id = ?", (tt, _iso(now), _iso(now), pid))
        elif trang_thai:
            kn.execute("UPDATE ht_phieu SET trang_thai = ?, qt_chua_doc = 0 WHERE id = ?", (trang_thai, pid))
        if trang_thai == "da_dong":
            kn.execute("UPDATE ht_phieu SET dong_luc = COALESCE(dong_luc, ?) WHERE id = ?", (_iso(now), pid))
        elif trang_thai:
            kn.execute("UPDATE ht_phieu SET dong_luc = NULL WHERE id = ?", (pid,))
        if uu_tien in UU_TIEN and uu_tien != p["uu_tien"]:
            kn.execute("UPDATE ht_phieu SET uu_tien = ?, han_phan_hoi = ? WHERE id = ?",
                       (uu_tien, _iso(cong_gio_lam(p["tao_luc"], GIO_HAN[uu_tien])), pid))
    if not noi_dung and not trang_thai and not uu_tien:
        return False, "Chưa có gì để lưu."
    return True, ("Đã ghi chú nội bộ." if noi_bo and noi_dung else "Đã gửi trả lời cho khách." if noi_dung
                  else "Đã cập nhật phiếu.")


def thong_tin_tai_khoan(nd_id) -> dict:
    if not nd_id:
        return {}
    with _ket_noi() as kn:
        r = kn.execute("SELECT * FROM nguoi_dung WHERE id = ?", (nd_id,)).fetchone()
        so = kn.execute("SELECT COUNT(*) FROM ht_phieu WHERE nguoi_dung_id = ?", (nd_id,)).fetchone()[0]
    if not r:
        return {}
    r = dict(r)
    return {"ho_ten": r.get("ho_ten", ""), "email": r.get("email", ""), "ngay_tao": (r.get("ngay_tao") or "")[:10],
            "sdt": r.get("so_dien_thoai") or "", "tinh": r.get("tinh") or "", "so_phieu": so}


def doc_cai_dat() -> dict:
    with _ket_noi() as kn:
        d = {r[0]: r[1] for r in kn.execute("SELECT khoa, gia_tri FROM ht_cai_dat")}
    return {"nghi_phep": d.get("nghi_phep") == "1", "ngay_quay_lai": d.get("ngay_quay_lai", "")}


def luu_cai_dat(nghi_phep: bool, ngay_quay_lai: str = ""):
    with _ket_noi() as kn:
        for k, v in (("nghi_phep", "1" if nghi_phep else "0"), ("ngay_quay_lai", ngay_quay_lai or "")):
            kn.execute("INSERT OR REPLACE INTO ht_cai_dat (khoa, gia_tri) VALUES (?, ?)", (k, v))
    return True, "Đã lưu cài đặt."


def thong_ke(so_ngay=7) -> dict:
    tu = bay_gio() - timedelta(days=so_ngay)
    with _ket_noi() as kn:
        rows = [_phieu(r) for r in kn.execute("SELECT * FROM ht_phieu WHERE tao_luc >= ?", (_iso(tu),))]
    co_ph = [p for p in rows if p["phan_hoi_dau_luc"]]
    dung_han = [p for p in co_ph if p["phan_hoi_dau_luc"] <= p["han_phan_hoi"]]
    dong = [p for p in rows if p["trang_thai"] == "da_dong" and p["so_lan_tra_loi"] >= 1]
    mot_lan = [p for p in dong if p["so_lan_tra_loi"] == 1]
    sao = [p["sao"] for p in rows if p["sao"]]
    gio = [gio_lam_giua(p["tao_luc"], p["phan_hoi_dau_luc"]) for p in co_ph]
    return {"tong": len(rows),
            "dung_han": round(100 * len(dung_han) / len(co_ph)) if co_ph else None,
            "gio_tb": round(sum(gio) / len(gio), 1) if gio else None,
            "mot_lan": round(100 * len(mot_lan) / len(dong)) if dong else None,
            "sao_tb": round(sum(sao) / len(sao), 1) if sao else None}


def link_email(chu_de="[Bồ Nông] Hỗ trợ") -> str:
    from urllib.parse import quote
    return f"mailto:{EMAIL_HO_TRO}?subject={quote(chu_de)}"
