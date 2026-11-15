# -*- coding: utf-8 -*-
"""
Phân tích giá tự động (mục "AI phân tích giá"), phát hiện biến động giá và tạo báo cáo tải về.

"AI phân tích giá" ở đây là phần NHẬN ĐỊNH TỰ ĐỘNG BẰNG LỜI, viết ra từ:
  - diễn biến giá thật (7, 30, 90 ngày gần nhất),
  - kết quả 3 mô hình dự báo (Holt, ARIMA, Random Forest) và sai số kiểm tra ngược,
  - giá cà phê thế giới (London) với cà phê.
Không gọi dịch vụ bên ngoài, không gửi dữ liệu đi đâu. Lời văn luôn trung lập:
chỉ mô tả và tham khảo, không khuyên mua/bán.
"""

import html as _html

import numpy as np
import pandas as pd


def _so(x) -> str:
    return f"{x:,.0f}".replace(",", ".")


def _pt(x) -> str:
    return f"{x:+.1f}%".replace(".", ",")


def _ps(x) -> str:
    return f"±{x:.1f}%".replace(".", ",")


def _doi(chuoi: pd.DataFrame, so_ngay: int):
    """% thay đổi so với giá cách đây `so_ngay` ngày (None nếu chưa đủ dữ liệu)."""
    cuoi = chuoi["ngay"].iloc[-1]
    truoc = chuoi[chuoi["ngay"] <= cuoi - pd.Timedelta(days=so_ngay)]
    if truoc.empty:
        return None
    g0 = truoc["gia"].iloc[-1]
    return (chuoi["gia"].iloc[-1] - g0) / g0 * 100


def _xu_huong(pt) -> str:
    if pt is None:
        return "chưa đủ dữ liệu"
    if abs(pt) < 0.5:
        return "gần như đi ngang"
    if pt > 0:
        return "tăng mạnh" if pt >= 5 else "tăng nhẹ"
    return "giảm mạnh" if pt <= -5 else "giảm nhẹ"


# ================================================================ AI phân tích giá
def phan_tich_gia(ten: str, chuoi: pd.DataFrame, kq, so_ngay_du_bao: int = 30, the_gioi: pd.DataFrame = None) -> list:
    """
    Trả về danh sách (tiêu đề, nội dung) — mỗi mục 1–2 câu tiếng Việt dễ hiểu.
    so_ngay_du_bao: số ngày dự báo người dùng được xem (để không lộ phần bị khoá).
    """
    gia = chuoi["gia"].iloc[-1]
    d7, d30, d90 = _doi(chuoi, 7), _doi(chuoi, 30), _doi(chuoi, 90)
    muc = []

    # 1. Xu hướng gần đây
    cau = f"Giá {ten} hiện ở mức {_so(gia)} đ/kg, {_xu_huong(d7)} trong 7 ngày"
    if d7 is not None:
        cau += f" ({_pt(d7)})"
    if d30 is not None:
        cau += f" và {_xu_huong(d30)} trong 30 ngày ({_pt(d30)})"
    muc.append(("Xu hướng gần đây", cau + "."))

    # 2. Vị trí so với 90 ngày
    g90 = chuoi[chuoi["ngay"] > chuoi["ngay"].iloc[-1] - pd.Timedelta(days=90)]["gia"]
    if len(g90) >= 20 and g90.max() > g90.min():
        vi_tri = (gia - g90.min()) / (g90.max() - g90.min()) * 100
        if vi_tri >= 85:
            nhan = "đang ở vùng CAO NHẤT của 3 tháng qua"
        elif vi_tri <= 15:
            nhan = "đang ở vùng THẤP NHẤT của 3 tháng qua"
        else:
            nhan = f"nằm khoảng {vi_tri:.0f}% của khoảng giá 3 tháng qua"
        muc.append(("So với 3 tháng qua",
                    f"Giá {nhan} (thấp nhất {_so(g90.min())} đ, cao nhất {_so(g90.max())} đ)."))

    # 3. Độ biến động
    loi_suat = chuoi["gia"].pct_change().dropna().tail(30)
    if len(loi_suat) >= 10:
        bd = loi_suat.std() * 100
        so_ngay_doi = int((loi_suat.abs() > 1e-9).sum())
        if bd < 0.4:
            m = "rất ổn định"
        elif bd < 1.2:
            m = "dao động vừa phải"
        else:
            m = "biến động mạnh"
        muc.append(("Mức dao động",
                    f"30 phiên gần nhất giá {m}: trung bình mỗi phiên lệch khoảng {_ps(bd)}"
                    + f", có {so_ngay_doi}/{len(loi_suat)} phiên giá thay đổi."))

    # 4. Dự báo (chỉ trong phạm vi được xem)
    if so_ngay_du_bao >= 7:
        n = min(so_ngay_du_bao, 30)
        dong = kq.bang.iloc[n - 1]
        pt_db = (dong["du_bao"] - gia) / gia * 100
        cau = (f"Mô hình {kq.mo_hinh_chon} dự báo sau {n} ngày giá {_xu_huong(pt_db)}, quanh "
               f"{_so(dong['du_bao'])} đ/kg ({_pt(pt_db)}); khoảng có thể {_so(dong['thap'])} – {_so(dong['cao'])} đ.")
        rong = (dong["cao"] - dong["thap"]) / gia * 100
        if rong > 8:
            cau += " Khoảng dao động khá rộng nên độ chắc chắn không cao."
        muc.append((f"Dự báo {n} ngày tới", cau))

    # 5. Độ tin cậy của mô hình
    try:
        sai = float(kq.sai_so_theo_ngay[6])
        giu = float(kq.giu_nguyen_theo_ngay[6])
        if sai < giu * 0.95:
            cau = (f"Khi kiểm tra trên dữ liệu cũ, mô hình đoán 7 ngày tới sai khoảng {_ps(sai)}, sát hơn cách đoán "
                   f"\"giá giữ nguyên\" ({_ps(giu)}).")
        else:
            cau = (f"Khi kiểm tra trên dữ liệu cũ, mô hình đoán 7 ngày tới sai khoảng {_ps(sai)}, chỉ ngang cách đoán "
                   f"\"giá giữ nguyên\" ({_ps(giu)}) — nên xem dự báo như một tham khảo về xu hướng.")
        muc.append(("Độ tin cậy", cau))
    except Exception:
        pass

    # 6. Cà phê: liên hệ giá London
    if the_gioi is not None and not the_gioi.empty and "robusta" in the_gioi:
        r = the_gioi.dropna(subset=["robusta"]).sort_values("ngay")
        if len(r) >= 2:
            pt_l = (r["robusta"].iloc[-1] - r["robusta"].iloc[-2]) / r["robusta"].iloc[-2] * 100
            muc.append(("Giá thế giới",
                        f"Robusta London phiên {r['ngay'].iloc[-1]:%d/%m} {_xu_huong(pt_l)} ({_pt(pt_l)}), "
                        f"đạt {_so(r['robusta'].iloc[-1])} USD/tấn. Giá trong nước thường phản ánh biến động này "
                        "vào sáng hôm sau."))

    muc.append(("Lưu ý", "Nhận định được tạo tự động từ số liệu, chỉ để tham khảo."))
    return muc


# ================================================================ Biến động giá (thông báo)
def bien_dong(df: pd.DataFrame, nguong: float = 1.0, toi_da: int = 8) -> list:
    """
    So sánh phiên mới nhất với phiên trước của từng loại/khu vực.
    Trả về các thay đổi có |%| >= nguong, lớn nhất trước:
    [{nong_san, loai, khu_vuc, ngay, gia, gia_truoc, pt}]
    """
    kq = []
    for (ns, loai, kv), g in df.groupby(["nong_san", "loai", "khu_vuc"]):
        g = g.sort_values("ngay")
        if len(g) < 2 or g["ngay"].iloc[-1] < df.loc[df["nong_san"] == ns, "ngay"].max():
            continue
        a, b = g["gia"].iloc[-2], g["gia"].iloc[-1]
        if a and abs((b - a) / a * 100) >= nguong:
            kq.append({"nong_san": ns, "loai": loai, "khu_vuc": kv, "ngay": g["ngay"].iloc[-1],
                       "gia": b, "gia_truoc": a, "pt": (b - a) / a * 100})
    return sorted(kq, key=lambda x: -abs(x["pt"]))[:toi_da]


# ================================================================ Báo cáo tải về (gói Đại Điền)
def bao_cao_html(ten_app: str, nong_san: str, loai: str, khu_vuc: str, chuoi: pd.DataFrame, kq,
                 cac_muc_phan_tich: list, nguoi_nhan: str) -> bytes:
    """Báo cáo 1 trang HTML (mở bằng trình duyệt, bấm Ctrl+P để lưu PDF)."""
    e = lambda x: _html.escape(str(x))
    gia = chuoi["gia"].iloc[-1]
    ngay = chuoi["ngay"].iloc[-1]
    bang = "".join(
        f"<tr><td>{r.ngay:%d/%m/%Y}</td><td class=p>{_so(r.du_bao)}</td>"
        f"<td class=p>{_pt((r.du_bao - gia) / gia * 100)}</td><td class=p>{_so(r.thap)} – {_so(r.cao)}</td></tr>"
        for r in kq.bang.itertuples())
    lich_su = "".join(f"<tr><td>{r.ngay:%d/%m/%Y}</td><td class=p>{_so(r.gia)}</td></tr>"
                      for r in chuoi.tail(14).iloc[::-1].itertuples())
    pt = "".join(f"<li><b>{e(t)}:</b> {e(c)}</li>" for t, c in cac_muc_phan_tich)
    # biểu đồ nhỏ 90 ngày + 30 ngày dự báo (SVG tự vẽ)
    g = chuoi.tail(90)
    ys = list(g["gia"]) + list(kq.bang["du_bao"])
    lo, hi = min(ys + list(kq.bang["thap"])), max(ys + list(kq.bang["cao"]))
    W, H, n = 680, 180, len(ys)
    X = lambda i: 10 + i * (W - 20) / max(n - 1, 1)
    Y = lambda v: H - 10 - (v - lo) / max(hi - lo, 1) * (H - 20)
    duong = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(g["gia"]))
    duong_db = " ".join(f"{X(len(g) - 1 + i):.1f},{Y(v):.1f}" for i, v in enumerate([gia] + list(kq.bang["du_bao"])))
    vung = (" ".join(f"{X(len(g) + i):.1f},{Y(v):.1f}" for i, v in enumerate(kq.bang["cao"])) + " "
            + " ".join(f"{X(len(g) + i):.1f},{Y(v):.1f}" for i, v in reversed(list(enumerate(kq.bang["thap"])))))
    svg = (f'<svg viewBox="0 0 {W} {H}" width="100%"><polygon points="{vung}" fill="rgba(232,116,59,.15)"/>'
           f'<polyline points="{duong}" fill="none" stroke="#1B7F3B" stroke-width="2.4"/>'
           f'<polyline points="{duong_db}" fill="none" stroke="#E8743B" stroke-width="2.2" stroke-dasharray="6 4"/></svg>')
    ma = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"><title>Báo cáo giá {e(loai)} – {e(khu_vuc)}</title>
<style>body{{font-family:'Segoe UI',Arial,sans-serif;color:#1F1A17;max-width:760px;margin:30px auto;padding:0 20px}}
h1{{font-size:24px;margin:0;color:#2F6B22}} .phu{{color:#6B625C;font-size:13px;margin:4px 0 18px}}
.o{{display:inline-block;border:1px solid #EFE7E1;border-radius:12px;padding:10px 16px;margin:0 8px 8px 0}}
.o b{{display:block;font-size:20px}} h2{{font-size:16px;border-bottom:2px solid #2F6B22;padding-bottom:4px;margin-top:24px}}
table{{border-collapse:collapse;width:100%;font-size:13px}} td,th{{border-bottom:1px solid #EFE7E1;padding:5px 8px;text-align:left}}
th{{background:#F1F7EC}} .p{{text-align:right}} li{{margin:6px 0;line-height:1.5;font-size:14px}}
.chan{{color:#6B625C;font-size:12px;margin-top:24px;border-top:1px solid #EFE7E1;padding-top:8px}}
@media print{{body{{margin:0}}}}</style></head><body>
<h1>Báo cáo giá {e(nong_san.lower())} · {e(loai)} · {e(khu_vuc)}</h1>
<div class="phu">{e(ten_app)} · Gói VIP Đại Điền · Lập ngày {pd.Timestamp.now():%d/%m/%Y %H:%M} cho {e(nguoi_nhan)}</div>
<div class="o">Giá ngày {ngay:%d/%m/%Y}<b>{_so(gia)} đ/kg</b></div>
<div class="o">Ngày mai<b>{_so(kq.bang['du_bao'].iloc[0])} đ</b></div>
<div class="o">7 ngày tới<b>{_so(kq.bang['du_bao'].iloc[6])} đ</b></div>
<div class="o">30 ngày tới<b>{_so(kq.bang['du_bao'].iloc[29])} đ</b></div>
<h2>Biểu đồ 90 ngày và dự báo 30 ngày</h2>{svg}
<div class="phu">Đường xanh: giá thật · Nét đứt cam: dự báo · Vùng cam: khoảng có thể (90%)</div>
<h2>Phân tích</h2><ul>{pt}</ul>
<h2>Bảng dự báo 30 ngày (mô hình {e(kq.mo_hinh_chon)})</h2>
<table><tr><th>Ngày</th><th class=p>Giá dự báo (đ/kg)</th><th class=p>So với hiện tại</th><th class=p>Khoảng có thể</th></tr>{bang}</table>
<h2>Giá 14 phiên gần nhất</h2><table><tr><th>Ngày</th><th class=p>Giá (đ/kg)</th></tr>{lich_su}</table>
<div class="chan">Số liệu và dự báo chỉ mang tính tham khảo.
Mẹo: bấm Ctrl + P → "Lưu dưới dạng PDF" để có file PDF.</div></body></html>"""
    return ma.encode("utf-8")
