# -*- coding: utf-8 -*-
"""
Trợ lý AI Bồ Nông: chatbot trả lời câu hỏi về giá nông sản.

CÁCH HOẠT ĐỘNG
  1. Gom số liệu THẬT trong web (giá hôm nay mọi giống/tỉnh, diễn biến, dự báo, độ tin cậy mô hình,
     giá thế giới, nhận định tự động) thành một "bản tóm tắt dữ liệu".
  2. Gửi bản tóm tắt + câu hỏi tới Google Gemini (gói miễn phí) để viết câu trả lời dễ hiểu.
  3. Chưa có khoá API / Gemini lỗi / hết lượt -> trả lời bằng nhận định tự động có sẵn (không cần mạng).

KHOÁ API (không bao giờ ghi khoá vào code):
  Mở file .streamlit/secrets.toml và điền:
      GEMINI_API_KEY = "khoá-của-bạn"
  Lấy khoá miễn phí tại https://aistudio.google.com (mục Get API key).
  Có thể đổi mô hình:  GEMINI_MODEL = "gemini-flash-latest"

Chỉ gửi số liệu giá và câu hỏi; không gửi tên, email hay thông tin tài khoản.
"""

import json
import os
import urllib.error
import urllib.request

import pandas as pd

MO_HINH_MAC_DINH = "gemini-flash-latest"
MO_HINH_DU_PHONG = ["gemini-flash-lite-latest", "gemini-2.5-flash"]
URL = "https://generativelanguage.googleapis.com/v1beta/models/{mo_hinh}:generateContent"
SO_LUOT_NGAY = {2: 20, 3: 50}          # số câu hỏi mỗi ngày theo hạng gói (Bội Thu, Đại Điền/Nhóm)

HUONG_DAN = """Bạn là "Trợ lý Bồ Nông", trợ lý về giá nông sản Việt Nam (lúa, cà phê, hồ tiêu) trong ứng dụng Bồ Nông.
Quy tắc:
- Luôn trả lời bằng tiếng Việt, giọng gần gũi, dễ hiểu với nông dân; ngắn gọn (thường dưới 180 chữ), dùng gạch đầu dòng khi liệt kê.
- Ưu tiên dùng SỐ LIỆU trong phần "DỮ LIỆU BỒ NÔNG" bên dưới; ghi rõ ngày của số liệu. Đơn vị giá trong nước là đồng/kg.
- Không bịa số liệu. Nếu dữ liệu không có thông tin cần thiết, nói rõ là ứng dụng chưa có số liệu đó; có thể giải thích kiến thức chung về nông nghiệp nhưng phải nói đó là thông tin chung.
- Dự báo chỉ để tham khảo: không khẳng định chắc chắn giá sẽ lên/xuống, không khuyên mua/bán/tích trữ cụ thể; có thể nêu các yếu tố người dùng nên cân nhắc.
- Chỉ dùng phần dự báo có trong dữ liệu; nếu người dùng hỏi mốc dự báo không có, nói rằng mốc đó cần gói VIP cao hơn.
- Không tự nhắc tên mô hình hay công ty cung cấp AI. Nếu được hỏi trực tiếp bạn là ai, nói bạn là Trợ lý Bồ Nông, dùng một mô hình AI bên ngoài để soạn câu trả lời từ số liệu của ứng dụng.
- Từ chối lịch sự các câu hỏi không liên quan đến nông nghiệp, giá cả, thời tiết mùa vụ hay cách dùng ứng dụng."""


# ================================================================ Khoá & cấu hình
def doc_cau_hinh(secrets=None):
    """(khoá API, tên mô hình). Khoá đọc từ .streamlit/secrets.toml hoặc biến môi trường GEMINI_API_KEY."""
    khoa, mo_hinh = "", MO_HINH_MAC_DINH
    try:
        if secrets is not None:
            khoa = str(secrets.get("GEMINI_API_KEY", "") or "")
            mo_hinh = str(secrets.get("GEMINI_MODEL", "") or mo_hinh)
    except Exception:
        pass
    khoa = khoa or os.environ.get("GEMINI_API_KEY", "")
    return khoa.strip(), mo_hinh.strip()


# ================================================================ Bản tóm tắt dữ liệu gửi kèm
def _so(x) -> str:
    return f"{x:,.0f}".replace(",", ".")


def ngu_canh(df, nong_san, loai, khu_vuc, chuoi, kq, so_ngay_du_bao, nhan_dinh, the_gioi=None, tieu_the_gioi=None,
             ten_goi="") -> str:
    """Tạo bản tóm tắt số liệu (dạng chữ) để AI đọc. Chỉ đưa dự báo trong phạm vi gói được xem."""
    d = [f"Hôm nay: {pd.Timestamp.now():%d/%m/%Y}. Người dùng đang dùng gói: {ten_goi}.",
         f"Đang xem: {nong_san} · {loai} · {khu_vuc}."]

    # 1. Diễn biến 14 phiên gần nhất của lựa chọn hiện tại
    gan = chuoi.tail(14)
    d.append("Giá 14 phiên gần nhất (đồng/kg): " + "; ".join(f"{r.ngay:%d/%m} {_so(r.gia)}" for r in gan.itertuples()))
    g90 = chuoi[chuoi["ngay"] > chuoi["ngay"].iloc[-1] - pd.Timedelta(days=90)]["gia"]
    d.append(f"90 ngày qua: thấp nhất {_so(g90.min())}, cao nhất {_so(g90.max())}, trung bình {_so(g90.mean())}.")

    # 2. Dự báo (chỉ phần được xem)
    moc = [1] + [m for m in (7, 30) if m <= so_ngay_du_bao]
    dong = []
    for m in moc:
        r = kq.bang.iloc[m - 1]
        dong.append(f"{'ngày mai' if m == 1 else f'{m} ngày tới'} ({r['ngay']:%d/%m}): {_so(r['du_bao'])} "
                    f"(khoảng có thể {_so(r['thap'])}–{_so(r['cao'])})")
    d.append(f"Dự báo của mô hình {kq.mo_hinh_chon}: " + "; ".join(dong) + ".")
    if so_ngay_du_bao < 30:
        d.append("Gói hiện tại KHÔNG được xem dự báo "
                 + ("7 và 30 ngày." if so_ngay_du_bao < 7 else "30 ngày."))
    try:
        d.append(f"Sai số kiểm tra ngược: ngày mai ±{kq.sai_so_theo_ngay[0]:.1f}%, 7 ngày ±{kq.sai_so_theo_ngay[6]:.1f}% "
                 f"(cách đoán 'giá giữ nguyên': ±{kq.giu_nguyen_theo_ngay[0]:.1f}% và ±{kq.giu_nguyen_theo_ngay[6]:.1f}%).")
    except Exception:
        pass

    # 3. Nhận định tự động
    d.append("Nhận định tự động: " + " ".join(f"[{t}] {c}" for t, c in nhan_dinh if t != "Lưu ý"))

    # 4. Giá mới nhất mọi giống / tỉnh trong ứng dụng
    bang = []
    for (ns, l, kv), g in df.groupby(["nong_san", "loai", "khu_vuc"]):
        g = g.sort_values("ngay")
        truoc = g["gia"].iloc[-2] if len(g) > 1 else g["gia"].iloc[-1]
        bang.append(f"{ns} | {l} | {kv} | ngày {g['ngay'].iloc[-1]:%d/%m} | {_so(g['gia'].iloc[-1])} "
                    f"({(g['gia'].iloc[-1] - truoc) / truoc * 100:+.1f}% so với phiên trước)")
    d.append("GIÁ MỚI NHẤT TRONG ỨNG DỤNG (nông sản | giống | khu vực | ngày | giá đồng/kg):\n" + "\n".join(bang))

    # 5. Giá thế giới
    if the_gioi is not None and not the_gioi.empty:
        r = the_gioi.dropna(subset=["robusta"]).sort_values("ngay").tail(1)
        a = the_gioi.dropna(subset=["arabica"]).sort_values("ngay").tail(1)
        if not r.empty:
            d.append(f"Cà phê thế giới: Robusta London {_so(r['robusta'].iloc[0])} USD/tấn (phiên {r['ngay'].iloc[0]:%d/%m})"
                     + (f"; Arabica New York {a['arabica'].iloc[0]:.2f} cent/lb (phiên {a['ngay'].iloc[0]:%d/%m})"
                        if not a.empty else "") + ".")
    if tieu_the_gioi is not None and not tieu_the_gioi.empty:
        moi = tieu_the_gioi[tieu_the_gioi["ngay"] == tieu_the_gioi["ngay"].max()]
        d.append(f"Hồ tiêu thế giới (IPC, USD/tấn FOB, ngày {moi['ngay'].max():%d/%m}): "
                 + "; ".join(f"{r.quoc_gia} {r.loai} {_so(r.gia)}" for r in moi.itertuples()))
    d.append("Nguồn số liệu trong nước: báo giá hằng ngày từ Báo Hà Tĩnh và Báo Lâm Đồng; dự báo bằng 3 mô hình "
             "Holt, ARIMA, Random Forest (chọn mô hình sai số nhỏ nhất khi kiểm tra ngược).")
    return "\n".join(d)


# ================================================================ Gọi Gemini
class LoiAI(Exception):
    pass


def _goi(mo_hinh: str, khoa: str, than: dict, het_gio: int = 30) -> str:
    req = urllib.request.Request(URL.format(mo_hinh=mo_hinh), data=json.dumps(than).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": khoa})
    with urllib.request.urlopen(req, timeout=het_gio) as r:
        kq = json.loads(r.read().decode("utf-8"))
    ung_vien = kq.get("candidates") or []
    if not ung_vien:
        ly_do = (kq.get("promptFeedback") or {}).get("blockReason", "không có câu trả lời")
        raise LoiAI("Trợ lý AI chưa trả lời được câu này.")
    chu = "".join(p.get("text", "") for p in (ung_vien[0].get("content") or {}).get("parts", []))
    if not chu.strip():
        raise LoiAI("Trợ lý AI chưa trả lời được câu này.")
    return chu.strip()


def hoi_gemini(cau_hoi: str, lich_su: list, du_lieu: str, khoa: str, mo_hinh: str = MO_HINH_MAC_DINH) -> str:
    """lich_su: [{"role": "user"|"assistant", "content": ...}] (các lượt trước). Trả về câu trả lời (markdown)."""
    noi_dung = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
                for m in lich_su[-8:]]
    noi_dung.append({"role": "user", "parts": [{"text": cau_hoi}]})
    than = {"systemInstruction": {"parts": [{"text": HUONG_DAN + "\n\nDỮ LIỆU BỒ NÔNG:\n" + du_lieu}]},
            "contents": noi_dung,
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 900}}
    loi_cuoi = None
    for mh in [mo_hinh] + [m for m in MO_HINH_DU_PHONG if m != mo_hinh]:
        try:
            return _goi(mh, khoa, than)
        except urllib.error.HTTPError as loi:
            if loi.code in (400, 401, 403):
                raise LoiAI("Trợ lý AI đang tạm ngưng.")
            loi_cuoi = LoiAI("Trợ lý AI đang quá tải, hãy thử lại sau ít phút." if loi.code == 429
                             else "Trợ lý AI đang gặp sự cố.")
            if loi.code not in (404, 429, 500, 503):
                break
        except urllib.error.URLError:
            raise LoiAI("Không kết nối được tới trợ lý AI (kiểm tra mạng Internet).")
        except TimeoutError:
            loi_cuoi = LoiAI("Trợ lý AI trả lời quá lâu.")
    raise loi_cuoi or LoiAI("Trợ lý AI đang gặp sự cố.")


def tra_loi_du_phong(cau_hoi: str, nhan_dinh: list, ly_do: str = "") -> str:
    """Khi không gọi được Gemini: trả lời bằng nhận định tự động có sẵn."""
    dau = (f"_{ly_do} Dưới đây là nhận định tự động từ số liệu của Bồ Nông:_\n\n" if ly_do
           else "_Dưới đây là nhận định tự động từ số liệu của Bồ Nông:_\n\n")
    return dau + "\n".join(f"- **{t}:** {c}" for t, c in nhan_dinh)


def cau_hoi_goi_y(ten: str, nong_san: str) -> list:
    g = [f"Giá {ten} tuần tới có xu hướng thế nào?", f"Hôm nay tỉnh nào có giá {ten} cao nhất?",
         "Vì sao dự báo có khoảng dao động rộng?"]
    if nong_san == "Cà phê":
        g[2] = "Giá Robusta London đang ảnh hưởng thế nào tới giá trong nước?"
    elif nong_san == "Hồ tiêu":
        g[2] = "Giá tiêu Việt Nam so với các nước khác ra sao?"
    return g
