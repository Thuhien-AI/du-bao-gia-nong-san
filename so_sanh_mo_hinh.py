# -*- coding: utf-8 -*-
"""
SO SÁNH 3 MÔ HÌNH DỰ BÁO (Holt · ARIMA · Random Forest) VÀ MÔ HÌNH ĐƯỢC CHỌN

Chạy trong cmd / Terminal (trong thư mục dự án, nhớ bật .venv trước):
    python so_sanh_mo_hinh.py              -> cả 3 nông sản (15 chuỗi giá, khoảng 1–2 phút)
    python so_sanh_mo_hinh.py lua          -> chỉ lúa
    python so_sanh_mo_hinh.py ca-phe       -> chỉ cà phê
    python so_sanh_mo_hinh.py ho-tieu      -> chỉ hồ tiêu

Kết quả:
  - In bảng sai số của 3 mô hình cho từng giống/tỉnh và mô hình được chọn.
  - Lưu toàn bộ bảng vào file  ket_qua_so_sanh_mo_hinh.csv  (mở bằng Excel).
Cách tính giống hệt trang web (dùng chung file du_bao.py).
"""

import sys
import time
from pathlib import Path

import pandas as pd

from du_bao import TEN_MO_HINH, du_bao
from du_lieu import doc_du_lieu, doc_gia_the_gioi, lay_chuoi_gia

FILE_KET_QUA = Path(__file__).parent / "ket_qua_so_sanh_mo_hinh.csv"
LOC = {"lua": "Lúa", "ca-phe": "Cà phê", "caphe": "Cà phê", "ho-tieu": "Hồ tiêu", "hotieu": "Hồ tiêu",
       "tieu": "Hồ tiêu"}
COT = [("1 ngày", "Ngày mai"), ("7 ngày", "7 ngày"), ("30 ngày", "30 ngày"), ("Trung bình", "TB 1-30")]
RONG = 92


def pt(x) -> str:
    return f"{x:.2f}%".replace(".", ",")


def dong_ke(ky="-"):
    print(ky * RONG)


def in_bang(kq):
    """In bảng sai số 3 mô hình + dòng 'Giữ nguyên' cho một chuỗi giá."""
    print(f"  {'Mô hình':<20}" + "".join(f"{ten:>11}" for _, ten in COT))
    print("  " + "-" * (20 + 11 * len(COT)))
    for _, r in kq.so_sanh.iterrows():
        ten = r["Mô hình"]
        nhan = "(Giữ nguyên)" if ten == "Giữ nguyên" else ten
        ghi = ("   <== ĐƯỢC CHỌN" if ten == kq.mo_hinh_chon
               else ("   mốc tham khảo" if ten == "Giữ nguyên" else ""))
        print(f"  {nhan:<20}" + "".join(f"{pt(r[c]):>11}" for c, _ in COT) + ghi)


def in_london(nm):
    """(Cà phê) Sai số dự báo ngày mai có / không có giá London."""
    s = nm.get("sai_so", {})
    if not s:
        return
    print(f"\n  Dự báo NGÀY MAI có thêm giá London (thử trên {nm.get('so_ngay_thu', 0)} ngày):")
    print(f"  {'Mô hình':<20}{'Không London':>15}{'Có London':>13}")
    for ten, khong, co in [("Holt", "Holt", None), ("ARIMA", "ARIMA (không London)", "ARIMA"),
                           ("Random Forest", "Random Forest (không London)", "Random Forest")]:
        ghi = "   <== DÙNG CHO NGÀY MAI" if ten == nm.get("mo_hinh") else ""
        print(f"  {ten:<20}{pt(s[khong]):>15}{(pt(s[co]) if co else '—'):>13}{ghi}")
    if nm.get("dung"):
        print(f"  -> Đang dùng: {nm['mo_hinh']} + giá London (phiên gần nhất "
              f"{nm['london_thay_doi']:+.2f}%)".replace(".", ","))
    else:
        print(f"  -> Chưa dùng giá London cho ngày mai: {nm.get('ly_do', '')}")


def main():
    # hiện đúng tiếng Việt trên cmd của Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    chon_nong_san = None
    if len(sys.argv) > 1:
        chon_nong_san = LOC.get(sys.argv[1].strip().lower())
        if chon_nong_san is None:
            print(f"Không hiểu '{sys.argv[1]}'. Dùng: lua, ca-phe hoặc ho-tieu (hoặc để trống).")
            return

    print("Đang đọc dữ liệu…", flush=True)
    df = doc_du_lieu()
    the_gioi = doc_gia_the_gioi()
    cac_chuoi = df[["nong_san", "loai", "khu_vuc"]].drop_duplicates()
    if chon_nong_san:
        cac_chuoi = cac_chuoi[cac_chuoi["nong_san"] == chon_nong_san]
    cac_chuoi = cac_chuoi.sort_values(["nong_san", "loai", "khu_vuc"]).values.tolist()

    dong_ke("=")
    print(" SO SÁNH 3 MÔ HÌNH DỰ BÁO:  " + "  ·  ".join(TEN_MO_HINH))
    print(f" Dữ liệu đến ngày {df['ngay'].max():%d/%m/%Y} · {len(cac_chuoi)} chuỗi giá")
    print(" Mỗi mô hình 'dự báo lại' nhiều lần trong 6 tháng gần nhất rồi so với giá thật.")
    print(" Số trong bảng = SAI SỐ TRUNG BÌNH (%), càng nhỏ càng tốt. Mô hình có TB 1-30 nhỏ nhất được chọn.")
    dong_ke("=")

    ket_qua, tong_hop = [], []
    t_dau = time.time()
    for i, (ns, loai, kv) in enumerate(cac_chuoi, 1):
        t0 = time.time()
        chuoi = lay_chuoi_gia(df, ns, loai, kv)
        kq = du_bao(chuoi, 30, the_gioi if ns == "Cà phê" else None)
        print(f"\n[{i}/{len(cac_chuoi)}] {ns.upper()} · {loai} · {kv}")
        print(f"  Số liệu: {chuoi['ngay'].min():%d/%m/%Y} – {chuoi['ngay'].max():%d/%m/%Y} · "
              f"thử lại {kq.so_lan_kiem_tra} lần · {time.time() - t0:.1f} giây")
        in_bang(kq)
        print(f"  => Mô hình được chọn: {kq.mo_hinh_chon} ({kq.mo_ta_tham_so})")
        if ns == "Cà phê":
            in_london(kq.ngay_mai)
        sys.stdout.flush()

        for _, r in kq.so_sanh.iterrows():
            ket_qua.append({
                "Nông sản": ns, "Giống / loại": loai, "Khu vực": kv, "Mô hình": r["Mô hình"],
                "Sai số ngày mai (%)": round(r["1 ngày"], 3), "Sai số 7 ngày (%)": round(r["7 ngày"], 3),
                "Sai số 30 ngày (%)": round(r["30 ngày"], 3), "Sai số TB 1-30 ngày (%)": round(r["Trung bình"], 3),
                "Được chọn": "Có" if r["Mô hình"] == kq.mo_hinh_chon else "",
            })
        tb = kq.so_sanh.set_index("Mô hình")["Trung bình"]
        tong_hop.append((ns, loai, kv, kq.mo_hinh_chon, tb[kq.mo_hinh_chon], tb["Giữ nguyên"],
                         kq.ngay_mai.get("mo_hinh", "") if ns == "Cà phê" else ""))

    # ---- Bảng tổng hợp
    print()
    dong_ke("=")
    print(" TỔNG HỢP: MÔ HÌNH ĐƯỢC CHỌN CHO TỪNG CHUỖI GIÁ")
    dong_ke("=")
    print(f" {'Nông sản':<9}{'Giống / loại':<22}{'Khu vực':<30}{'Được chọn':<15}{'Sai số TB':>10}{'Giữ nguyên':>12}")
    dong_ke()
    for ns, loai, kv, mh, s_mh, s_gn, nm in tong_hop:
        print(f" {ns:<9}{loai[:21]:<22}{kv[:29]:<30}{mh:<15}{pt(s_mh):>10}{pt(s_gn):>12}")
    dong_ke()
    dem = pd.Series([t[3] for t in tong_hop]).value_counts()
    print(" Số lần được chọn: " + " · ".join(f"{ten}: {int(dem.get(ten, 0))}" for ten in TEN_MO_HINH))
    nm_cp = [t[6] for t in tong_hop if t[0] == "Cà phê" and t[6]]
    if nm_cp:
        dem_nm = pd.Series(nm_cp).value_counts()
        print(" Cà phê – mô hình cho NGÀY MAI (có giá London): "
              + " · ".join(f"{k}: {v}" for k, v in dem_nm.items()))

    pd.DataFrame(ket_qua).to_csv(FILE_KET_QUA, index=False, encoding="utf-8-sig")
    print(f"\n Đã lưu bảng chi tiết vào: {FILE_KET_QUA.name}  (mở bằng Excel)")
    print(f" Tổng thời gian: {time.time() - t_dau:.0f} giây")


if __name__ == "__main__":
    main()
