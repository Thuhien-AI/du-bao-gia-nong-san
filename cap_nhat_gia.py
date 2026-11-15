# -*- coding: utf-8 -*-
"""
Tự động cập nhật giá nông sản mới vào 3 file CSV trong thư mục data/.

NGUỒN: các bảng "lịch sử 30 ngày" của Báo Hà Tĩnh (baohatinh.vn/cong-cu/...)
  - Hồ tiêu : https://baohatinh.vn/cong-cu/gia-tieu-hom-nay
  - Cà phê  : https://baohatinh.vn/cong-cu/gia-ca-phe-hom-nay
  - Lúa     : https://baohatinh.vn/cong-cu/gia-lua-gao-hom-nay

CÁCH LÀM:
  1. Tải trang, tìm bảng có cột đầu tiên là "Ngày".
  2. Lấy các ngày CHƯA CÓ trong file CSV, tính đến HÔM QUA (theo giờ Việt Nam).
     Vì bảng có 30 ngày, nếu máy tắt vài hôm thì lần sau vẫn lấy bù được.
  3. Lúa & cà phê: ngày nào báo không đăng giá thì lấy giá ngày trước đó và ghi
     "Điền từ ngày trước" (giống cách dataset gốc đang làm). Nếu sau này báo có giá thật
     của ngày đó thì thay bằng giá thật.
  4. KHÔNG sửa bất kỳ giá gốc nào đã có. Trước khi ghi luôn sao lưu file vào data/sao_luu/.

Chạy tay:  python cap_nhat_gia.py
"""

import json
import re
import shutil
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

THU_MUC = Path(__file__).parent
THU_MUC_DATA = THU_MUC / "data"
THU_MUC_SAO_LUU = THU_MUC_DATA / "sao_luu"
FILE_NHAT_KY = THU_MUC_DATA / "nhat_ky_cap_nhat.txt"
FILE_TRANG_THAI = THU_MUC_DATA / "lan_cap_nhat_cuoi.json"

GIO_VIET_NAM = timezone(timedelta(hours=7))
TRINH_DUYET = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DuBaoGiaNongSan/1.0"

NGUON = {
    "Hồ tiêu": ("https://baohatinh.vn/cong-cu/gia-tieu-hom-nay",
                "Báo Hà Tĩnh – bảng lịch sử 30 ngày (baohatinh.vn/cong-cu/gia-tieu-hom-nay)"),
    "Cà phê": ("https://baohatinh.vn/cong-cu/gia-ca-phe-hom-nay",
               "Báo Hà Tĩnh – bảng lịch sử 30 ngày (baohatinh.vn/cong-cu/gia-ca-phe-hom-nay)"),
    "Lúa": ("https://baohatinh.vn/cong-cu/gia-lua-gao-hom-nay",
            "Báo Hà Tĩnh (baohatinh.vn) – bảng giá lúa"),
    "Cà phê thế giới": ("https://baolamdong.vn/gia-ca-phe/the-gioi",
                        "Báo Lâm Đồng – giá cà phê thế giới (baolamdong.vn/gia-ca-phe/the-gioi)"),
    "Hồ tiêu thế giới": ("https://baolamdong.vn/gia-tieu/the-gioi",
                         "Báo Lâm Đồng – trang giá tiêu thế giới (theo IPC)"),
}

# Tên cột trên trang báo  ->  tên trong file CSV (so khớp không phân biệt dấu cách/gạch)
TEN_TINH_TIEU = {"Đắk Lắk": "Đắk Lắk", "Đắk Nông": "Đắk Nông (cũ)",
                 "Bà Rịa–VT": "Bà Rịa – Vũng Tàu (cũ)", "Gia Lai": "Gia Lai",
                 "Bình Phước": "Bình Phước (cũ)", "Đồng Nai": "Đồng Nai"}
TEN_TINH_CA_PHE = {"Đắk Lắk": "Đắk Lắk", "Gia Lai": "Gia Lai", "Lâm Đồng": "Lâm Đồng",
                   "Đắk Nông": "Đắk Nông (cũ)"}


# ================================================================ Đọc trang web
class _DocBang(HTMLParser):
    """Gom mọi bảng <table> trong trang thành danh sách các hàng chữ."""

    def __init__(self):
        super().__init__()
        self.cac_bang, self._bang, self._hang, self._o = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._bang = []
        elif tag == "tr" and self._bang is not None:
            self._hang = []
        elif tag in ("td", "th") and self._hang is not None:
            self._o = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._o is not None:
            self._hang.append(re.sub(r"\s+", " ", "".join(self._o)).strip())
            self._o = None
        elif tag == "tr" and self._hang is not None:
            if self._hang:
                self._bang.append(self._hang)
            self._hang = None
        elif tag == "table" and self._bang is not None:
            self.cac_bang.append(self._bang)
            self._bang = None

    def handle_data(self, data):
        if self._o is not None:
            self._o.append(data)


def tai_trang(url: str) -> str:
    yeu_cau = urllib.request.Request(url, headers={"User-Agent": TRINH_DUYET})
    with urllib.request.urlopen(yeu_cau, timeout=30) as phan_hoi:
        return phan_hoi.read().decode("utf-8", errors="replace")


def lay_bang_lich_su(html: str) -> pd.DataFrame:
    """Tìm bảng có ô đầu tiên là 'Ngày' -> bảng (cột 'ngay' + mỗi tỉnh/giống một cột)."""
    doc = _DocBang()
    doc.feed(html)
    for bang in doc.cac_bang:
        if bang and bang[0] and bang[0][0] == "Ngày":
            tieu_de, cac_hang = bang[0], [h for h in bang[1:] if len(h) == len(bang[0])]
            df = pd.DataFrame(cac_hang, columns=tieu_de)
            df["ngay"] = pd.to_datetime(df["Ngày"], format="%d/%m/%Y", errors="coerce").dt.date
            return df.dropna(subset=["ngay"])
    raise ValueError("Không tìm thấy bảng lịch sử giá trên trang (có thể trang đã đổi giao diện).")


def _chuan(ten: str) -> str:
    return re.sub(r"[\s–\-]", "", ten).lower()


def _tim_cot(df: pd.DataFrame, ten_tren_bao: str):
    for cot in df.columns:
        if _chuan(cot) == _chuan(ten_tren_bao):
            return cot
    return None


def doc_so(chu: str):
    """'138.000' -> 138000 ; '—' hoặc rỗng -> None."""
    chu = (chu or "").strip()
    so = re.sub(r"[^\d]", "", chu)
    return int(so) if so else None


def doc_khoang(chu: str):
    """'6.100–6.200' -> (6100, 6200) ; '6.100' -> (6100, 6100) ; '—' -> None."""
    phan = [doc_so(p) for p in re.split(r"[–\-]", chu or "") if doc_so(p)]
    if not phan:
        return None
    return min(phan), max(phan)


# ================================================================ Ghi file CSV
def hom_qua_viet_nam() -> date:
    return datetime.now(GIO_VIET_NAM).date() - timedelta(days=1)


def _doc_csv(ten_file: str) -> pd.DataFrame:
    return pd.read_csv(THU_MUC_DATA / ten_file, encoding="utf-8-sig", dtype=str,
                       keep_default_na=False)


def _ghi_csv(df: pd.DataFrame, ten_file: str):
    duong_dan = THU_MUC_DATA / ten_file
    THU_MUC_SAO_LUU.mkdir(exist_ok=True)
    ban_sao = THU_MUC_SAO_LUU / f"{duong_dan.stem}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    shutil.copy2(duong_dan, ban_sao)
    # Chỉ giữ 14 bản sao lưu gần nhất của mỗi file
    for cu in sorted(THU_MUC_SAO_LUU.glob(f"{duong_dan.stem}_*.csv"))[:-14]:
        cu.unlink(missing_ok=True)
    # Ghi ra file tạm rồi mới thay -> nếu mất điện giữa chừng, file cũ không bị hỏng
    tam = duong_dan.with_suffix(".tmp")
    df.to_csv(tam, index=False, encoding="utf-8-sig", lineterminator="\r\n")
    tam.replace(duong_dan)


def _sap_xep(df: pd.DataFrame, cot_ten: str, thu_tu: list) -> pd.DataFrame:
    vi_tri = {ten: i for i, ten in enumerate(thu_tu)}
    df = df.assign(_n=df["ngay"], _t=df[cot_ten].map(lambda x: vi_tri.get(x, 99)))
    return df.sort_values(["_n", "_t"], kind="stable").drop(columns=["_n", "_t"])


def _cap_nhat_chung(ten_file, cot_ten, ten_tren_bao, bang, nguon, tao_dong, dien_thieu):
    """
    Phần dùng chung cho cả 3 nông sản.
      cot_ten      : cột trong CSV phân biệt các chuỗi giá (tinh_vung hoặc giong)
      ten_tren_bao : {tên cột trên báo: tên trong CSV}
      tao_dong     : hàm (mẫu, ngày, giá thô, trạng thái, ghi chú) -> dict một dòng CSV
      dien_thieu   : True = ngày không có tin thì lấy giá ngày trước ("Điền từ ngày trước")
    Trả về danh sách các ngày đã thêm và số dòng đã thay.
    """
    df = _doc_csv(ten_file)
    hom_qua = hom_qua_viet_nam()
    ngay_csv = pd.to_datetime(df["ngay"]).dt.date
    ngay_cuoi = ngay_csv.max()
    co_trang_thai = "loai_so_lieu" in df.columns

    # Giá thật trên báo: {ngày: {tên trong CSV: giá thô}}
    cac_chuoi = set(df[cot_ten])
    gia_bao = {}
    for ten_bao, ten_csv in ten_tren_bao.items():
        cot = _tim_cot(bang, ten_bao)
        if cot is None or ten_csv not in cac_chuoi:
            continue
        for _, hang in bang.iterrows():
            gia_bao.setdefault(hang["ngay"], {})[ten_csv] = hang[cot]

    # 1) Thay các dòng "Điền từ ngày trước" nếu nay báo đã có giá thật của ngày đó
    so_dong_thay, tu_ngay_tinh_lai = 0, {}
    if co_trang_thai:
        for i in df.index[df["loai_so_lieu"] == "Điền từ ngày trước"]:
            gia_tho = gia_bao.get(ngay_csv[i], {}).get(df.at[i, cot_ten])
            moi = tao_dong(df.loc[i], ngay_csv[i], gia_tho, "Gốc", "") if gia_tho else None
            if moi:
                for k, v in moi.items():
                    df.at[i, k] = v
                df.at[i, "nguon"] = nguon
                so_dong_thay += 1
                tu_ngay_tinh_lai.setdefault(df.at[i, cot_ten], ngay_csv[i])

        # Các ngày tạm phía SAU một ngày vừa có giá thật -> tính lại theo giá thật mới nhất
        cot_gia = [c for c in ("gia", "gia_thap", "gia_cao", "gia_tb") if c in df.columns]
        for ten, tu_ngay in tu_ngay_tinh_lai.items():
            gan_nhat = None
            for i in df.index[(df[cot_ten] == ten) & (ngay_csv >= tu_ngay)]:
                if df.at[i, "loai_so_lieu"] != "Điền từ ngày trước":
                    gan_nhat = i
                elif gan_nhat is not None:
                    for c in cot_gia:
                        df.at[i, c] = df.at[gan_nhat, c]
                    df.at[i, "ghi_chu"] = ("Không tìm được bản tin ngày này – lấy giá ngày "
                                           f"{ngay_csv[gan_nhat]:%d/%m}")

    # Mẫu của từng chuỗi = dòng gần nhất (giữ tên tỉnh hiện nay, đơn vị...)
    mau_chuoi = {ten: nhom.iloc[-1] for ten, nhom in df.groupby(cot_ten, sort=False)}
    # Giá thật gần nhất của từng chuỗi (để điền ngày thiếu)
    la_goc = ((df["loai_so_lieu"] != "Điền từ ngày trước") if co_trang_thai
              else pd.Series(True, index=df.index))
    gia_truoc = {ten: nhom.iloc[-1] for ten, nhom in df[la_goc].groupby(cot_ten, sort=False)}
    # Chuỗi còn đang có giá ở ngày cuối (vd. IR 50404 đã ngừng thì không điền tạm)
    dang_hoat_dong = set(df.loc[ngay_csv == ngay_cuoi, cot_ten])

    # 2) Thêm các ngày mới, từ sau ngày cuối trong file đến hôm qua
    dong_moi, ngay_co_tin, ngay_dien = [], [], []
    ngay = ngay_cuoi + timedelta(days=1)
    while ngay <= hom_qua:
        co_tin = co_dien = False
        for ten, mau in mau_chuoi.items():
            gia_tho = gia_bao.get(ngay, {}).get(ten)
            dong = tao_dong(mau, ngay, gia_tho, "Gốc", "") if gia_tho else None
            if dong:
                dong["nguon"] = nguon
                dong = {**mau.to_dict(), **dong}
                gia_truoc[ten] = pd.Series(dong)
                co_tin = True
            elif dien_thieu and ten in dang_hoat_dong and ten in gia_truoc:
                truoc = gia_truoc[ten]
                dong = {**mau.to_dict(), **truoc.to_dict(),
                        "ngay": ngay.isoformat(), "loai_so_lieu": "Điền từ ngày trước",
                        "ghi_chu": "Không tìm được bản tin ngày này – lấy giá ngày "
                                   f"{pd.Timestamp(truoc['ngay']):%d/%m}"}
                co_dien = True
            if dong:
                dong_moi.append(dong)
        if co_tin:
            ngay_co_tin.append(ngay)
        elif co_dien:
            ngay_dien.append(ngay)
        ngay += timedelta(days=1)

    if dong_moi or so_dong_thay:
        thu_tu = list(df.loc[ngay_csv == ngay_cuoi, cot_ten])
        if dong_moi:
            # chỉ sắp xếp các dòng MỚI rồi nối vào cuối; thứ tự các dòng cũ giữ nguyên
            moi = _sap_xep(pd.DataFrame(dong_moi)[df.columns], cot_ten, thu_tu)
            df = pd.concat([df, moi], ignore_index=True)
        _ghi_csv(df, ten_file)
    return ngay_co_tin, len(ngay_dien), so_dong_thay


# ================================================================ Từng nông sản
def cap_nhat_ho_tieu(html: str):
    url, nguon = NGUON["Hồ tiêu"]

    def tao_dong(mau, ngay, gia_tho, trang_thai, ghi_chu):
        gia = doc_so(gia_tho)
        return {"ngay": ngay.isoformat(), "gia": str(gia)} if gia else None

    return _cap_nhat_chung("gia_ho_tieu_trong_nuoc.csv", "tinh_vung", TEN_TINH_TIEU,
                           lay_bang_lich_su(html), nguon, tao_dong, dien_thieu=False)


def cap_nhat_ca_phe(html: str):
    url, nguon = NGUON["Cà phê"]

    def tao_dong(mau, ngay, gia_tho, trang_thai, ghi_chu):
        gia = doc_so(gia_tho)
        if not gia:
            return None
        return {"ngay": ngay.isoformat(), "gia": str(gia), "loai_so_lieu": trang_thai,
                "ghi_chu": ghi_chu}

    return _cap_nhat_chung("gia_ca_phe_trong_nuoc.csv", "tinh_vung", TEN_TINH_CA_PHE,
                           lay_bang_lich_su(html), nguon, tao_dong, dien_thieu=True)


def cap_nhat_lua(html: str):
    url, nguon = NGUON["Lúa"]
    bang = lay_bang_lich_su(html)
    # Cột trên báo trùng tên giống trong CSV (OM 18, Đài Thơm 8, OM 5451, IR 50404, OM 34)
    ten_tren_bao = {c: c for c in bang.columns if c not in ("Ngày", "ngay")}

    def tao_dong(mau, ngay, gia_tho, trang_thai, ghi_chu):
        khoang = doc_khoang(gia_tho)
        if not khoang:
            return None
        thap, cao = khoang
        return {"ngay": ngay.isoformat(), "gia_thap": str(thap), "gia_cao": str(cao),
                "gia_tb": str((thap + cao) / 2), "loai_so_lieu": trang_thai, "ghi_chu": ghi_chu}

    return _cap_nhat_chung("gia_lua.csv", "giong", ten_tren_bao, bang, nguon, tao_dong,
                           dien_thieu=True)


def _so_the_gioi(chu: str):
    """'3.226↓ giảm 24' -> 3226 ; '263,30↑ tăng 0,40' -> 263.3 ; '—' -> None."""
    dau = re.match(r"\s*([\d.,]+)", chu or "")
    if not dau:
        return None
    so = dau.group(1).replace(".", "").replace(",", ".")
    try:
        return float(so)
    except ValueError:
        return None


def _ky_han_dai_dien(doc: "_DocBang", thu_tu: int):
    """Kỳ hạn có chữ 'Đại diện' trong bảng kỳ hạn thứ 'thu_tu' (0 = Robusta, 1 = Arabica)."""
    bang_ky_han = [b for b in doc.cac_bang if b and b[0] and b[0][0] == "Kỳ hạn"]
    if len(bang_ky_han) <= thu_tu:
        return ""
    for hang in bang_ky_han[thu_tu][1:]:
        if "Đại diện" in hang[0]:
            m = re.match(r"(\d{2})/(\d{2,4})", hang[0])
            if m:
                return f"{m.group(1)}/{m.group(2)[-2:]}"
    return ""


def cap_nhat_the_gioi(html: str):
    """
    Giá cà phê thế giới (Báo Lâm Đồng): bảng 'Phiên | Robusta London | Arabica New York'.
    Chỉ lấy phiên đã chốt (bỏ dòng 'Đang giao dịch'), chỉ thêm ngày mới hơn ngày cuối trong file.
    """
    ten_file = "gia_ca_phe_the_gioi.csv"
    nguon = NGUON["Cà phê thế giới"][1]
    doc = _DocBang()
    doc.feed(html)
    bang = next((b for b in doc.cac_bang if b and b[0] and b[0][0] == "Phiên"), None)
    if bang is None:
        raise ValueError("Không tìm thấy bảng giá các phiên (có thể trang đã đổi giao diện).")
    ky_r, ky_a = _ky_han_dai_dien(doc, 0), _ky_han_dai_dien(doc, 1)

    df = _doc_csv(ten_file)
    ngay_cuoi = pd.to_datetime(df["ngay_phien"]).max().date()
    hom_nay = datetime.now(GIO_VIET_NAM).date()
    dong_moi = []
    for hang in bang[1:]:
        if len(hang) < 3 or "Đang giao dịch" in hang[0]:
            continue
        m = re.match(r"(\d{2}/\d{2}/\d{4})", hang[0])
        if not m:
            continue
        ngay = datetime.strptime(m.group(1), "%d/%m/%Y").date()
        if ngay <= ngay_cuoi or ngay > hom_nay:
            continue
        r, a = _so_the_gioi(hang[1]), _so_the_gioi(hang[2])
        if r is None and a is None:
            continue
        dong_moi.append({
            "ngay_phien": ngay.isoformat(),
            "robusta_london_usd_tan": "" if r is None else str(int(round(r))),
            "ky_han_robusta": ky_r if r is not None else "",
            "arabica_ny_cent_lb": "" if a is None else str(round(a, 2)),
            "ky_han_arabica": ky_a if a is not None else "",
            "nguon": nguon,
        })
    if dong_moi:
        moi = pd.DataFrame(dong_moi).reindex(columns=df.columns, fill_value="")
        moi = moi.sort_values("ngay_phien", kind="stable")   # dòng cũ giữ nguyên thứ tự
        df = pd.concat([df, moi], ignore_index=True)
        _ghi_csv(df, ten_file)
    them = sorted(datetime.strptime(d["ngay_phien"], "%Y-%m-%d").date() for d in dong_moi)
    return them, 0, 0


# Tên trên trang Báo Lâm Đồng -> (quốc gia, loại) trong file gia_ho_tieu_the_gioi.csv
TEN_TIEU_THE_GIOI = [
    ("Tiêu đen Indonesia (Lampung", ("Indonesia", "Tiêu đen Lampung")),
    ("Tiêu trắng Indonesia (Muntok", ("Indonesia", "Tiêu trắng Muntok")),
    ("Tiêu đen Brazil", ("Brazil", "Tiêu đen ASTA 570")),
    ("Tiêu đen Malaysia", ("Malaysia", "Tiêu đen Kuching ASTA")),
    ("Tiêu trắng Malaysia", ("Malaysia", "Tiêu trắng ASTA")),
    ("Tiêu đen Việt Nam loại 500", ("Việt Nam", "Tiêu đen 500 g/l")),
    ("Tiêu đen Việt Nam loại 550", ("Việt Nam", "Tiêu đen 550 g/l")),
    ("Tiêu trắng Việt Nam", ("Việt Nam", "Tiêu trắng ASTA")),
]


def cap_nhat_tieu_the_gioi(html: str):
    """
    Giá xuất khẩu hồ tiêu các nước theo IPC (Báo Lâm Đồng: bảng giá mới nhất, mỗi loại có
    'Ngày báo giá'). Ghi mỗi ngày một dòng cho mỗi loại, theo quy ước của file:
      giá ngày D = giá IPC công bố gần nhất TRƯỚC ngày D
      (bài báo ngày D thường đưa giá IPC của hôm trước).
    Ngày D liền sau ngày báo giá -> 'Có số liệu'; các ngày khác -> 'Lấy giá ngày trước'.
    Chỉ thêm ngày mới (đến hôm qua, giờ Việt Nam), không sửa dòng cũ.
    """
    ten_file = "gia_ho_tieu_the_gioi.csv"
    url, nguon = NGUON["Hồ tiêu thế giới"]
    doc = _DocBang()
    doc.feed(html)
    bang = next((b for b in doc.cac_bang
                 if b and b[0] and b[0][0].startswith("Thị trường và chủng loại")), None)
    if bang is None:
        raise ValueError("Không tìm thấy bảng giá tiêu thế giới (có thể trang đã đổi giao diện).")

    # Giá mới nhất trên trang: {(quốc gia, loại): (giá, ngày báo giá)}
    tren_trang = {}
    for ten_bao, khoa in TEN_TIEU_THE_GIOI:
        hang = next((h for h in bang if len(h) >= 5 and ten_bao in h[0]), None)
        if hang is None:
            continue
        m = re.search(r"(\d{2}/\d{2}/\d{4})", hang[-1])
        gia = _so_the_gioi(hang[1])
        if m and gia is not None:
            tren_trang[khoa] = (int(round(gia)), datetime.strptime(m.group(1), "%d/%m/%Y").date())

    df = _doc_csv(ten_file)
    ngay_csv = pd.to_datetime(df["ngay"]).dt.date
    ngay_cuoi = ngay_csv.max()
    hom_qua = hom_qua_viet_nam()
    cuoi = df[ngay_csv == ngay_cuoi]                      # các dòng của ngày cuối (giữ thứ tự)
    dong_moi, ngay_co_so_lieu = [], set()
    truoc = {(r["quoc_gia"], r["loai"]): r for _, r in cuoi.iterrows()}
    ngay = ngay_cuoi + timedelta(days=1)
    while ngay <= hom_qua:
        for _, mau in cuoi.iterrows():
            khoa = (mau["quoc_gia"], mau["loai"])
            dong = dict(truoc[khoa])
            dong.update({"ngay": ngay.isoformat(), "nguon": nguon, "link_bai_goc": url})
            gia_trang = tren_trang.get(khoa)
            if gia_trang and gia_trang[1] < ngay:          # đã có giá IPC công bố trước ngày này
                dong["gia"] = str(gia_trang[0])
            if gia_trang and gia_trang[1] == ngay - timedelta(days=1):
                dong["trang_thai"] = "Có số liệu"
                dong["ghi_chu"] = f"Giá IPC công bố ngày {gia_trang[1]:%d/%m/%Y}"
                ngay_co_so_lieu.add(ngay)
            else:
                ngay_truoc = pd.Timestamp(truoc[khoa]["ngay"])
                dong["trang_thai"] = "Lấy giá ngày trước"
                dong["ghi_chu"] = f"Không có báo giá IPC mới – lấy giá ngày {ngay_truoc:%d/%m/%Y}"
            dong_moi.append(dong)
            truoc[khoa] = pd.Series(dong)
        ngay += timedelta(days=1)

    if dong_moi:
        moi = pd.DataFrame(dong_moi).reindex(columns=df.columns, fill_value="")
        _ghi_csv(pd.concat([df, moi], ignore_index=True), ten_file)   # dòng cũ giữ nguyên thứ tự
    so_ngay_them = len({d["ngay"] for d in dong_moi})
    return sorted(ngay_co_so_lieu), so_ngay_them - len(ngay_co_so_lieu), 0


CAP_NHAT = {"Lúa": cap_nhat_lua, "Cà phê": cap_nhat_ca_phe, "Hồ tiêu": cap_nhat_ho_tieu,
            "Cà phê thế giới": cap_nhat_the_gioi, "Hồ tiêu thế giới": cap_nhat_tieu_the_gioi}
FILE_CUA = {"Lúa": "gia_lua.csv", "Cà phê": "gia_ca_phe_trong_nuoc.csv",
            "Hồ tiêu": "gia_ho_tieu_trong_nuoc.csv", "Cà phê thế giới": "gia_ca_phe_the_gioi.csv",
            "Hồ tiêu thế giới": "gia_ho_tieu_the_gioi.csv"}
# Giá IPC không đăng mỗi ngày -> không dùng để quyết định "có cần cập nhật khi mở web không"
FILE_KIEM_TRA_THIEU = [f for ten, f in FILE_CUA.items() if ten != "Hồ tiêu thế giới"]


def ngay_moi_nhat(ten_file: str):
    cot = "ngay_phien" if ten_file == "gia_ca_phe_the_gioi.csv" else "ngay"
    ngay = pd.read_csv(THU_MUC_DATA / ten_file, encoding="utf-8-sig", usecols=[cot])
    return pd.to_datetime(ngay[cot]).max().date()


# ================================================================ Hàm chính
def cap_nhat_tat_ca(tai=tai_trang) -> list:
    """Cập nhật cả 3 nông sản. Trả về danh sách câu báo cáo (dễ đọc)."""
    bao_cao = []
    for ten, ham in CAP_NHAT.items():
        try:
            them, dien, thay = ham(tai(NGUON[ten][0]))
            phan = []
            if them:
                phan.append("thêm giá ngày " + ", ".join(f"{d:%d/%m}" for d in them))
            if dien:
                phan.append(f"{dien} ngày báo không đăng giá (lấy giá ngày trước)")
            if thay:
                phan.append(f"thay {thay} dòng tạm bằng giá thật")
            if not phan:
                moi_nhat = ngay_moi_nhat(FILE_CUA[ten])
                phan.append("đã đầy đủ đến hôm qua" if moi_nhat >= hom_qua_viet_nam()
                            else f"báo chưa đăng giá mới (số liệu mới nhất: {moi_nhat:%d/%m})")
            bao_cao.append(f"✅ {ten}: " + "; ".join(phan))
        except Exception as loi:
            bao_cao.append(f"⚠️ {ten}: không cập nhật được ({loi}). Dữ liệu cũ vẫn giữ nguyên.")

    thoi_gian = datetime.now()
    with open(FILE_NHAT_KY, "a", encoding="utf-8") as f:
        for dong in bao_cao:
            f.write(f"{thoi_gian:%Y-%m-%d %H:%M}  {dong}\n")
    FILE_TRANG_THAI.write_text(json.dumps(
        {"lan_cuoi": thoi_gian.isoformat(timespec="seconds"), "bao_cao": bao_cao},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return bao_cao


def doc_trang_thai() -> dict:
    """Lần cập nhật gần nhất (để hiện lên web)."""
    try:
        return json.loads(FILE_TRANG_THAI.read_text(encoding="utf-8"))
    except Exception:
        return {}


def can_cap_nhat(so_gio_cho: float = 3) -> bool:
    """
    True nếu dữ liệu còn thiếu ngày hôm qua VÀ lần thử gần nhất đã cách đây quá 'so_gio_cho' giờ
    (tránh tải trang báo liên tục mỗi khi mở web).
    """
    hom_qua = hom_qua_viet_nam()
    thieu = False
    for ten_file in FILE_KIEM_TRA_THIEU:
        try:
            if ngay_moi_nhat(ten_file) < hom_qua:
                thieu = True
        except Exception:
            thieu = True
    if not thieu:
        return False
    lan_cuoi = doc_trang_thai().get("lan_cuoi")
    if lan_cuoi and datetime.now() - datetime.fromisoformat(lan_cuoi) < timedelta(hours=so_gio_cho):
        return False
    return True


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # hiện đúng tiếng Việt trên Windows
    print(f"Đang cập nhật giá (đến ngày {hom_qua_viet_nam():%d/%m/%Y}, giờ Việt Nam)...")
    for dong in cap_nhat_tat_ca():
        print(dong)
