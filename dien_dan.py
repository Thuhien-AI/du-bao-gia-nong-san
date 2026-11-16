# -*- coding: utf-8 -*-
"""
Diễn đàn Bồ Nông: phòng chat chung · bảng tin (bài viết, bình luận, thả tim) · chợ nông nghiệp.

LƯU TRỮ: thêm bảng vào file data/nguoi_dung.db có sẵn (không đụng dữ liệu cũ).
GIỮ DIỄN ĐÀN SẠCH:
  - Lọc từ thô tục: tự che bằng *** (danh sách TU_CAM bên dưới, nhóm có thể bổ sung).
  - Giới hạn tốc độ: mỗi người gửi cách nhau ít nhất 5 giây; tối đa 100 tin chat, 10 bài viết,
    200 bình luận mỗi ngày.
  - Báo cáo: nội dung bị 3 người khác nhau báo cáo sẽ tự ẩn (quản trị xem lại và khôi phục được).
  - Người gửi tự xoá nội dung của mình; tài khoản quản trị (admin) xoá được mọi nội dung.
CHỢ: sản phẩm do app quản lý (admin thêm/sửa trên web). Đặt hàng ở chế độ thử như thanh toán VIP.
"""

import io
import re
import secrets
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageOps

import csdl
import vi_xu as vx
import xac_thuc as xt
from san_pham_cho import CHI_TIET, DANH_MUC, SAN_PHAM_MAU

THU_MUC_ANH_SP = Path(__file__).parent / "data" / "anh_san_pham"   # bỏ ảnh vào đây, app tự nạp lên Chợ

CHU_DE = ["Chung", "Lúa", "Cà phê", "Hồ tiêu"]
GIAN_CACH_GIAY = 5
TRAN_NGAY = {"tin": 100, "bai": 10, "bl": 200}
TEN_LOAI = {"tin": "tin nhắn", "bai": "bài viết", "bl": "bình luận"}
SO_BAO_CAO_AN = 3
DAI_TOI_DA = {"tin": 500, "bai": 3000, "bl": 800}
ANH_TOI_DA_MB = 5
SO_ANH_BAI = 10          # tối đa số ảnh mỗi bài viết
SO_ANH_SP = 8            # tối đa số ảnh mỗi sản phẩm
GIU_DON_GIO = 24
TRANG_THAI_DON = {"cho": "Chờ thanh toán", "da_tt": "Đã thanh toán · chờ giao", "da_giao": "Đã giao",
                  "huy": "Đã huỷ"}

# Từ thô tục (viết thường). Thêm từ mới vào đây; khớp nguyên từ, không phân biệt hoa thường.
TU_CAM = [
    "địt", "đụ", "đéo", "lồn", "cặc", "buồi", "đĩ", "dái", "đmm", "đm", "dmm", "dm", "đcm", "dcm", "cmm", "clm",
    "vcl", "vkl", "vl", "vãi lồn", "vãi cả lồn", "clgt", "cc", "đcmm", "địt mẹ", "dit me", "du ma", "đụ má",
    "con mẹ mày", "mẹ mày", "thằng chó", "óc chó", "fuck", "shit", "bitch",
]
_MAU_CAM = re.compile(r"(?<![\wÀ-ỹ])(" + "|".join(sorted(map(re.escape, TU_CAM), key=len, reverse=True))
                      + r")(?![\wÀ-ỹ])", re.IGNORECASE)


def loc_tu(chu: str) -> str:
    """Che từ thô tục bằng ***."""
    return _MAU_CAM.sub(lambda m: "*" * max(3, len(m.group(0))), chu)


# ================================================================ CSDL
def _ket_noi():
    kn = vx._ket_noi()
    if csdl.mot_lan("dien_dan"):
        kn.executescript("""
        CREATE TABLE IF NOT EXISTS dd_tin (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nguoi_dung_id INTEGER NOT NULL, noi_dung TEXT NOT NULL,
            tao_luc TEXT NOT NULL, da_xoa INTEGER NOT NULL DEFAULT 0, an INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS dd_bai (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nguoi_dung_id INTEGER NOT NULL, noi_dung TEXT NOT NULL,
            chu_de TEXT NOT NULL DEFAULT 'Chung', anh BLOB, tao_luc TEXT NOT NULL,
            da_xoa INTEGER NOT NULL DEFAULT 0, an INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS dd_binh_luan (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bai_id INTEGER NOT NULL, nguoi_dung_id INTEGER NOT NULL,
            noi_dung TEXT NOT NULL, tao_luc TEXT NOT NULL, da_xoa INTEGER NOT NULL DEFAULT 0,
            an INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS dd_tim (
            bai_id INTEGER NOT NULL, nguoi_dung_id INTEGER NOT NULL, PRIMARY KEY (bai_id, nguoi_dung_id));
        CREATE TABLE IF NOT EXISTS dd_bao_cao (
            loai TEXT NOT NULL, muc_id INTEGER NOT NULL, nguoi_dung_id INTEGER NOT NULL, tao_luc TEXT NOT NULL,
            PRIMARY KEY (loai, muc_id, nguoi_dung_id));
        CREATE TABLE IF NOT EXISTS cho_san_pham (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ten TEXT NOT NULL, danh_muc TEXT NOT NULL, gia INTEGER NOT NULL,
            don_vi TEXT NOT NULL, mo_ta TEXT NOT NULL DEFAULT '', phu_hop TEXT NOT NULL DEFAULT '', anh BLOB,
            con_hang INTEGER NOT NULL DEFAULT 1, an INTEGER NOT NULL DEFAULT 0, tao_luc TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS cho_don (
            ma_don TEXT PRIMARY KEY, nguoi_dung_id INTEGER NOT NULL, san_pham_id INTEGER NOT NULL,
            ten_sp TEXT NOT NULL, don_vi TEXT NOT NULL, so_luong INTEGER NOT NULL, don_gia INTEGER NOT NULL,
            so_tien INTEGER NOT NULL, ho_ten TEXT NOT NULL, so_dien_thoai TEXT NOT NULL, dia_chi TEXT NOT NULL,
            ghi_chu TEXT NOT NULL DEFAULT '', trang_thai TEXT NOT NULL, tao_luc TEXT NOT NULL,
            het_han_luc TEXT NOT NULL, cap_nhat_luc TEXT);
        CREATE TABLE IF NOT EXISTS dd_bai_anh (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bai_id INTEGER NOT NULL, anh BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS cho_sp_anh (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sp_id INTEGER NOT NULL, anh BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS cho_anh_da_nap (ten_file TEXT PRIMARY KEY, nap_luc TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS ix_dd_bai_anh ON dd_bai_anh(bai_id);
        CREATE INDEX IF NOT EXISTS ix_cho_sp_anh ON cho_sp_anh(sp_id);
        CREATE INDEX IF NOT EXISTS ix_dd_tin ON dd_tin(tao_luc);
        CREATE INDEX IF NOT EXISTS ix_dd_bl ON dd_binh_luan(bai_id);
        """)
        da_co = {r[1] for r in kn.execute("PRAGMA table_info(cho_san_pham)")}
        for cot in ("chi_tiet", "huong_dan", "luu_y"):
            if cot not in da_co:
                kn.execute(f"ALTER TABLE cho_san_pham ADD COLUMN {cot} TEXT NOT NULL DEFAULT ''")
        if not kn.execute("SELECT 1 FROM cho_san_pham LIMIT 1").fetchone():
            bay_gio = _bay_gio()
            kn.executemany("INSERT INTO cho_san_pham (ten, danh_muc, gia, don_vi, mo_ta, phu_hop, tao_luc) "
                           "VALUES (?, ?, ?, ?, ?, ?, ?)", [(*sp, bay_gio) for sp in SAN_PHAM_MAU])
        kn.commit()
        csdl.da_lam("dien_dan")
    return kn


def _bay_gio() -> str:
    return datetime.now().isoformat(timespec="seconds")


_BANG = {"tin": "dd_tin", "bai": "dd_bai", "bl": "dd_binh_luan"}


def _kiem_tra_gui(kn, loai: str, nd_id: int, noi_dung: str):
    """Trả về (nội dung đã lọc, None) hoặc (None, lỗi)."""
    noi_dung = (noi_dung or "").strip()
    if not noi_dung:
        return None, "Bạn chưa nhập nội dung."
    if len(noi_dung) > DAI_TOI_DA[loai]:
        return None, f"Nội dung dài quá ({len(noi_dung)} ký tự, tối đa {DAI_TOI_DA[loai]})."
    bang = _BANG[loai]
    # gián cách 5 giây giữa 2 lần gửi bất kỳ (chat, bài, bình luận)
    gan_nhat = max((r[0] for b in _BANG.values() for r in
                    kn.execute(f"SELECT MAX(tao_luc) FROM {b} WHERE nguoi_dung_id = ?", (nd_id,)) if r[0]),
                   default=None)
    if gan_nhat:
        da_qua = (datetime.now() - datetime.fromisoformat(gan_nhat)).total_seconds()
        if da_qua < GIAN_CACH_GIAY:
            return None, f"Bạn gửi nhanh quá. Chờ {GIAN_CACH_GIAY - int(da_qua)} giây rồi gửi lại nhé."
    dau_ngay = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    so = kn.execute(f"SELECT COUNT(*) FROM {bang} WHERE nguoi_dung_id = ? AND tao_luc >= ?",
                    (nd_id, dau_ngay)).fetchone()[0]
    if so >= TRAN_NGAY[loai]:
        return None, f"Hôm nay bạn đã gửi đủ {TRAN_NGAY[loai]} {TEN_LOAI[loai]}. Mai quay lại nhé!"
    return loc_tu(noi_dung), None


def _anh_gon(du_lieu: bytes) -> bytes:
    """Kiểm tra ảnh thật, xoay đúng chiều, thu về tối đa 1280 px, lưu JPEG."""
    if len(du_lieu) > ANH_TOI_DA_MB * 1024 * 1024:
        raise ValueError(f"Ảnh lớn quá (tối đa {ANH_TOI_DA_MB} MB).")
    try:
        Image.open(io.BytesIO(du_lieu)).verify()
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(du_lieu))).convert("RGB")
    except Exception:
        raise ValueError("File này không phải ảnh hợp lệ (dùng JPG hoặc PNG).")
    im.thumbnail((1280, 1280))
    bo_dem = io.BytesIO()
    im.save(bo_dem, format="JPEG", quality=85, optimize=True)
    return bo_dem.getvalue()


# ================================================================ Phòng chat chung
def gui_tin(nd_id: int, noi_dung: str):
    _ket_noi().close()          # bảo đảm đã có bảng trước khi khoá CSDL
    with vx._GiaoDich() as kn:
        chu, loi = _kiem_tra_gui(kn, "tin", nd_id, noi_dung)
        if loi:
            return False, loi
        kn.execute("INSERT INTO dd_tin (nguoi_dung_id, noi_dung, tao_luc) VALUES (?, ?, ?)", (nd_id, chu, _bay_gio()))
    return True, "Đã gửi."


def ds_tin(so: int = 60, xem_an: bool = False) -> list:
    """Tin mới nhất (cũ → mới), kèm tên và ảnh người gửi."""
    with _ket_noi() as kn:
        rows = kn.execute(f"""SELECT t.id, t.nguoi_dung_id, t.noi_dung, t.tao_luc, t.an, n.ho_ten, n.anh, n.email
                              FROM dd_tin t JOIN nguoi_dung n ON n.id = t.nguoi_dung_id
                              WHERE t.da_xoa = 0 {'' if xem_an else 'AND t.an = 0'}
                              ORDER BY t.id DESC LIMIT ?""", (so,)).fetchall()
    return [dict(r) for r in reversed(rows)]


def so_tin_moi_nhat() -> int:
    with _ket_noi() as kn:
        return kn.execute("SELECT COALESCE(MAX(id), 0) FROM dd_tin").fetchone()[0]


# ================================================================ Bảng tin
def _nhieu_anh(cac_anh, toi_da: int):
    """Danh sách bytes ảnh -> danh sách ảnh đã thu gọn (lỗi -> ValueError)."""
    if isinstance(cac_anh, (bytes, bytearray)):
        cac_anh = [cac_anh]
    cac_anh = [a for a in (cac_anh or []) if a]
    if len(cac_anh) > toi_da:
        raise ValueError(f"Tối đa {toi_da} ảnh (bạn chọn {len(cac_anh)} ảnh).")
    kq = []
    for i, a in enumerate(cac_anh, 1):
        try:
            kq.append(_anh_gon(a))
        except ValueError as loi:
            raise ValueError(f"Ảnh thứ {i}: {loi}" if len(cac_anh) > 1 else str(loi))
    return kq


def dang_bai(nd_id: int, noi_dung: str, chu_de: str, cac_anh=None):
    try:
        cac_anh = _nhieu_anh(cac_anh, SO_ANH_BAI)
    except ValueError as loi:
        return False, str(loi)
    if chu_de not in CHU_DE:
        chu_de = "Chung"
    _ket_noi().close()          # bảo đảm đã có bảng trước khi khoá CSDL
    with vx._GiaoDich() as kn:
        chu, loi = _kiem_tra_gui(kn, "bai", nd_id, noi_dung)
        if loi:
            return False, loi
        bai_id = kn.execute("INSERT INTO dd_bai (nguoi_dung_id, noi_dung, chu_de, tao_luc) VALUES (?, ?, ?, ?)",
                            (nd_id, chu, chu_de, _bay_gio())).lastrowid
        kn.executemany("INSERT INTO dd_bai_anh (bai_id, anh) VALUES (?, ?)", [(bai_id, a) for a in cac_anh])
    return True, "Đã đăng bài viết" + (f" kèm {len(cac_anh)} ảnh." if cac_anh else ".")


def anh_bai(bai_id: int) -> list:
    """Các ảnh của 1 bài (gồm ảnh kiểu cũ lưu trong cột anh)."""
    with _ket_noi() as kn:
        cu = kn.execute("SELECT anh FROM dd_bai WHERE id = ?", (bai_id,)).fetchone()
        moi = [r[0] for r in kn.execute("SELECT anh FROM dd_bai_anh WHERE bai_id = ? ORDER BY id", (bai_id,))]
    return ([cu[0]] if cu and cu[0] else []) + moi


def ds_bai(nd_id: int, chu_de: str = None, sap_xep: str = "moi", so: int = 10, xem_an: bool = False) -> list:
    dk = ["b.da_xoa = 0"] + ([] if xem_an else ["b.an = 0"])
    tham_so = [nd_id]
    if chu_de in CHU_DE:
        dk.append("b.chu_de = ?")
        tham_so.append(chu_de)
    thu_tu = "so_tim DESC, b.id DESC" if sap_xep == "tim" else "b.id DESC"
    with _ket_noi() as kn:
        rows = kn.execute(f"""
            SELECT b.id, b.nguoi_dung_id, b.noi_dung, b.chu_de, b.tao_luc, b.an, n.ho_ten, n.anh AS anh_nd, n.email,
                   (SELECT COUNT(*) FROM dd_tim WHERE bai_id = b.id) AS so_tim,
                   (SELECT COUNT(*) FROM dd_bai_anh WHERE bai_id = b.id) + (b.anh IS NOT NULL) AS so_anh,
                   (SELECT COUNT(*) FROM dd_binh_luan WHERE bai_id = b.id AND da_xoa = 0 AND an = 0) AS so_bl,
                   EXISTS(SELECT 1 FROM dd_tim WHERE bai_id = b.id AND nguoi_dung_id = ?) AS da_tim
            FROM dd_bai b JOIN nguoi_dung n ON n.id = b.nguoi_dung_id
            WHERE {' AND '.join(dk)} ORDER BY {thu_tu} LIMIT ?""", (*tham_so, so + 1)).fetchall()
    return [dict(r) for r in rows]


def tha_tim(nd_id: int, bai_id: int) -> bool:
    """Bật / tắt tim. Trả về True nếu giờ đang thả tim."""
    with _ket_noi() as kn:
        if kn.execute("SELECT 1 FROM dd_tim WHERE bai_id = ? AND nguoi_dung_id = ?", (bai_id, nd_id)).fetchone():
            kn.execute("DELETE FROM dd_tim WHERE bai_id = ? AND nguoi_dung_id = ?", (bai_id, nd_id))
            return False
        kn.execute("INSERT INTO dd_tim (bai_id, nguoi_dung_id) VALUES (?, ?)", (bai_id, nd_id))
        return True


def binh_luan(nd_id: int, bai_id: int, noi_dung: str):
    _ket_noi().close()          # bảo đảm đã có bảng trước khi khoá CSDL
    with vx._GiaoDich() as kn:
        if not kn.execute("SELECT 1 FROM dd_bai WHERE id = ? AND da_xoa = 0", (bai_id,)).fetchone():
            return False, "Bài viết này không còn nữa."
        chu, loi = _kiem_tra_gui(kn, "bl", nd_id, noi_dung)
        if loi:
            return False, loi
        kn.execute("INSERT INTO dd_binh_luan (bai_id, nguoi_dung_id, noi_dung, tao_luc) VALUES (?, ?, ?, ?)",
                   (bai_id, nd_id, chu, _bay_gio()))
    return True, "Đã bình luận."


def ds_binh_luan(bai_id: int, xem_an: bool = False) -> list:
    with _ket_noi() as kn:
        rows = kn.execute(f"""SELECT c.id, c.nguoi_dung_id, c.noi_dung, c.tao_luc, c.an, n.ho_ten, n.anh, n.email
                              FROM dd_binh_luan c JOIN nguoi_dung n ON n.id = c.nguoi_dung_id
                              WHERE c.bai_id = ? AND c.da_xoa = 0 {'' if xem_an else 'AND c.an = 0'}
                              ORDER BY c.id""", (bai_id,)).fetchall()
    return [dict(r) for r in rows]


# ================================================================ Xoá · báo cáo · khôi phục
def xoa(nd_id: int, loai: str, muc_id: int, la_qt: bool = False):
    bang = _BANG[loai]
    with _ket_noi() as kn:
        r = kn.execute(f"SELECT nguoi_dung_id FROM {bang} WHERE id = ? AND da_xoa = 0", (muc_id,)).fetchone()
        if not r:
            return False, "Nội dung này đã bị xoá."
        if r[0] != nd_id and not la_qt:
            return False, "Bạn chỉ xoá được nội dung của chính mình."
        kn.execute(f"UPDATE {bang} SET da_xoa = 1 WHERE id = ?", (muc_id,))
    return True, f"Đã xoá {TEN_LOAI[loai]}."


def bao_cao(nd_id: int, loai: str, muc_id: int):
    bang = _BANG[loai]
    with _ket_noi() as kn:
        r = kn.execute(f"SELECT nguoi_dung_id FROM {bang} WHERE id = ? AND da_xoa = 0", (muc_id,)).fetchone()
        if not r:
            return False, "Nội dung này không còn nữa."
        if r[0] == nd_id:
            return False, "Bạn không thể báo cáo nội dung của chính mình."
        kn.execute("INSERT OR IGNORE INTO dd_bao_cao (loai, muc_id, nguoi_dung_id, tao_luc) VALUES (?, ?, ?, ?)",
                   (loai, muc_id, nd_id, _bay_gio()))
        so = kn.execute("SELECT COUNT(*) FROM dd_bao_cao WHERE loai = ? AND muc_id = ?", (loai, muc_id)).fetchone()[0]
        if so >= SO_BAO_CAO_AN:
            kn.execute(f"UPDATE {bang} SET an = 1 WHERE id = ?", (muc_id,))
            return True, "Cảm ơn bạn! Nội dung đã bị ẩn vì nhiều người báo cáo."
    return True, "Cảm ơn bạn đã báo cáo. Nội dung bị 3 người báo cáo sẽ tự ẩn."


def khoi_phuc(loai: str, muc_id: int):
    """Quản trị: hiện lại nội dung bị ẩn do báo cáo và xoá các báo cáo cũ."""
    with _ket_noi() as kn:
        kn.execute(f"UPDATE {_BANG[loai]} SET an = 0 WHERE id = ?", (muc_id,))
        kn.execute("DELETE FROM dd_bao_cao WHERE loai = ? AND muc_id = ?", (loai, muc_id))
    return True, "Đã hiện lại nội dung."


def so_bi_an() -> int:
    with _ket_noi() as kn:
        return sum(kn.execute(f"SELECT COUNT(*) FROM {b} WHERE an = 1 AND da_xoa = 0").fetchone()[0]
                   for b in _BANG.values())


# ================================================================ Chợ nông nghiệp
def ds_san_pham(danh_muc: str = None, tu_khoa: str = "", xem_an: bool = False) -> list:
    dk, ts = ([] if xem_an else ["an = 0"]), []
    if danh_muc in DANH_MUC:
        dk.append("danh_muc = ?")
        ts.append(danh_muc)
    with _ket_noi() as kn:
        rows = kn.execute("SELECT * FROM cho_san_pham" + (" WHERE " + " AND ".join(dk) if dk else "")
                          + " ORDER BY an, con_hang DESC, id", ts).fetchall()
    kq = [dict(r) for r in rows]
    with _ket_noi() as kn:
        for sp in kq:
            moi = kn.execute("SELECT anh, (SELECT COUNT(*) FROM cho_sp_anh WHERE sp_id = ?) FROM cho_sp_anh "
                             "WHERE sp_id = ? ORDER BY id LIMIT 1", (sp["id"], sp["id"])).fetchone()
            sp["so_anh"] = (1 if sp["anh"] else 0) + (moi[1] if moi else 0)
            if not sp["anh"] and moi:
                sp["anh"] = moi[0]                 # ảnh đại diện = ảnh đầu tiên
    tk = (tu_khoa or "").strip().lower()
    if tk:
        kq = [s for s in kq if tk in f"{s['ten']} {s['mo_ta']} {s['phu_hop']} {s['danh_muc']}".lower()]
    return kq


def lay_san_pham(sp_id: int):
    with _ket_noi() as kn:
        r = kn.execute("SELECT * FROM cho_san_pham WHERE id = ?", (sp_id,)).fetchone()
    return dict(r) if r else None


def anh_san_pham(sp_id: int) -> list:
    """[(id_ảnh, bytes)] của sản phẩm; ảnh kiểu cũ (cột anh) có id = 0."""
    with _ket_noi() as kn:
        cu = kn.execute("SELECT anh FROM cho_san_pham WHERE id = ?", (sp_id,)).fetchone()
        moi = [(r[0], r[1]) for r in kn.execute("SELECT id, anh FROM cho_sp_anh WHERE sp_id = ? ORDER BY id", (sp_id,))]
    return ([(0, cu[0])] if cu and cu[0] else []) + moi


def luu_san_pham(sp_id, ten, danh_muc, gia, don_vi, mo_ta, phu_hop, con_hang, an, anh_moi=None,
                 xoa_anh_ids=(), chi_tiet="", huong_dan="", luu_y=""):
    """Quản trị thêm (sp_id=None) hoặc sửa sản phẩm."""
    ten, don_vi = (ten or "").strip(), (don_vi or "").strip()
    if len(ten) < 2 or not don_vi:
        return False, "Cần nhập tên sản phẩm và đơn vị tính."
    if danh_muc not in DANH_MUC:
        return False, "Danh mục chưa đúng."
    try:
        gia = int(gia)
        assert 0 < gia <= 1_000_000_000
    except Exception:
        return False, "Giá phải là số tiền lớn hơn 0."
    xoa_anh_ids = set(xoa_anh_ids or ())
    con_lai = 0 if sp_id is None else len([1 for i, _ in anh_san_pham(sp_id) if i not in xoa_anh_ids])
    try:
        anh_moi = _nhieu_anh(anh_moi, SO_ANH_SP - con_lai)
    except ValueError as loi:
        return False, f"{loi} Mỗi sản phẩm tối đa {SO_ANH_SP} ảnh."
    with _ket_noi() as kn:
        if sp_id is None:
            moi_id = kn.execute("INSERT INTO cho_san_pham (ten, danh_muc, gia, don_vi, mo_ta, phu_hop, con_hang, an, tao_luc) "
                                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (ten, danh_muc, gia, don_vi, mo_ta.strip(), phu_hop.strip(), int(con_hang), int(an),
                                 _bay_gio())).lastrowid
            kn.executemany("INSERT INTO cho_sp_anh (sp_id, anh) VALUES (?, ?)", [(moi_id, a) for a in anh_moi])
            kn.execute("UPDATE cho_san_pham SET chi_tiet=?, huong_dan=?, luu_y=? WHERE id=?",
                       ((chi_tiet or "").strip(), (huong_dan or "").strip(), (luu_y or "").strip(), moi_id))
            return True, f"Đã thêm “{ten}”" + (f" kèm {len(anh_moi)} ảnh." if anh_moi else ".")
        kn.execute("UPDATE cho_san_pham SET ten=?, danh_muc=?, gia=?, don_vi=?, mo_ta=?, phu_hop=?, con_hang=?, an=? "
                   "WHERE id=?", (ten, danh_muc, gia, don_vi, mo_ta.strip(), phu_hop.strip(), int(con_hang), int(an), sp_id))
        kn.execute("UPDATE cho_san_pham SET chi_tiet=?, huong_dan=?, luu_y=? WHERE id=?",
                   ((chi_tiet or "").strip(), (huong_dan or "").strip(), (luu_y or "").strip(), sp_id))
        if 0 in xoa_anh_ids:
            kn.execute("UPDATE cho_san_pham SET anh = NULL WHERE id = ?", (sp_id,))
        kn.executemany("DELETE FROM cho_sp_anh WHERE id = ? AND sp_id = ?", [(i, sp_id) for i in xoa_anh_ids if i])
        kn.executemany("INSERT INTO cho_sp_anh (sp_id, anh) VALUES (?, ?)", [(sp_id, a) for a in anh_moi])
    return True, f"Đã lưu “{ten}”."


def _don_tu_hang(r) -> dict:
    d = dict(r)
    d["tao_luc"] = datetime.fromisoformat(d["tao_luc"])
    d["het_han_luc"] = datetime.fromisoformat(d["het_han_luc"])
    if d["trang_thai"] == "cho" and d["het_han_luc"] < datetime.now():
        d["trang_thai"] = "huy"
    return d


def tao_don_cho(nd_id, sp_id, so_luong, ho_ten, so_dien_thoai, dia_chi, ghi_chu=""):
    sp = lay_san_pham(sp_id)
    if not sp or sp["an"]:
        return False, "Sản phẩm này không còn bán."
    if not sp["con_hang"]:
        return False, "Sản phẩm đang tạm hết hàng."
    try:
        so_luong = int(so_luong)
        assert 1 <= so_luong <= 999
    except Exception:
        return False, "Số lượng phải từ 1 đến 999."
    ho_ten, so_dien_thoai, dia_chi = (ho_ten or "").strip(), (so_dien_thoai or "").strip(), (dia_chi or "").strip()
    if len(ho_ten) < 2:
        return False, "Cần nhập họ tên người nhận."
    if not re.fullmatch(r"\+?\d[\d\s.]{8,14}", so_dien_thoai):
        return False, "Số điện thoại chưa đúng (ví dụ 0912 345 678)."
    if len(dia_chi) < 8:
        return False, "Cần nhập địa chỉ giao hàng đầy đủ."
    ma = "CH" + secrets.token_hex(3).upper()
    bay_gio = datetime.now()
    with _ket_noi() as kn:
        kn.execute("""INSERT INTO cho_don (ma_don, nguoi_dung_id, san_pham_id, ten_sp, don_vi, so_luong, don_gia, so_tien,
                        ho_ten, so_dien_thoai, dia_chi, ghi_chu, trang_thai, tao_luc, het_han_luc)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'cho', ?, ?)""",
                   (ma, nd_id, sp_id, sp["ten"], sp["don_vi"], so_luong, sp["gia"], sp["gia"] * so_luong, ho_ten,
                    so_dien_thoai, dia_chi, loc_tu((ghi_chu or "").strip()[:300]), bay_gio.isoformat(timespec="seconds"),
                    (bay_gio + timedelta(hours=GIU_DON_GIO)).isoformat(timespec="seconds")))
    return True, ma


def lay_don_cho(ma_don: str):
    with _ket_noi() as kn:
        r = kn.execute("SELECT * FROM cho_don WHERE ma_don = ?", (ma_don or "",)).fetchone()
    return _don_tu_hang(r) if r else None


def _doi_trang_thai(ma_don, tu: tuple, sang: str, nd_id=None):
    with _ket_noi() as kn:
        d = kn.execute("SELECT * FROM cho_don WHERE ma_don = ?", (ma_don,)).fetchone()
        if not d:
            return False, "Không tìm thấy đơn."
        d = _don_tu_hang(d)
        if nd_id is not None and d["nguoi_dung_id"] != nd_id:
            return False, "Đây không phải đơn của bạn."
        if d["trang_thai"] not in tu:
            return False, "Đơn này không đổi trạng thái được nữa."
        kn.execute("UPDATE cho_don SET trang_thai = ?, cap_nhat_luc = ? WHERE ma_don = ?", (sang, _bay_gio(), ma_don))
    return True, "ok"


def gia_lap_thanh_toan_don(nd_id, ma_don):
    if not vx.CHE_DO_THU:
        return False, "Chế độ thử đã tắt."
    ok, tb = _doi_trang_thai(ma_don, ("cho",), "da_tt", nd_id)
    return ok, (f"Đã thanh toán đơn {ma_don} (chế độ thử). Cửa hàng sẽ liên hệ giao hàng." if ok else tb)


def huy_don_cho(nd_id, ma_don):
    ok, tb = _doi_trang_thai(ma_don, ("cho",), "huy", nd_id)
    return ok, (f"Đã huỷ đơn {ma_don}." if ok else tb)


def danh_dau_da_giao(ma_don):
    ok, tb = _doi_trang_thai(ma_don, ("da_tt",), "da_giao")
    return ok, (f"Đơn {ma_don} đã chuyển sang “Đã giao”." if ok else tb)


def ds_don(nd_id: int = None, so: int = 30) -> list:
    """Đơn của 1 người (nd_id) hoặc mọi đơn (quản trị, nd_id=None)."""
    with _ket_noi() as kn:
        if nd_id is None:
            rows = kn.execute("SELECT * FROM cho_don ORDER BY tao_luc DESC LIMIT ?", (so,)).fetchall()
        else:
            rows = kn.execute("SELECT * FROM cho_don WHERE nguoi_dung_id = ? ORDER BY tao_luc DESC LIMIT ?",
                              (nd_id, so)).fetchall()
    return [_don_tu_hang(r) for r in rows]


# ================================================================ Tiện ích hiển thị
def luc_tuong_doi(iso: str) -> str:
    t = datetime.fromisoformat(iso) if isinstance(iso, str) else iso
    giay = (datetime.now() - t).total_seconds()
    if giay < 60:
        return "vừa xong"
    if giay < 3600:
        return f"{int(giay // 60)} phút trước"
    if t.date() == datetime.now().date():
        return f"{t:%H:%M} hôm nay"
    if t.date() == (datetime.now() - timedelta(days=1)).date():
        return f"{t:%H:%M} hôm qua"
    return f"{t:%H:%M} · {t:%d/%m/%Y}"


_hang_cache = {}


def hang_nguoi(nd_id: int, email: str = "") -> int:
    """Hạng VIP để gắn huy hiệu (−1 = quản trị). Nhớ tạm 60 giây cho nhanh."""
    if email == xt.EMAIL_QUAN_TRI:
        return -1
    gio = datetime.now()
    c = _hang_cache.get(nd_id)
    if c and (gio - c[1]).total_seconds() < 60:
        return c[0]
    h = vx.hang_vip(nd_id)
    _hang_cache[nd_id] = (h, gio)
    return h


def ds_bi_an() -> list:
    """Quản trị: các nội dung đang bị ẩn do báo cáo."""
    kq = []
    with _ket_noi() as kn:
        for loai, bang in _BANG.items():
            for r in kn.execute(f"""SELECT x.id, x.noi_dung, x.tao_luc, n.ho_ten,
                                      (SELECT COUNT(*) FROM dd_bao_cao WHERE loai = ? AND muc_id = x.id) AS so_bc
                                    FROM {bang} x JOIN nguoi_dung n ON n.id = x.nguoi_dung_id
                                    WHERE x.an = 1 AND x.da_xoa = 0""", (loai,)):
                kq.append({"loai": loai, **dict(r)})
    return sorted(kq, key=lambda d: d["tao_luc"], reverse=True)


def thong_ke() -> dict:
    dau_ngay = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    with _ket_noi() as kn:
        return {"thanh_vien": kn.execute("SELECT COUNT(*) FROM nguoi_dung").fetchone()[0],
                "bai": kn.execute("SELECT COUNT(*) FROM dd_bai WHERE da_xoa = 0 AND an = 0").fetchone()[0],
                "tin_hom_nay": kn.execute("SELECT COUNT(*) FROM dd_tin WHERE da_xoa = 0 AND tao_luc >= ?",
                                          (dau_ngay,)).fetchone()[0],
                "san_pham": kn.execute("SELECT COUNT(*) FROM cho_san_pham WHERE an = 0").fetchone()[0]}


def thanh_vien_moi(so: int = 5) -> list:
    with _ket_noi() as kn:
        return [dict(r) for r in kn.execute("SELECT id, ho_ten, ngay_tao, anh FROM nguoi_dung WHERE email != ? "
                                            "ORDER BY id DESC LIMIT ?", (xt.EMAIL_QUAN_TRI, so))]


def anh_thanh_vien_moi(so: int = 5) -> dict:
    with _ket_noi() as kn:
        return {r[0]: r[1] for r in kn.execute("SELECT id, anh FROM nguoi_dung WHERE email != ? AND anh IS NOT NULL "
                                               "ORDER BY id DESC LIMIT ?", (xt.EMAIL_QUAN_TRI, so))}


# ================================================================ Nạp ảnh & hướng dẫn sản phẩm
def ten_file(ten: str) -> str:
    """'Phân Urê 46%' -> 'phan-ure-46' (tên file ảnh tương ứng)."""
    t = unicodedata.normalize("NFD", ten.replace("đ", "d").replace("Đ", "D"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def nap_anh_va_huong_dan() -> int:
    """1) Điền chi tiết / hướng dẫn / lưu ý cho sản phẩm còn trống (theo san_pham_cho.CHI_TIET).
    2) Ảnh mới trong data/anh_san_pham/ được gắn vào sản phẩm có tên khớp đầu tên file
       (vd. 'phan-ure-46.png', 'phan-ure-46-anh-that.jpg'). Mỗi file chỉ nạp 1 lần;
       admin xoá ảnh trên web thì ảnh đó không bị nạp lại. Trả về số ảnh vừa nạp."""
    so_anh = 0
    with _ket_noi() as kn:
        cac_sp = [dict(r) for r in kn.execute("SELECT id, ten, chi_tiet, huong_dan, luu_y FROM cho_san_pham")]
        for sp in cac_sp:
            nd = CHI_TIET.get(sp["ten"])
            if nd and not (sp["chi_tiet"] or sp["huong_dan"] or sp["luu_y"]):
                kn.execute("UPDATE cho_san_pham SET chi_tiet=?, huong_dan=?, luu_y=? WHERE id=?",
                           (nd["chi_tiet"], nd["huong_dan"], nd["luu_y"], sp["id"]))
        if not THU_MUC_ANH_SP.is_dir():
            return 0
        da_nap = {r[0] for r in kn.execute("SELECT ten_file FROM cho_anh_da_nap")}
        theo_ten = sorted(((ten_file(sp["ten"]), sp["id"]) for sp in cac_sp), key=lambda x: -len(x[0]))
        for f in sorted(THU_MUC_ANH_SP.iterdir()):
            if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp") or f.name in da_nap:
                continue
            sp_id = next((i for t, i in theo_ten if f.stem.lower() == t or f.stem.lower().startswith(t + "-")
                          or f.stem.lower().startswith(t + "_")), None)
            if sp_id is None:
                continue
            try:
                kn.execute("INSERT INTO cho_sp_anh (sp_id, anh) VALUES (?, ?)", (sp_id, _anh_gon(f.read_bytes())))
                so_anh += 1
            except (ValueError, OSError):
                pass
            kn.execute("INSERT OR IGNORE INTO cho_anh_da_nap (ten_file, nap_luc) VALUES (?, ?)", (f.name, _bay_gio()))
    return so_anh


# ================================================================ ĐẠI LÝ THU MUA
# Danh sách khởi đầu: doanh nghiệp THẬT có thu mua nông sản ở vùng trồng của app, địa chỉ/điện thoại lấy từ
# tài liệu công khai trên internet (link ở cột nguồn). KHÔNG có giá thu mua riêng của từng nơi -> "Gọi hỏi giá".
# Quản trị cập nhật giá / sửa thông tin trên web; người dùng đề xuất thêm (chờ duyệt) và báo sai.
DAI_LY_MAU = [
    dict(ten="Công ty CP Tập đoàn Lộc Trời", nong_san="Lúa", tinh="An Giang",
         dia_chi="23 Hà Hoàng Hổ, phường Long Xuyên, tỉnh An Giang", sdt="0296 3841 299",
         ghi_chu="Doanh nghiệp lúa gạo lớn ở ĐBSCL, có chuỗi liên kết bao tiêu lúa với nông dân. Gọi trước để hỏi điểm thu mua gần nhất.",
         nguon="https://finance.vietstock.vn/LTG-ctcp-tap-doan-loc-troi.htm"),
    dict(ten="Công ty CP Xuất nhập khẩu An Giang (Angimex)", nong_san="Lúa", tinh="An Giang",
         dia_chi="Số 01 Ngô Gia Tự, phường Long Xuyên, tỉnh An Giang", sdt="0296 999 9999",
         ghi_chu="Doanh nghiệp xuất khẩu gạo lâu năm của An Giang. Gọi trước để hỏi kho/điểm thu mua lúa.",
         nguon="https://finance.vietstock.vn/AGM-ctcp-xuat-nhap-khau-an-giang.htm"),
    dict(ten="Simexco Đắk Lắk (Công ty TNHH MTV XNK 2-9 Đắk Lắk)", nong_san="Cà phê,Hồ tiêu", tinh="Đắk Lắk",
         dia_chi="23 Ngô Quyền, phường Thành Công, Buôn Ma Thuột, tỉnh Đắk Lắk", sdt="0262 3950 017",
         ghi_chu="Doanh nghiệp xuất khẩu cà phê hàng đầu Đắk Lắk, cũng kinh doanh hồ tiêu; có chương trình thu mua, hỗ trợ nông dân.",
         nguon="https://thuvienphapluat.vn/ma-so-thue/cong-ty-tnhh-mot-thanh-vien-xuat-nhap-khau-29-dak-lak-mst-6000234538.html"),
    dict(ten="Công ty CP Đầu tư – Xuất nhập khẩu Đắk Lắk", nong_san="Cà phê", tinh="Đắk Lắk",
         dia_chi="228 Hoàng Diệu, phường Thành Công, Buôn Ma Thuột, tỉnh Đắk Lắk", sdt="0262 3852 233",
         ghi_chu="Doanh nghiệp kinh doanh, xuất khẩu cà phê tại Buôn Ma Thuột.",
         nguon="https://yellowpages.vn/pdetail/694893/cà-phê.html"),
    dict(ten="Công ty TNHH Chế biến Gia vị Nedspice Việt Nam", nong_san="Hồ tiêu", tinh="TP. Hồ Chí Minh (Thuận An cũ)",
         dia_chi="Khu phố Hòa Lân 2, phường Thuận Giao, TP. Hồ Chí Minh", sdt="0274 3718 005",
         ghi_chu="Nhà máy chế biến, xuất khẩu hồ tiêu ở Đông Nam Bộ. Thường mua qua thương lái/đại lý – gọi hỏi điều kiện bán trực tiếp.",
         nguon="https://boa.gov.vn/sites/default/files/2025-10/1062tt1025.pdf"),
]
NGAY_GIA_CU = 3


def _bang_dai_ly(kn):
    kn.executescript("""
    CREATE TABLE IF NOT EXISTS dl_dai_ly (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ten TEXT NOT NULL, nong_san TEXT NOT NULL, tinh TEXT NOT NULL,
        dia_chi TEXT NOT NULL, sdt TEXT NOT NULL DEFAULT '', gio_mo TEXT NOT NULL DEFAULT '', gia INTEGER,
        gia_luc TEXT, ghi_chu TEXT NOT NULL DEFAULT '', nguon TEXT NOT NULL DEFAULT '',
        trang_thai TEXT NOT NULL DEFAULT 'duyet', nguoi_gui_id INTEGER, tao_luc TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS dl_bao_sai (
        id INTEGER PRIMARY KEY AUTOINCREMENT, dai_ly_id INTEGER NOT NULL, nguoi_dung_id INTEGER NOT NULL,
        noi_dung TEXT NOT NULL, tao_luc TEXT NOT NULL, da_xem INTEGER NOT NULL DEFAULT 0);
    """)
    if not kn.execute("SELECT 1 FROM dl_dai_ly LIMIT 1").fetchone():
        kn.executemany("INSERT INTO dl_dai_ly (ten, nong_san, tinh, dia_chi, sdt, ghi_chu, nguon, tao_luc) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       [(d["ten"], d["nong_san"], d["tinh"], d["dia_chi"], d["sdt"], d["ghi_chu"], d["nguon"], _bay_gio())
                        for d in DAI_LY_MAU])
        kn.commit()


def _kn_dl():
    kn = _ket_noi()
    if csdl.mot_lan("dai_ly"):
        _bang_dai_ly(kn)
        csdl.da_lam("dai_ly")
    return kn


def ds_dai_ly(nong_san=None, tinh=None, trang_thai="duyet") -> list:
    with _kn_dl() as kn:
        rows = [dict(r) for r in kn.execute("SELECT * FROM dl_dai_ly WHERE trang_thai = ? ORDER BY id", (trang_thai,))]
    if nong_san:
        rows = [r for r in rows if nong_san in r["nong_san"].split(",")]
    if tinh:
        rows = [r for r in rows if r["tinh"] == tinh]
    return rows


def ds_tinh_dai_ly() -> list:
    with _kn_dl() as kn:
        return [r[0] for r in kn.execute("SELECT DISTINCT tinh FROM dl_dai_ly WHERE trang_thai = 'duyet' ORDER BY tinh")]


def lay_dai_ly(dl_id):
    with _kn_dl() as kn:
        r = kn.execute("SELECT * FROM dl_dai_ly WHERE id = ?", (dl_id,)).fetchone()
    return dict(r) if r else None


def _kiem_dai_ly(ten, nong_san, tinh, dia_chi, sdt, gia):
    ten, tinh, dia_chi, sdt = (ten or "").strip(), (tinh or "").strip(), (dia_chi or "").strip(), (sdt or "").strip()
    if len(ten) < 3:
        return None, "Cần nhập tên đại lý."
    ns = [n for n in (nong_san or []) if n in ("Lúa", "Cà phê", "Hồ tiêu")]
    if not ns:
        return None, "Chọn ít nhất 1 loại nông sản đại lý thu mua."
    if len(tinh) < 2 or len(dia_chi) < 6:
        return None, "Cần nhập tỉnh và địa chỉ đầy đủ."
    if sdt and not re.fullmatch(r"\+?\d[\d\s.]{7,14}", sdt):
        return None, "Số điện thoại chưa đúng."
    if gia not in (None, "", 0):
        try:
            gia = int(gia)
            assert 1_000 <= gia <= 1_000_000
        except Exception:
            return None, "Giá thu mua phải là số đồng/kg (từ 1.000 đến 1.000.000)."
    else:
        gia = None
    return dict(ten=loc_tu(ten), nong_san=",".join(ns), tinh=tinh, dia_chi=loc_tu(dia_chi), sdt=sdt, gia=gia), None


def de_xuat_dai_ly(nd_id, ten, nong_san, tinh, dia_chi, sdt="", gia=None, ghi_chu="", la_qt=False):
    """Người dùng đề xuất (chờ duyệt). Quản trị thêm thì hiện luôn."""
    d, loi = _kiem_dai_ly(ten, nong_san, tinh, dia_chi, sdt, gia)
    if loi:
        return False, loi
    with _kn_dl() as kn:
        da_gui = kn.execute("SELECT COUNT(*) FROM dl_dai_ly WHERE nguoi_gui_id = ? AND tao_luc >= ?",
                            (nd_id, datetime.now().replace(hour=0, minute=0, second=0).isoformat())).fetchone()[0]
        if da_gui >= 5 and not la_qt:
            return False, "Hôm nay bạn đã đề xuất đủ 5 đại lý. Mai gửi tiếp nhé!"
        kn.execute("INSERT INTO dl_dai_ly (ten, nong_san, tinh, dia_chi, sdt, gia, gia_luc, ghi_chu, trang_thai, "
                   "nguoi_gui_id, tao_luc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (d["ten"], d["nong_san"], d["tinh"], d["dia_chi"], d["sdt"], d["gia"],
                    _bay_gio() if d["gia"] else None, loc_tu((ghi_chu or "").strip()[:400]),
                    "duyet" if la_qt else "cho", nd_id, _bay_gio()))
    return True, ("Đã thêm đại lý." if la_qt else "Cảm ơn bạn! Đề xuất đã gửi, sẽ hiện sau khi quản trị duyệt.")


def sua_dai_ly(dl_id, ten, nong_san, tinh, dia_chi, sdt, gio_mo, gia, ghi_chu, nguon):
    d, loi = _kiem_dai_ly(ten, nong_san, tinh, dia_chi, sdt, gia)
    if loi:
        return False, loi
    cu = lay_dai_ly(dl_id)
    gia_luc = _bay_gio() if d["gia"] and (not cu or cu["gia"] != d["gia"]) else (cu or {}).get("gia_luc")
    with _kn_dl() as kn:
        kn.execute("UPDATE dl_dai_ly SET ten=?, nong_san=?, tinh=?, dia_chi=?, sdt=?, gio_mo=?, gia=?, gia_luc=?, "
                   "ghi_chu=?, nguon=? WHERE id=?",
                   (d["ten"], d["nong_san"], d["tinh"], d["dia_chi"], d["sdt"], (gio_mo or "").strip(), d["gia"],
                    gia_luc if d["gia"] else None, (ghi_chu or "").strip(), (nguon or "").strip(), dl_id))
    return True, "Đã lưu thông tin đại lý."


def duyet_dai_ly(dl_id, dong_y: bool):
    with _kn_dl() as kn:
        kn.execute("UPDATE dl_dai_ly SET trang_thai = ? WHERE id = ?", ("duyet" if dong_y else "tu_choi", dl_id))
    return True, "Đã duyệt, đại lý đã hiện lên." if dong_y else "Đã từ chối đề xuất."


def xoa_dai_ly(dl_id):
    with _kn_dl() as kn:
        kn.execute("UPDATE dl_dai_ly SET trang_thai = 'xoa' WHERE id = ?", (dl_id,))
    return True, "Đã xoá đại lý."


def bao_sai_dai_ly(nd_id, dl_id, noi_dung):
    noi_dung = (noi_dung or "").strip()
    if len(noi_dung) < 4:
        return False, "Ghi rõ thông tin nào sai nhé (ví dụ: giá hôm nay chỉ còn 6.200 đ/kg)."
    with _kn_dl() as kn:
        kn.execute("INSERT INTO dl_bao_sai (dai_ly_id, nguoi_dung_id, noi_dung, tao_luc) VALUES (?, ?, ?, ?)",
                   (dl_id, nd_id, loc_tu(noi_dung[:400]), _bay_gio()))
    return True, "Cảm ơn bạn! Quản trị sẽ kiểm tra và cập nhật."


def ds_bao_sai_dai_ly() -> list:
    with _kn_dl() as kn:
        return [dict(r) for r in kn.execute(
            """SELECT b.id, b.noi_dung, b.tao_luc, d.ten AS ten_dl, d.id AS dai_ly_id, n.ho_ten
               FROM dl_bao_sai b JOIN dl_dai_ly d ON d.id = b.dai_ly_id JOIN nguoi_dung n ON n.id = b.nguoi_dung_id
               WHERE b.da_xem = 0 ORDER BY b.id DESC""")]


def da_xem_bao_sai(bs_id):
    with _kn_dl() as kn:
        kn.execute("UPDATE dl_bao_sai SET da_xem = 1 WHERE id = ?", (bs_id,))
