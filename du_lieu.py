# -*- coding: utf-8 -*-
"""
Đọc và làm sạch dữ liệu giá nông sản.

Đầu vào: 3 file CSV trong thư mục data/ (lúa, cà phê, hồ tiêu) – mỗi file có cột khác nhau.
Đầu ra: MỘT bảng chung với các cột:
    ngay        – ngày (kiểu ngày tháng)
    nong_san    – Lúa / Cà phê / Hồ tiêu
    loai        – giống lúa hoặc loại cà phê / tiêu
    khu_vuc     – tỉnh / vùng
    gia         – giá (đồng/kg); với lúa là giá trung bình giữa giá thấp và giá cao
    trang_thai  – "Gốc", "Điền từ ngày trước", "Nghi sai", "Điền tự động"...
    nguon       – nguồn số liệu

Các bước làm sạch:
    1. Gộp 3 file về cùng một kiểu cột.
    2. Giữ nguyên mọi giá trong dataset gốc (kể cả dòng ghi "Nghi sai").
    3. Ngày bị thiếu hoàn toàn -> điền bằng nội suy (nối thẳng giữa hai ngày có giá).
"""

from pathlib import Path

import numpy as np
import pandas as pd

THU_MUC_DATA = Path(__file__).parent / "data"

FILE_LUA = "gia_lua.csv"
FILE_CA_PHE = "gia_ca_phe_trong_nuoc.csv"
FILE_HO_TIEU = "gia_ho_tieu_trong_nuoc.csv"
FILE_CA_PHE_THE_GIOI = "gia_ca_phe_the_gioi.csv"
FILE_HO_TIEU_THE_GIOI = "gia_ho_tieu_the_gioi.csv"
CAC_FILE = (FILE_LUA, FILE_CA_PHE, FILE_HO_TIEU, FILE_CA_PHE_THE_GIOI, FILE_HO_TIEU_THE_GIOI)

COT_CHUNG = ["ngay", "nong_san", "loai", "khu_vuc", "gia", "trang_thai", "nguon"]


def _doc_csv(ten_file: str) -> pd.DataFrame:
    duong_dan = THU_MUC_DATA / ten_file
    if not duong_dan.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file '{ten_file}' trong thư mục data/. "
            f"Hãy kiểm tra lại tên file (phải đúng là {ten_file})."
        )
    # utf-8-sig: đọc đúng tiếng Việt và bỏ ký tự ẩn ở đầu file do Excel tạo ra
    return pd.read_csv(duong_dan, encoding="utf-8-sig")


def _ten_khu_vuc(tinh_vung: pd.Series, tinh_hien_nay: pd.Series) -> pd.Series:
    """'Đắk Nông (cũ)' + 'Lâm Đồng' -> 'Đắk Nông (cũ) – nay Lâm Đồng'."""
    ten = tinh_vung.astype(str).str.strip()
    nay = tinh_hien_nay.astype(str).str.strip()
    khac = ten.str.contains(r"\(cũ\)") & (nay != "") & (nay != "nan")
    ten = ten.where(~khac, ten + " – nay " + nay)
    return ten


def _chuan_hoa_lua(df: pd.DataFrame) -> pd.DataFrame:
    gia = df["gia_tb"]
    # Nếu thiếu giá trung bình thì tự tính từ giá thấp và giá cao
    gia = gia.fillna((df["gia_thap"] + df["gia_cao"]) / 2)
    khu_vuc = df["khu_vuc"].astype(str).str.replace("ĐBSCL – giá tham khảo An Giang",
                                                     "An Giang (ĐBSCL)", regex=False)
    return pd.DataFrame({
        "ngay": df["ngay"],
        "nong_san": "Lúa",
        "loai": "Lúa tươi " + df["giong"].astype(str).str.strip(),
        "khu_vuc": khu_vuc,
        "gia": gia,
        "trang_thai": df["loai_so_lieu"].fillna("Gốc"),
        "nguon": df["nguon"],
    })


def _chuan_hoa_ca_phe(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "ngay": df["ngay"],
        "nong_san": "Cà phê",
        "loai": df["loai"].astype(str).str.strip(),
        "khu_vuc": _ten_khu_vuc(df["tinh_vung"], df["tinh_hien_nay"]),
        "gia": df["gia"],
        "trang_thai": df["loai_so_lieu"].fillna("Gốc"),
        "nguon": df["nguon"],
    })


def _chuan_hoa_ho_tieu(df: pd.DataFrame) -> pd.DataFrame:
    trang_thai = df["loai_so_lieu"] if "loai_so_lieu" in df else "Gốc"
    return pd.DataFrame({
        "ngay": df["ngay"],
        "nong_san": "Hồ tiêu",
        "loai": df["loai"].astype(str).str.strip(),
        "khu_vuc": _ten_khu_vuc(df["tinh_vung"], df["tinh_hien_nay"]),
        "gia": df["gia"],
        "trang_thai": trang_thai,
        "nguon": df["nguon"],
    })


def _lam_sach_mot_chuoi(nhom: pd.DataFrame) -> pd.DataFrame:
    """Làm sạch giá của MỘT loại tại MỘT khu vực (một 'chuỗi giá')."""
    nhom = nhom.sort_values("ngay")
    # Nếu một ngày có 2 dòng trùng thì lấy trung bình
    nhom = nhom.groupby("ngay", as_index=False).agg(
        gia=("gia", "mean"), trang_thai=("trang_thai", "first"), nguon=("nguon", "first"))

    # Lưu ý: các dòng "Nghi sai" được GIỮ NGUYÊN giá như trong dataset gốc.

    # 1) Tạo đủ tất cả các ngày từ ngày đầu đến ngày cuối của chuỗi này
    du_ngay = pd.date_range(nhom["ngay"].min(), nhom["ngay"].max(), freq="D")
    nhom = nhom.set_index("ngay").reindex(du_ngay)
    nhom.index.name = "ngay"
    thieu_ngay = nhom["trang_thai"].isna()
    nhom.loc[thieu_ngay, "trang_thai"] = "Điền tự động (thiếu ngày)"
    nhom["nguon"] = nhom["nguon"].ffill()

    # 2) Nội suy: nối thẳng giữa hai ngày có giá; hai đầu thì lấy giá gần nhất
    nhom["gia"] = nhom["gia"].interpolate(method="time").ffill().bfill().round(0)
    return nhom.reset_index()


def doc_du_lieu() -> pd.DataFrame:
    """Đọc 3 file, gộp lại, làm sạch. Trả về một bảng chung (xem đầu file)."""
    phan = [
        _chuan_hoa_lua(_doc_csv(FILE_LUA)),
        _chuan_hoa_ca_phe(_doc_csv(FILE_CA_PHE)),
        _chuan_hoa_ho_tieu(_doc_csv(FILE_HO_TIEU)),
    ]
    df = pd.concat(phan, ignore_index=True)
    df["ngay"] = pd.to_datetime(df["ngay"], errors="coerce")
    df["gia"] = pd.to_numeric(df["gia"], errors="coerce")
    df = df.dropna(subset=["ngay"])

    ket_qua = []
    for (nong_san, loai, khu_vuc), nhom in df.groupby(["nong_san", "loai", "khu_vuc"]):
        sach = _lam_sach_mot_chuoi(nhom)
        sach["nong_san"], sach["loai"], sach["khu_vuc"] = nong_san, loai, khu_vuc
        ket_qua.append(sach)

    return pd.concat(ket_qua, ignore_index=True)[COT_CHUNG]


def doc_gia_the_gioi() -> pd.DataFrame:
    """
    Giá cà phê thế giới theo phiên giao dịch.
    Cột: ngay, robusta (USD/tấn, sàn London), ky_han_robusta, arabica (cent/lb, sàn New York),
         ky_han_arabica, nguon.  Trả về bảng rỗng nếu chưa có file.
    """
    if not (THU_MUC_DATA / FILE_CA_PHE_THE_GIOI).exists():
        return pd.DataFrame(columns=["ngay", "robusta", "ky_han_robusta", "arabica",
                                     "ky_han_arabica", "nguon"])
    df = _doc_csv(FILE_CA_PHE_THE_GIOI).rename(columns={
        "ngay_phien": "ngay", "robusta_london_usd_tan": "robusta", "arabica_ny_cent_lb": "arabica"})
    df["ngay"] = pd.to_datetime(df["ngay"], errors="coerce")
    for cot in ("robusta", "arabica"):
        df[cot] = pd.to_numeric(df[cot], errors="coerce")
    return df.dropna(subset=["ngay"]).sort_values("ngay").reset_index(drop=True)


def doc_gia_tieu_the_gioi() -> pd.DataFrame:
    """
    Giá xuất khẩu hồ tiêu các nước theo IPC (USD/tấn), mỗi ngày mỗi loại một dòng.
    Cột: ngay, quoc_gia, loai, ten (vd. 'Tiêu đen 500 g/l · Việt Nam'), gia, trang_thai, nguon.
    Trả về bảng rỗng nếu chưa có file.
    """
    cot = ["ngay", "quoc_gia", "loai", "ten", "gia", "trang_thai", "nguon"]
    if not (THU_MUC_DATA / FILE_HO_TIEU_THE_GIOI).exists():
        return pd.DataFrame(columns=cot)
    df = _doc_csv(FILE_HO_TIEU_THE_GIOI)
    if "quoc_gia" not in df.columns:
        df["quoc_gia"] = "Việt Nam"
    if "trang_thai" not in df.columns:
        df["trang_thai"] = "Có số liệu"
    df["ngay"] = pd.to_datetime(df["ngay"], errors="coerce")
    df["gia"] = pd.to_numeric(df["gia"], errors="coerce")
    df = df.dropna(subset=["ngay", "gia"])
    df["ten"] = df["loai"].astype(str) + " · " + df["quoc_gia"].astype(str)
    df = df.drop_duplicates(["ngay", "quoc_gia", "loai"], keep="last")
    return df[cot].sort_values(["ngay", "quoc_gia", "loai"]).reset_index(drop=True)


def lay_chuoi_gia(df: pd.DataFrame, nong_san: str, loai: str, khu_vuc: str) -> pd.DataFrame:
    """Lấy bảng giá theo ngày của một lựa chọn cụ thể."""
    chon = (df["nong_san"] == nong_san) & (df["loai"] == loai) & (df["khu_vuc"] == khu_vuc)
    return df[chon].sort_values("ngay").reset_index(drop=True)


if __name__ == "__main__":
    # Chạy thử:  python du_lieu.py
    bang = doc_du_lieu()
    print("Đọc thành công!", len(bang), "dòng.\n")
    tom_tat = bang.groupby(["nong_san", "loai", "khu_vuc"]).agg(
        tu_ngay=("ngay", "min"), den_ngay=("ngay", "max"),
        so_ngay=("ngay", "size"), gia_moi_nhat=("gia", "last"))
    print(tom_tat.to_string())
    print("\nSố dòng theo trạng thái:")
    print(bang["trang_thai"].value_counts().to_string())
