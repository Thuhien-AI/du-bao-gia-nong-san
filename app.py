# Ứng dụng dự báo giá nông sản Việt Nam
# File chính của trang web. Chạy bằng lệnh:  streamlit run app.py
#
# Bố cục:
#   1. Trang đầu    : logo + 3 thẻ Lúa / Cà phê / Hồ tiêu để khách chọn
#   2. Trang kết quả: 4 ô giá · 3 ô dự báo · biểu đồ 7/30/90 ngày · bảng so sánh · chi tiết
# Phần vẽ ô / bảng / màu sắc nằm trong file giao_dien.py

import base64
import io
from urllib.parse import urlencode
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

import importlib

import giao_dien as gd

gd = importlib.reload(gd)   # luôn nạp bản giao diện mới nhất mỗi lần chạy lại (không cần tắt web)
from cap_nhat_gia import can_cap_nhat, cap_nhat_tat_ca, doc_trang_thai
from du_bao import du_bao
from du_lieu import CAC_FILE, doc_du_lieu, doc_gia_the_gioi, doc_gia_tieu_the_gioi, lay_chuoi_gia
import xac_thuc as xt
import vi_xu as vx
import phan_tich as pt
import tro_ly_ai as ai
import nong_trai as nt
import dien_dan as dd

xt = importlib.reload(xt)
vx = importlib.reload(vx)
pt = importlib.reload(pt)
ai = importlib.reload(ai)
nt = importlib.reload(nt)
dd = importlib.reload(dd)

THU_MUC = Path(__file__).parent
FILE_LOGO = THU_MUC / "image" / "iconapp.png"
FILE_LOGO_CHU = THU_MUC / "image" / "logo.png"
TEN_APP = "Dự báo giá nông sản Việt Nam"

NONG_SAN = {
    "Lúa": "Lúa tươi tại ruộng · An Giang (ĐBSCL)",
    "Cà phê": "Robusta nhân xô · Tây Nguyên",
    "Hồ tiêu": "Tiêu đen · Tây Nguyên & Đông Nam Bộ",
}
TEN_NGAN = {"Lúa": "lúa", "Cà phê": "cà phê", "Hồ tiêu": "tiêu"}
MOC_DU_BAO = [(1, "Ngày mai"), (7, "7 ngày tới"), (30, "30 ngày tới")]


# ================================================================ Cài đặt trang
def _anh_logo():
    try:
        return Image.open(FILE_LOGO)
    except Exception:
        return "🌾"


st.set_page_config(page_title=TEN_APP, page_icon=_anh_logo(), layout="wide",
                   initial_sidebar_state="collapsed")
try:
    xt.dam_bao_quan_tri()      # tạo tài khoản "admin" của diễn đàn nếu chưa có
except Exception:
    pass


@st.cache_data
def logo_base64(kich_thuoc: int = 200) -> str:
    """Thu nhỏ logo và đổi sang dạng chữ để chèn vào trang."""
    if not FILE_LOGO.exists():
        return ""
    anh = Image.open(FILE_LOGO).convert("RGB")
    anh.thumbnail((kich_thuoc, kich_thuoc))
    bo_dem = io.BytesIO()
    anh.save(bo_dem, format="PNG")
    return base64.b64encode(bo_dem.getvalue()).decode()


@st.cache_data
def logo_chu_base64(rong: int = 760) -> str:
    """
    Logo chữ 'Bồ Nông': xoá các chấm mờ lấm tấm quanh chữ (do tách nền), cắt sát chữ, thu nhỏ.
    File gốc trong thư mục image/ không bị thay đổi.
    """
    if not FILE_LOGO_CHU.exists():
        return ""
    from PIL import ImageChops, ImageFilter
    anh = Image.open(FILE_LOGO_CHU).convert("RGBA")
    alpha = anh.getchannel("A")
    mat_na = alpha.point(lambda v: 255 if v >= 90 else 0)
    mat_na = mat_na.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    anh.putalpha(ImageChops.multiply(alpha, mat_na.filter(ImageFilter.MaxFilter(3))))
    khung = mat_na.getbbox()
    if khung:
        anh = anh.crop((max(khung[0] - 10, 0), max(khung[1] - 10, 0),
                        min(khung[2] + 10, anh.width), min(khung[3] + 10, anh.height)))
    anh.thumbnail((rong, rong))
    bo_dem = io.BytesIO()
    anh.save(bo_dem, format="PNG")
    return base64.b64encode(bo_dem.getvalue()).decode()


def html(ma: str):
    st.markdown(gd.gon(ma), unsafe_allow_html=True)


# ================================================================ Dữ liệu & cập nhật
def dau_vet_du_lieu():
    """Thời điểm sửa của 3 file CSV: file đổi (vừa cập nhật giá) -> web tự đọc lại."""
    return tuple((THU_MUC / "data" / f).stat().st_mtime if (THU_MUC / "data" / f).exists() else 0
                 for f in CAC_FILE)


@st.cache_data
def tai_du_lieu(dau_vet):
    return doc_du_lieu()


@st.cache_data
def tai_the_gioi(dau_vet):
    return doc_gia_the_gioi()


@st.cache_data
def tai_tieu_the_gioi(dau_vet):
    return doc_gia_tieu_the_gioi()


# persist="disk": lưu kết quả ra ổ đĩa -> tắt/mở lại web không phải tính lại
@st.cache_data(persist="disk", show_spinner="Đang chạy 3 mô hình và chọn mô hình tốt nhất…")
def tinh_du_bao(nong_san, loai, khu_vuc, dau_vet):
    the_gioi = tai_the_gioi(dau_vet) if nong_san == "Cà phê" else None
    return du_bao(lay_chuoi_gia(tai_du_lieu(dau_vet), nong_san, loai, khu_vuc), 30, the_gioi)


def chay_cap_nhat():
    with st.spinner("Đang lấy giá mới nhất từ Báo Hà Tĩnh…"):
        st.session_state.bao_cao_cap_nhat = cap_nhat_tat_ca()


def khu_cap_nhat(df):
    """Dòng 'Số liệu mới nhất … · cập nhật lần cuối …' + nút cập nhật."""
    lan_cuoi = doc_trang_thai().get("lan_cuoi")
    chu = f" · Tự cập nhật lần cuối: {pd.Timestamp(lan_cuoi):%H:%M %d/%m/%Y}" if lan_cuoi else ""
    trai, phai = st.columns([4, 1.3], vertical_alignment="center")
    trai.caption(f"📅 Số liệu mới nhất: ngày {df['ngay'].max():%d/%m/%Y}{chu}")
    if phai.button("🔄 Cập nhật giá ngay", width="stretch"):
        chay_cap_nhat()
        st.rerun()
    for dong in st.session_state.pop("bao_cao_cap_nhat", []):
        (st.warning if dong.startswith("⚠️") else st.success)(dong)


def chan_trang():
    html(f"""<div class="chan-trang">© {pd.Timestamp.today().year} · {TEN_APP} ·
    Số liệu chỉ mang tính tham khảo.</div>""")


# ================================================================ ĐĂNG NHẬP / ĐĂNG KÝ
TEN_COOKIE = "bo_nong_ve"
SO_LAN_SAI_TOI_DA = 5


def ghi_cookie(gia_tri: str, so_giay: int):
    """Lưu 'vé đăng nhập' vào trình duyệt để tải lại trang vẫn còn đăng nhập."""
    components.html(
        f"<script>window.parent.document.cookie = '{TEN_COOKIE}={gia_tri}; path=/; "
        f"max-age={so_giay}; SameSite=Lax';</script>", height=0)


# Lần đầu mở trang: thử đăng nhập lại bằng vé lưu trong trình duyệt.
# - Chạy trên máy: đọc thẳng cookie (st.context.cookies).
# - Trên Streamlit Cloud, máy chủ trung gian xoá cookie, nên một đoạn JavaScript nhỏ (cau_noi_ve) đọc vé
#   trong trình duyệt rồi gửi lên qua địa chỉ (?ve=...). App đọc xong xoá ngay khỏi địa chỉ.
if "nguoi_dung" not in st.session_state:
    try:
        ve_cu = st.context.cookies.get(TEN_COOKIE)
    except Exception:
        ve_cu = None
    ve_url = st.query_params.get("ve")
    if ve_url:
        st.query_params.pop("ve", None)
        st.session_state.da_thu_ve_url = True
    nd = xt.nguoi_dung_tu_ve(ve_cu)
    ve_dung = ve_cu if nd else None
    if not nd and ve_url:
        nd = xt.nguoi_dung_tu_ve(ve_url)
        ve_dung = ve_url if nd else None
        if not nd:                      # vé hết hạn / sai -> xoá trong trình duyệt để không thử lại mãi
            st.session_state.xoa_ve_trinh_duyet = True
    st.session_state.nguoi_dung = nd
    st.session_state.ve = ve_dung

if st.session_state.pop("ghi_ve_moi", None):          # vừa đăng nhập -> lưu vé vào trình duyệt
    ghi_cookie(st.session_state.ve, xt.SO_NGAY_GIU_DANG_NHAP * 86400)
VUA_XOA_VE = bool(st.session_state.pop("xoa_ve_trinh_duyet", None))
if VUA_XOA_VE:                                        # vừa đăng xuất / vé hỏng -> xoá vé trong trình duyệt
    ghi_cookie("", 0)


def dang_xuat():
    xt.xoa_ve(st.session_state.get("ve"))
    st.session_state.nguoi_dung = None
    st.session_state.ve = None
    st.session_state.xoa_ve_trinh_duyet = True
    st.session_state.pop("mo_bao_mat", None)
    st.query_params.clear()          # lần đăng nhập sau vào thẳng trang chủ


def trang_dang_nhap():
    """Trang đăng nhập / đăng ký (hiện khi chưa đăng nhập)."""
    html(gd.css("Lúa"))
    html(gd.css_dang_nhap())
    html(gd.nen_dang_nhap())
    html(gd.dau_trang_dang_nhap(logo_base64(300), logo_chu_base64(), TEN_APP,
                                "Giá nông sản mỗi ngày · dự báo <b style='color:#F2B33D'>ngày mai</b>, "
                                "<b style='color:#F2B33D'>7</b> và "
                                "<b style='color:#F2B33D'>30 ngày</b> tới"))
    _, giua, _ = st.columns([1, 1.35, 1])
    with giua:
        with st.container(border=True, key="khung_dang_nhap"):
            # Thanh chuyển Đăng nhập / Đăng ký (2 nút tự làm, không dùng tabs của Streamlit)
            che_do = st.session_state.get("che_do_dn", "dang_nhap")
            with st.container(key="thanh_chuyen"):
                c_dn, c_dk = st.columns(2, gap="small")
                c_dn.button("Đăng nhập", key=f"the_dn_{'on' if che_do == 'dang_nhap' else 'off'}",
                            width="stretch", on_click=lambda: st.session_state.update(che_do_dn="dang_nhap"))
                c_dk.button("Đăng ký", key=f"the_dk_{'on' if che_do == 'dang_ky' else 'off'}",
                            width="stretch", on_click=lambda: st.session_state.update(che_do_dn="dang_ky"))
            if che_do == "dang_nhap":
                html('<div class="dn-tieu-de"><span class="chu-chay">Chào mừng trở lại</span> <span class="tay">👋</span></div>'
                     '<div class="dn-phu">Đăng nhập để xem giá và dự báo hôm nay</div>')
                so_lan_sai = st.session_state.get("so_lan_sai", 0)
                khoa_den = st.session_state.get("khoa_den")
                bi_khoa = khoa_den is not None and pd.Timestamp.now() < khoa_den
                with st.form("form_dang_nhap", clear_on_submit=False, border=False):
                    email = st.text_input("Email", placeholder="ten@gmail.com")
                    mat_khau = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
                    bam = st.form_submit_button("Đăng nhập", type="primary", width="stretch")
                if bi_khoa:
                    st.error(f"Bạn nhập sai quá nhiều lần. Hãy thử lại sau "
                             f"{int((khoa_den - pd.Timestamp.now()).total_seconds()) + 1} giây.")
                elif bam:
                    nd = xt.dang_nhap(email, mat_khau)
                    if nd:
                        st.session_state.nguoi_dung = nd
                        st.session_state.ve = xt.tao_ve(nd["id"])
                        st.session_state.ghi_ve_moi = True
                        st.session_state.so_lan_sai = 0
                        st.rerun()
                    so_lan_sai += 1
                    st.session_state.so_lan_sai = so_lan_sai
                    if so_lan_sai >= SO_LAN_SAI_TOI_DA:
                        st.session_state.khoa_den = pd.Timestamp.now() + pd.Timedelta(seconds=60)
                        st.session_state.so_lan_sai = 0
                        st.error("Bạn nhập sai quá nhiều lần. Hãy thử lại sau 60 giây.")
                    else:
                        st.error("Email hoặc mật khẩu chưa đúng.")
            else:
                html('<div class="dn-tieu-de"><span class="chu-chay">Tạo tài khoản mới</span> <span class="sao">✨</span></div>'
                     '<div class="dn-phu">Miễn phí · chỉ mất chưa đầy một phút</div>')
                with st.form("form_dang_ky", clear_on_submit=False, border=False):
                    ho_ten = st.text_input("Họ và tên", placeholder="Nguyễn Văn A")
                    email_dk = st.text_input("Email", placeholder="ten@gmail.com", key="email_dk")
                    mk1 = st.text_input("Mật khẩu", type="password", key="mk1", placeholder="••••••••",
                                        help="Ít nhất 8 ký tự, có cả chữ và số.")
                    mk2 = st.text_input("Nhập lại mật khẩu", type="password", key="mk2",
                                        placeholder="••••••••")
                    dong_y = st.checkbox("Tôi hiểu giá và dự báo chỉ mang tính tham khảo.")
                    bam_dk = st.form_submit_button("Tạo tài khoản", type="primary", width="stretch")
                if bam_dk:
                    if not dong_y:
                        st.error("Bạn cần đánh dấu ô xác nhận ở trên.")
                    else:
                        ok, kq_dk = xt.dang_ky(ho_ten, email_dk, mk1, mk2)
                        if ok:
                            # đăng ký xong -> tự đăng nhập và vào thẳng trang chủ
                            nd = xt.dang_nhap(email_dk, mk1)
                            st.session_state.nguoi_dung = nd
                            st.session_state.ve = xt.tao_ve(nd["id"])
                            st.session_state.ghi_ve_moi = True
                            st.session_state.che_do_dn = "dang_nhap"
                            st.session_state.chao_mung = f"🎉 Tạo tài khoản thành công! Chào mừng {nd['ho_ten']}."
                            st.rerun()
                        else:
                            for loi in kq_dk:
                                st.error(loi)
    # đèn rọi theo chuột: gửi vị trí chuột vào trang chính
    components.html("""<script>
      const d = window.parent.document;
      if (!d.__boNongDen) { d.__boNongDen = true;
        d.addEventListener("mousemove", e => {
          d.documentElement.style.setProperty("--mx", e.clientX + "px");
          d.documentElement.style.setProperty("--my", e.clientY + "px"); }); }
    </script>""", height=0)
    html(f'<div class="dn-chan">© {pd.Timestamp.today().year} · {TEN_APP} · '
         "Mật khẩu được mã hoá an toàn</div>")


def cau_noi_ve():
    """Trình duyệt còn vé đăng nhập -> tải lại trang kèm ?ve=... để app tự đăng nhập (dùng trên Streamlit Cloud)."""
    components.html(f"""<script>
    try {{
      const w = window.parent;
      const m = w.document.cookie.match(/(?:^|; ){TEN_COOKIE}=([^;]+)/);
      const u = new URL(w.location.href);
      if (m && m[1] && !u.searchParams.has("ve")) {{
        u.searchParams.set("ve", m[1]);
        // khung này bị "sandbox" nên không tự đổi trang được -> tạo 1 đường link trong trang chính rồi bấm
        const a = w.document.createElement("a");
        a.href = u.toString(); a.target = "_self"; a.style.display = "none";
        w.document.body.appendChild(a);
        w.document.body.style.opacity = "0";
        setTimeout(() => {{ w.document.body.style.opacity = "1"; }}, 3000);   // phòng khi không chuyển được
        a.click();
      }}
    }} catch (e) {{}}
    </script>""", height=0)


if not st.session_state.nguoi_dung:
    if not st.session_state.get("da_thu_ve_url") and not VUA_XOA_VE:
        cau_noi_ve()
    trang_dang_nhap()
    st.stop()

if st.session_state.get("chao_mung"):   # lời chào sau khi vừa đăng ký
    st.toast(st.session_state.pop("chao_mung"), icon="🌾")

# ================================================================ VÍ XU & VIP
ND_ID = st.session_state.nguoi_dung["id"]
try:
    vx.dong_bo(ND_ID)          # tặng xu chào mừng, xu VIP hằng tháng, ghi xu hết hạn
except Exception as loi:
    st.warning(f"Ví xu đang gặp lỗi: {loi}")
VIP = vx.thong_tin_vip(ND_ID)  # None = gói Miễn phí
HANG = VIP["hang"] if VIP else 0   # 0 Miễn phí · 1 Mùa Vàng · 2 Bội Thu · 3 Đại Điền (và Nhóm)
for _tb in st.session_state.pop("thong_bao_xu", []):
    st.toast(_tb, icon="🪙")


@st.cache_data
def anh_nho_b64(anh: bytes, co: int = 72) -> str:
    """Ảnh đại diện thu nhỏ (base64) cho ô tài khoản; không có ảnh -> chuỗi rỗng."""
    if not anh:
        return ""
    im = Image.open(io.BytesIO(anh)).convert("RGB")
    im.thumbnail((co, co))
    bo_dem = io.BytesIO()
    im.save(bo_dem, format="JPEG", quality=90)
    return base64.b64encode(bo_dem.getvalue()).decode()


def ho_so_hien_tai() -> dict:
    return xt.lay_ho_so(ND_ID) or {}


def bao(chu: str):
    """Hiện thông báo nhỏ sau khi trang tải lại."""
    st.session_state.setdefault("thong_bao_xu", []).append(chu)


def ve_thanh_tren(nong_san_css: str):
    """CSS + thanh tài khoản (Trang chủ · số xu · VIP · tên · Đăng xuất) cho mọi trang."""
    html(gd.css(nong_san_css))
    html(gd.css_vi())
    # (nút Đăng xuất đã chuyển vào Trang Cá Nhân)
    _, o_chao = st.columns([1, 5], vertical_alignment="center")
    with o_chao:
        html(gd.thanh_tai_khoan(st.session_state.nguoi_dung["ho_ten"], "?" + urlencode({"ns": MAC_DINH}),
                                vx.so_du(ND_ID), VIP, anh_nho_b64(ho_so_hien_tai().get("anh")),
                                st.query_params.get("trang") == "ca_nhan"))
    if st.query_params.get("trang") != "tro_ly":
        q = {"trang": "tro_ly"}
        for k in ("ns", "loai", "kv"):
            if st.query_params.get(k):
                q[k] = st.query_params.get(k)
        html(gd.nut_tro_ly("?" + urlencode(q), logo_base64(160)))
    if VIP and not VIP["la_thanh_vien"] and not VIP["tu_gia_han"]:
        con = (VIP["ket_thuc"] - pd.Timestamp.now()).total_seconds() / 86400
        if con <= 3:
            st.warning(f"⏳ {VIP['ten']} của bạn hết hạn lúc {VIP['ket_thuc']:%H:%M ngày %d/%m/%Y}. "
                       "Vào trang **Gói VIP** để gia hạn nếu muốn dùng tiếp.")


@st.dialog("Mở khoá bằng xu")
def hop_mo_khoa(tinh_nang: str, khoa: str, mo_ta: str):
    so_xu, so_ngay, ten = vx.GIA_MO_KHOA[tinh_nang]
    con = vx.so_du(ND_ID)
    thoi_han = "24 giờ" if so_ngay == 1 else f"{so_ngay} ngày"
    st.markdown(f"#### {ten}\n{mo_ta}")
    st.markdown(f"- Giá: **{so_xu} xu** (≈ {vx.tien(so_xu * vx.DONG_MOI_XU)})\n"
                f"- Dùng được: **{thoi_han}**, đếm từ lúc mở\n"
                f"- Ví của bạn: **{con} xu**" + (f" → còn **{con - so_xu} xu** sau khi mở" if con >= so_xu else ""))
    c1, c2 = st.columns(2)
    if con >= so_xu:
        if c1.button(f"Dùng {so_xu} xu", type="primary", width="stretch", key="xac_nhan_mo_khoa"):
            ok, tb = vx.mo_khoa(ND_ID, tinh_nang, khoa)
            if ok:
                bao(tb)
                st.rerun()
            st.error(tb)
    else:
        c1.error(f"Bạn còn thiếu {so_xu - con} xu.")
        st.caption("Điểm danh mỗi ngày trong **Ví xu** để nhận thêm xu, hoặc dùng thử VIP 7 ngày miễn phí.")
    with c2:
        html(gd.nut_link("Xem gói VIP", "?trang=vip", nhat=True))


@st.dialog("Thanh toán gói VIP", width="large")
def hop_thanh_toan():
    d = vx.lay_don(st.session_state.get("ma_don"))
    if not d or d["trang_thai"] != "cho":
        st.warning("Đơn này đã hết hạn hoặc đã huỷ. Hãy đóng cửa sổ và bấm mua lại.")
        return
    g = vx.GOI_VIP[d["san_pham"]]
    trai, phai = st.columns([1, 1.5], vertical_alignment="center")
    with trai:
        html(gd.qr_mau(d["ma_don"]))
        st.caption("Mã QR mẫu (chế độ thử) — không quét được")
    with phai:
        html("".join(f'<div class="tt-dong"><span>{a}</span><b>{b}</b></div>' for a, b in [
            ("Gói", f"{gd.e(g['ten'])} · {gd.e(g['ky'])}"),
            ("Số tiền", vx.tien(d["so_tien"])),
            ("Nội dung chuyển khoản", f"BONONG {d['ma_don']}"),
            ("Giữ đơn đến", f"{d['het_han_luc']:%H:%M %d/%m/%Y}"),
            ("Tự gia hạn", "Không")]))
    if vx.CHE_DO_THU:
        html('<div class="che-do-thu"><b>Chế độ thử:</b> ứng dụng chưa thu tiền thật. Bấm '
             '<b>Giả lập đã thanh toán</b> để xem VIP được bật như thế nào.</div>')
    b1, b2 = st.columns(2)
    if vx.CHE_DO_THU and b1.button("✅ Giả lập đã thanh toán", type="primary", width="stretch", key="gia_lap_tt"):
        ok, tb = vx.xac_nhan_thanh_toan(d["ma_don"], f"THU-{d['ma_don']}")
        if ok:
            bao(tb)
            st.balloons()
            st.rerun()
        st.error(tb)
    if b2.button("Huỷ đơn", width="stretch", key="huy_don"):
        vx.huy_don(d["ma_don"])
        st.rerun()


@st.dialog("Đổi xu lấy VIP")
def hop_doi_xu(loai_goi: str):
    g, can = vx.GOI_VIP[loai_goi], vx.DOI_XU_LAY_VIP[loai_goi]
    con = vx.so_du(ND_ID)
    st.markdown(f"Đổi **{can} xu** lấy **{g['ten']}** ({g['ky']}).\n\nVí của bạn: **{con} xu** "
                f"→ còn **{con - can} xu**. Xu đã đổi không hoàn lại.")
    if st.button(f"Xác nhận đổi {can} xu", type="primary", width="stretch", key="xac_nhan_doi_xu"):
        ok, tb = vx.doi_xu_lay_vip(ND_ID, loai_goi)
        if ok:
            bao(tb)
            st.rerun()
        st.error(tb)


@st.cache_data
def do_tin_cay():
    """Sai số trung bình (kiểm tra ngược) của mô hình được chọn so với cách đoán 'giá giữ nguyên'."""
    f = THU_MUC / "ket_qua_so_sanh_mo_hinh.csv"
    if not f.exists():
        return []
    ss = pd.read_csv(f, encoding="utf-8-sig")
    cot = ["Sai số ngày mai (%)", "Sai số 7 ngày (%)", "Sai số 30 ngày (%)"]
    chon = ss[ss["Được chọn"].fillna("") == "Có"][cot].mean()
    giu = ss[ss["Mô hình"] == "Giữ nguyên"][cot].mean()
    return [("Mô hình Bồ Nông chọn cho từng loại", *chon), ("Đoán \"giá giữ nguyên như hôm nay\"", *giu)]


def trang_vi():
    html(gd.dau_trang_con("Ví xu", "Xu được tặng miễn phí · dùng để mở khoá dự báo xa, lịch sử giá và tải Excel"))
    so_du = vx.so_du(ND_ID)
    sap_het, ngay_het = vx.xu_sap_het_han(ND_ID)
    trai, phai = st.columns([1.5, 1], gap="large")
    with trai:
        html(gd.the_vi(so_du, sap_het, ngay_het, VIP, vx.DONG_MOI_XU))
    with phai:
        hom_nay_co, chuoi = vx.chuoi_diem_danh(ND_ID)
        with st.container(border=True):
            st.markdown("**📅 Điểm danh mỗi ngày**")
            html(gd.chuoi_diem_danh(chuoi, hom_nay_co))
            st.caption(f"Chuỗi hiện tại: {chuoi} ngày. +2 xu mỗi ngày, ngày thứ 7 liên tiếp +10 xu "
                       f"(tối đa {vx.TRAN_DIEM_DANH_THANG} xu/tháng).")
            if st.button("Hôm nay đã điểm danh ✓" if hom_nay_co else "Điểm danh nhận xu", disabled=hom_nay_co,
                         type="primary", width="stretch", key="nut_diem_danh"):
                _, tb = vx.diem_danh(ND_ID)
                bao(tb)
                st.rerun()

    da_chi = vx.xu_da_chi(ND_ID)
    if not VIP and da_chi > vx.NGUONG_GOI_Y_VIP:
        st.info(f"💡 30 ngày qua bạn đã dùng {da_chi} xu (≈ {vx.tien(da_chi * vx.DONG_MOI_XU)}). "
                f"VIP Mùa Vàng chỉ {vx.tien(vx.GOI_VIP['mua_vang']['gia'])} và xem không giới hạn.")

    html(gd.tieu_de_muc("Cách nhận xu", "Bồ Nông không bán xu. Xu tặng dùng được 30 ngày, không đổi ra tiền "
                        "và không chuyển cho người khác. Khi tiêu, xu sắp hết hạn được dùng trước."))
    for o, (td, md) in zip(st.columns(4), [
            ("🎁 Tạo tài khoản · 50 xu", "Tặng một lần khi bạn có tài khoản Bồ Nông."),
            ("🌾 Nông trại · tới 11 xu/ngày", "Trồng cây, làm nhiệm vụ, đoán giá trong trò chơi Nông trại."),
            ("📅 Điểm danh · 2 – 10 xu/ngày", "Mở app và bấm điểm danh. Ngày thứ 7 liên tiếp được 10 xu."),
            ("👑 Thành viên VIP · 100 – 200 xu/tháng", "Mỗi tháng của kỳ VIP được cộng xu tặng.")]):
        with o:
            html(gd.o_nho(td, md))

    html(gd.tieu_de_muc("Dùng xu vào việc gì", "Mở khoá có thời hạn, đếm ngược từ lúc mở. VIP thì không cần xu."))
    for o, ma in zip(st.columns(3), ["du_bao", "du_bao_30", "lich_su"]):
        so_xu, so_ngay, ten = vx.GIA_MO_KHOA[ma]
        han = "24 giờ" if so_ngay == 1 else f"{so_ngay} ngày"
        cho = {"du_bao": "cho 1 giống hoặc 1 tỉnh", "du_bao_30": "cho 1 giống hoặc 1 tỉnh",
               "lich_su": "cho 1 nông sản"}[ma]
        with o:
            html(gd.o_nho(f"{ten} · {so_xu} xu", f"Dùng {han} {cho}. Mở ngay trên trang giá."))
    mo = vx.cac_mo_khoa_con_han(ND_ID)
    if mo:
        st.write("")
        st.markdown("**Đang mở khoá**")
        for m in mo:
            html(gd.da_mo_khoa(f"{gd.e(m['ten'])} · {gd.e(m['khoa'])} — đến {m['het_han']:%H:%M %d/%m/%Y}"))

    html(gd.tieu_de_muc("Đổi xu lấy VIP", "Tích đủ xu thì đổi lấy VIP, không cần trả tiền."))
    for o, (ma, can) in zip(st.columns(len(vx.DOI_XU_LAY_VIP) + 1), vx.DOI_XU_LAY_VIP.items()):
        g = vx.GOI_VIP[ma]
        if o.button(f"Đổi {can} xu → {g['ten']} ({g['ky']})", disabled=so_du < can, width="stretch",
                    key=f"doi_{ma}", help=None if so_du >= can else f"Bạn cần {can} xu"):
            hop_doi_xu(ma)

    html(gd.tieu_de_muc("Lịch sử giao dịch", "Mọi lần cộng, trừ xu và mọi đơn mua VIP đều được ghi lại."))
    loc = st.segmented_control("Lọc", ["Tất cả", "Được tặng", "Đã dùng", "Đơn VIP"], default="Tất cả",
                               label_visibility="collapsed", key="loc_lich_su") or "Tất cả"
    ds = vx.lich_su(ND_ID, {"Tất cả": None, "Được tặng": "tang", "Đã dùng": "chi", "Đơn VIP": "don"}[loc])
    if not ds:
        st.caption("Chưa có giao dịch nào.")
    else:
        bang = pd.DataFrame([{
            "Thời gian": pd.Timestamp(d["luc"]).strftime("%H:%M %d/%m/%Y"), "Nội dung": d["noi_dung"],
            "Xu": "" if d["xu"] is None else f"{d['xu']:+d}",
            "Số tiền": "" if d["tien"] is None else vx.tien(d["tien"]), "Trạng thái": d["trang_thai"]}
            for d in ds])
        st.dataframe(bang, hide_index=True, width="stretch", height=min(420, 38 + 35 * len(bang)))


def hieu_ung_the_vip():
    """Thẻ nghiêng 3D + đốm sáng theo chuột, giá chạy số từ 0 khi mở trang."""
    components.html("""<script>
    const w = window.parent, d = w.document;
    if (!d.__boNongVip) { d.__boNongVip = true;
      d.addEventListener("mousemove", e => {
        const the = e.target.closest ? e.target.closest(".goi-vo") : null;
        d.querySelectorAll(".goi-vo.nghieng").forEach(x => { if (x !== the) {
          x.classList.remove("nghieng"); x.style.setProperty("--rx", "0deg"); x.style.setProperty("--ry", "0deg"); } });
        if (!the) return;
        const r = the.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        the.classList.add("nghieng");
        the.style.setProperty("--ry", ((x - .5) * 12).toFixed(2) + "deg");
        the.style.setProperty("--rx", ((.5 - y) * 9).toFixed(2) + "deg");
        const goi = the.querySelector(".goi");
        if (goi) { goi.style.setProperty("--px", (x * 100).toFixed(1) + "%"); goi.style.setProperty("--py", (y * 100).toFixed(1) + "%"); }
      });
    }
    const chay = () => d.querySelectorAll(".gia[data-gia]:not([data-xong])").forEach((el, i) => {
      el.dataset.xong = 1;
      const dich = +el.dataset.gia, so = el.querySelector(".so");
      if (!so || !dich) return;
      const t0 = w.performance.now() + 250 + i * 120;
      const buoc = t => { const p = Math.max(0, Math.min(1, (t - t0) / 1300));
        so.textContent = Math.round(dich * (1 - Math.pow(1 - p, 3))).toLocaleString("vi-VN");
        if (p < 1) w.requestAnimationFrame(buoc); };
      so.textContent = "0"; w.requestAnimationFrame(buoc);
    });
    chay(); setTimeout(chay, 300); setTimeout(chay, 1200);
    </script>""", height=0)


def trang_vip():
    html(gd.dau_trang_con("Gói VIP", "Xem dự báo 7 & 30 ngày, lịch sử giá và giá thế giới không giới hạn",
                          bieu_tuong="vip"))
    if vx.CHE_DO_THU:
        html('<div class="che-do-thu"><b>Đang chạy chế độ thử:</b> chưa thu tiền thật. Khi mua, bạn sẽ thấy mã QR '
             'mẫu và nút "Giả lập đã thanh toán".</div>')
    if VIP:
        phu = " (trong gói Nhóm của người khác)" if VIP["la_thanh_vien"] else ""
        st.success(f"👑 Bạn đang là **{VIP['ten']}**{phu} đến **{VIP['ket_thuc']:%H:%M %d/%m/%Y}**. "
                   "Mua lại cùng gói sẽ được cộng nối tiếp; mua gói cao hơn có hiệu lực ngay.")
    goi_dang_dung = VIP["loai_goi"] if VIP else None
    html(gd.cac_the_goi_vip(vx.GOI_VIP, goi_dang_dung))
    hieu_ung_the_vip()
    cot = st.columns(4)
    cot[0].button("Gói hiện tại" if not VIP else "Gói cơ bản", key="goi_mien_phi", width="stretch", disabled=True)
    for o, ma in zip(cot[1:], ["mua_vang", "boi_thu", "dai_dien"]):
        g = vx.GOI_VIP[ma]
        nhan = ("Gia hạn" if goi_dang_dung == ma else "Chọn") + f" {g['ten'].replace('VIP ', '')}"
        if o.button(nhan, key=f"mua_{ma}", width="stretch"):
            st.session_state.ma_don = vx.tao_don(ND_ID, ma)["ma_don"]
            hop_thanh_toan()
    html(gd.dai_goi_nhom(vx.GOI_VIP["nhom"], goi_dang_dung == "nhom"))
    _, c_nhom = st.columns([3, 1])
    if c_nhom.button("Chọn VIP Nhóm", key="mua_nhom", width="stretch"):
        st.session_state.ma_don = vx.tao_don(ND_ID, "nhom")["ma_don"]
        hop_thanh_toan()
    st.write("")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.container(border=True):
            st.markdown("**🎁 Dùng thử VIP Mùa Vàng 7 ngày miễn phí**")
            st.caption("Mỗi tài khoản một lần, không cần thanh toán. Hết hạn tự về gói Miễn phí, không trừ tiền.")
            da_thu = vx.da_dung_thu(ND_ID)
            if st.button("Đã dùng thử" if da_thu else ("Bạn đang là VIP" if VIP else "Bắt đầu dùng thử"),
                         disabled=da_thu or bool(VIP), type="primary", width="stretch", key="nut_dung_thu"):
                ok, tb = vx.dung_thu(ND_ID)
                bao(tb) if ok else st.error(tb)
                st.rerun()
    with c2:
        with st.container(border=True):
            so_du = vx.so_du(ND_ID)
            st.markdown(f"**🪙 Đổi xu lấy VIP** · bạn đang có {so_du} xu")
            st.caption(" · ".join(f"{can} xu = {vx.GOI_VIP[m]['ten']} ({vx.GOI_VIP[m]['ky']})"
                                  for m, can in vx.DOI_XU_LAY_VIP.items()))
            for o, (ma, can) in zip(st.columns(2), vx.DOI_XU_LAY_VIP.items()):
                if o.button(f"Đổi {can} xu", disabled=so_du < can, width="stretch", key=f"vip_doi_{ma}"):
                    hop_doi_xu(ma)

    if VIP and not VIP["la_thanh_vien"] and not VIP["dung_thu"]:
        bat = st.toggle("Tự động gia hạn khi hết kỳ", value=VIP["tu_gia_han"], key="tu_gia_han",
                        help="Mặc định tắt. Trước khi hết hạn 3 ngày app sẽ nhắc bạn gia hạn.")
        if bat != VIP["tu_gia_han"]:
            vx.dat_tu_gia_han(ND_ID, bat)
            st.rerun()

    nhom = vx.goi_nhom_cua(ND_ID)
    if nhom:
        con_cho = vx.GOI_VIP["nhom"]["so_tk"] - 1 - len(nhom["thanh_vien"])
        html(gd.tieu_de_muc("Thành viên gói VIP Nhóm",
                            f"Gói dùng đến {nhom['ket_thuc']:%d/%m/%Y}. Bạn thêm được tối đa "
                            f"{vx.GOI_VIP['nhom']['so_tk'] - 1} người (còn {con_cho} chỗ). Người được thêm "
                            "đăng nhập bằng đúng email đó sẽ tự có VIP."))
        for tv in nhom["thanh_vien"]:
            a, b = st.columns([5, 1], vertical_alignment="center")
            a.markdown(f"**{tv['ho_ten'] or 'Chưa tạo tài khoản'}** · {tv['email']}")
            if b.button("Bỏ khỏi nhóm", key=f"bo_{tv['email']}", width="stretch"):
                vx.bo_thanh_vien(ND_ID, tv["email"])
                st.rerun()
        if con_cho > 0:
            with st.form("them_tv", clear_on_submit=True):
                email_tv = st.text_input("Email thành viên", placeholder="ban@gmail.com")
                if st.form_submit_button("Thêm vào nhóm", type="primary"):
                    ok, tb = vx.them_thanh_vien(ND_ID, email_tv)
                    if ok:
                        bao(tb)
                        st.rerun()
                    st.error(tb)

    html(gd.tieu_de_muc("So sánh quyền lợi"))
    html(gd.bang_quyen_loi())
    tc = do_tin_cay()
    if tc:
        html(gd.tieu_de_muc("Độ tin cậy của dự báo",
                            "Sai số trung bình khi kiểm tra ngược trên dữ liệu thật (càng nhỏ càng sát). "
                            "Dự báo ngắn hạn chỉ sát ngang cách đoán \"giá giữ nguyên\" — VIP giúp bạn xem "
                            "xu hướng và khoảng dao động, không hứa trước giá chính xác."))
        html(gd.bang_do_tin_cay(tc))
    html('<div class="chu-thich" style="margin-top:1rem">Dự báo chỉ để tham khảo. '
         'Trừ tiền mà không nhận được VIP: hoàn 100% trong 3 ngày làm việc. Mua nhầm: hoàn 100% nếu yêu cầu '
         'trong 48 giờ và chưa dùng tính năng VIP.</div>')

# Tự lấy giá mới khi mở web nếu còn thiếu ngày hôm qua (mỗi phiên chỉ thử 1 lần)
if not st.session_state.get("da_tu_cap_nhat"):
    st.session_state.da_tu_cap_nhat = True
    try:
        if can_cap_nhat():
            chay_cap_nhat()
    except Exception as loi:
        st.session_state.bao_cao_cap_nhat = [f"⚠️ Không tự cập nhật được: {loi}"]

try:
    df = tai_du_lieu(dau_vet_du_lieu())
except Exception as loi:
    st.error(f"Không đọc được dữ liệu: {loi}")
    st.stop()

MAC_DINH = "Lúa"   # mở web là hiện giá lúa trước


def gia_moi_nhat(ns, loai, kv):
    c = df[(df["nong_san"] == ns) & (df["loai"] == loai) & (df["khu_vuc"] == kv)]
    if c.empty:
        return None
    c = c.sort_values("ngay")
    return c["ngay"].iloc[-1], c["gia"].iloc[-1]


# Cảnh báo giá tuỳ chọn (Bội Thu trở lên): phiên giá mới chạm ngưỡng -> báo
if HANG >= vx.HANG_TOI_THIEU["canh_bao"]:
    try:
        for cb in vx.kiem_tra_canh_bao(ND_ID, gia_moi_nhat):
            chu = "đã lên" if cb["kieu"] == "tren" else "đã xuống"
            st.session_state.setdefault("canh_bao_moi", []).append(
                f"🔔 **Cảnh báo giá:** {cb['loai']} · {cb['khu_vuc']} {chu} **{gd.so(cb['gia'])} đ/kg** "
                f"(ngưỡng {gd.so(cb['nguong'])} đ) — phiên {pd.Timestamp(cb['ngay']):%d/%m/%Y}.")
    except Exception as loi:
        st.warning(f"Không kiểm tra được cảnh báo giá: {loi}")

@st.cache_resource
def avatar_bo_nong():
    """Avatar trợ lý: con bồ nông trên nền tròn trắng, viền vàng cam."""
    from PIL import ImageDraw
    n = 160
    nen = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ve = ImageDraw.Draw(nen)
    for i in range(10):   # viền chuyển màu vàng -> cam
        t = i / 9
        ve.ellipse((i, i, n - 1 - i, n - 1 - i), fill=(int(242 + (232 - 242) * t), int(179 + (116 - 179) * t),
                                                      int(61 + (59 - 61) * t), 255))
    ve.ellipse((10, 10, n - 11, n - 11), fill=(255, 255, 255, 255))
    if FILE_LOGO.exists():
        from PIL import ImageChops
        anh = Image.open(FILE_LOGO).convert("RGBA")
        # cắt sát con bồ nông (bỏ phần nền trắng/trong suốt thừa) để hình to, rõ
        nen_trang = Image.new("RGBA", anh.size, (255, 255, 255, 255))
        nen_trang.alpha_composite(anh)
        khac = ImageChops.difference(nen_trang.convert("RGB"), Image.new("RGB", anh.size, "white")).convert("L")
        khung = khac.point(lambda v: 255 if v > 24 else 0).getbbox()   # bỏ qua nền gần-trắng
        if khung:
            anh = anh.crop(khung)
        anh.thumbnail((n - 40, n - 40))
        anh = anh.convert("RGBA")
        nen.alpha_composite(anh, ((n - anh.width) // 2, (n - anh.height) // 2))
    return nen


@st.cache_resource
def avatar_nguoi_dung(ho_ten: str, anh: bytes = None):
    """Avatar người dùng: ảnh đại diện (cắt tròn, viền trắng); chưa có ảnh -> chữ cái đầu trên nền xanh lá."""
    from PIL import ImageDraw, ImageFont
    n = 160
    nen = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ve = ImageDraw.Draw(nen)
    if anh:
        ve.ellipse((0, 0, n - 1, n - 1), fill=(255, 255, 255, 255))
        im = Image.open(io.BytesIO(anh)).convert("RGBA").resize((n - 12, n - 12))
        mat_na = Image.new("L", im.size, 0)
        ImageDraw.Draw(mat_na).ellipse((0, 0, im.width - 1, im.height - 1), fill=255)
        nen.paste(im, (6, 6), mat_na)
        return nen
    for i in range(n // 2):   # nền tròn chuyển màu từ xanh đậm (ngoài) tới xanh tươi (trong)
        t = i / (n // 2)
        ve.ellipse((i, i, n - 1 - i, n - 1 - i), fill=(int(31 + (92 - 31) * t), int(74 + (180 - 74) * t),
                                                      int(22 + (70 - 22) * t), 255))
    chu = (ho_ten.strip().split()[-1][:1] if ho_ten.strip() else "?").upper()
    phong = None
    for ten in ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            phong = ImageFont.truetype(ten, 84)
            break
        except Exception:
            pass
    phong = phong or ImageFont.load_default()
    ve.text((n / 2, n / 2 + 2), chu, fill=(255, 255, 255, 255), font=phong, anchor="mm")
    return nen


def trang_tro_ly():
    """Trang chatbot: hỏi đáp về giá, trả lời bằng AI dựa trên số liệu của web."""
    khoa, mo_hinh = ai.doc_cau_hinh(st.secrets)
    co_quyen_ai = HANG >= vx.HANG_TOI_THIEU["ai"]
    ns_q = st.query_params.get("ns")
    ns_q = ns_q if ns_q in NONG_SAN else MAC_DINH
    html(gd.dau_trang_tro_ly(logo_base64(220), bool(khoa) and co_quyen_ai,
                             "?" + urlencode({k: st.query_params.get(k) for k in ("ns", "loai", "kv")
                                              if st.query_params.get(k)} or {"ns": MAC_DINH})))
    html(gd.css_chat())
    if not co_quyen_ai:
        html(gd.khung_khoa("Trợ lý AI dành cho gói Bội Thu trở lên",
                           "Hỏi bất cứ điều gì về giá lúa, cà phê, hồ tiêu: trợ lý đọc giá thật, dự báo và giá thế giới "
                           "trong Bồ Nông rồi trả lời dễ hiểu."))
        _, giua, _ = st.columns([1, 1.2, 1])
        with giua:
            html(gd.nut_link("Xem gói Bội Thu", "?trang=vip"))
        return

    # --- Loại người dùng vừa xem ở trang giá (lấy từ đường link); không có thì lấy loại có số liệu mới nhất.
    #     Trợ lý vẫn có giá mới nhất của MỌI giống/tỉnh nên hỏi loại khác vẫn trả lời được.
    ns = ns_q
    phan_tl = df[df["nong_san"] == ns]
    moi = phan_tl.groupby("loai")["ngay"].max()
    ds_loai = sorted(moi.index, key=lambda x: (-moi[x].value, x))
    loai = st.query_params.get("loai") if st.query_params.get("loai") in ds_loai else ds_loai[0]
    ds_kv = sorted(phan_tl.loc[phan_tl["loai"] == loai, "khu_vuc"].unique())
    kv = st.query_params.get("kv") if st.query_params.get("kv") in ds_kv else ds_kv[0]
    chuoi_tl = lay_chuoi_gia(df, ns, loai, kv)
    try:
        kq_tl = tinh_du_bao(ns, loai, kv, dau_vet_du_lieu())
    except Exception as loi:
        st.error(f"Không tính được dự báo: {loi}")
        return
    khoa_tl = vx.khoa_du_bao(ns, loai, kv)
    xem_ngay = 30 if vx.co_quyen(ND_ID, "du_bao_30", khoa_tl, HANG) else (
        7 if vx.co_quyen(ND_ID, "du_bao_7", khoa_tl, HANG) else 1)
    nhan_dinh = pt.phan_tich_gia(TEN_NGAN[ns], chuoi_tl, kq_tl, xem_ngay,
                                 tai_the_gioi(dau_vet_du_lieu()) if ns == "Cà phê" else None)

    # (Chưa có khoá API trong .streamlit/secrets.toml -> trợ lý tự trả lời bằng nhận định có sẵn)

    # --- Cuộc trò chuyện
    gioi_han = ai.SO_LUOT_NGAY.get(HANG, 20)
    lich = st.session_state.setdefault("chat_ai", [])
    anh_bn = avatar_bo_nong()
    anh_nd = avatar_nguoi_dung(st.session_state.nguoi_dung["ho_ten"], ho_so_hien_tai().get("anh"))
    if not lich:
        with st.chat_message("assistant", avatar=anh_bn):
            st.markdown("Chào bạn 👋 Mình là **Trợ lý Bồ Nông**. Mình có giá hằng ngày của lúa, cà phê, hồ tiêu "
                        "ở các tỉnh, dự báo và giá thế giới "
                        "cùng giá các tỉnh và giá thế giới. Bạn muốn hỏi gì về giá nông sản?")
    for m in lich[-20:]:
        with st.chat_message(m["role"], avatar=anh_nd if m["role"] == "user" else anh_bn):
            st.markdown(m["content"])
    chon = None
    if not lich:
        for i, (o, q) in enumerate(zip(st.columns(3), ai.cau_hoi_goi_y(TEN_NGAN[ns], ns))):
            if o.button(q, key=f"goi_y_ai_{i}", width="stretch"):
                chon = q
    con = gioi_han - vx.so_luot_hoi_hom_nay(ND_ID)
    cau = st.chat_input("Nhắn cho Trợ lý Bồ Nông… (giá hôm nay, dự báo, giá thế giới, thời vụ)", key="o_hoi_ai",
                        max_chars=500) or chon
    if cau:
        lich.append({"role": "user", "content": cau})
        with st.chat_message("user", avatar=anh_nd):
            st.markdown(cau)
        with st.chat_message("assistant", avatar=anh_bn):
            with st.spinner("Trợ lý đang đọc số liệu của Bồ Nông…"):
                if not khoa:
                    tl = ai.tra_loi_du_phong(cau, nhan_dinh)
                elif con <= 0:
                    tl = ai.tra_loi_du_phong(cau, nhan_dinh, f"Bạn đã dùng hết {gioi_han} lượt hỏi trợ lý AI hôm nay.")
                else:
                    try:
                        du_lieu = ai.ngu_canh(df, ns, loai, kv, chuoi_tl, kq_tl, xem_ngay, nhan_dinh,
                                              tai_the_gioi(dau_vet_du_lieu()), tai_tieu_the_gioi(dau_vet_du_lieu()),
                                              VIP["ten"] if VIP else "Miễn phí")
                        tl = ai.hoi_gemini(cau, lich[:-1], du_lieu, khoa, mo_hinh)
                        vx.tang_luot_hoi(ND_ID)
                        con -= 1
                    except ai.LoiAI as loi:
                        tl = ai.tra_loi_du_phong(cau, nhan_dinh, str(loi))
                    except Exception as loi:
                        tl = ai.tra_loi_du_phong(cau, nhan_dinh, "Trợ lý AI đang gặp sự cố.")
            st.markdown(tl)
        lich.append({"role": "assistant", "content": tl})
        del lich[:-30]
    if lich:
        _, c2 = st.columns([3.2, 1])
        if c2.button("Xoá trò chuyện", key="xoa_chat_ai", width="stretch"):
            lich.clear()
            st.rerun()

    # Dòng ghi chú + chân trang: đặt NGAY DƯỚI ô nhập câu hỏi (khu vực ghim cuối màn hình)
    ghi_chu = gd.chu_duoi_o_hoi(
        (f"Còn {max(con, 0)}/{gioi_han} lượt hỏi trợ lý AI hôm nay. " if khoa else "")
        + "Câu hỏi và số liệu giá được gửi tới dịch vụ AI bên ngoài để soạn câu trả lời; không gửi tên hay email. "
        "Câu trả lời chỉ để tham khảo.",
        f"© {pd.Timestamp.today().year} · {TEN_APP} · Số liệu chỉ mang tính tham khảo.")
    vung_duoi = getattr(st, "bottom", None) or getattr(st, "_bottom", None)
    if vung_duoi is not None:
        with vung_duoi:
            html(ghi_chu)
    else:
        html(ghi_chu)


def trang_ca_nhan():
    """Trang cá nhân: đổi ảnh đại diện, thông tin cá nhân; email & mật khẩu chỉ mở ra khi bấm."""
    hs = ho_so_hien_tai()
    html(gd.css_ca_nhan())
    mo = st.session_state.get("mo_bao_mat")          # None | "email" | "mat_khau"

    def bat_tat(muc):
        st.session_state.mo_bao_mat = None if st.session_state.get("mo_bao_mat") == muc else muc

    with st.container(key="trang_ca_nhan"):
        html(gd.the_ho_so(hs.get("ho_ten", ""), hs.get("email", ""), anh_nho_b64(hs.get("anh"), 240),
                          VIP["ten"] if VIP else "Gói Miễn phí", bool(VIP), hs.get("ngay_tao"), vx.so_du(ND_ID)))

        trai, phai = st.columns([1, 1.85], gap="medium")
        # ---------------- Ảnh đại diện
        with trai:
            with st.container(key="khung_anh"):
                html(gd.dau_muc_ca_nhan("anh", "Ảnh đại diện", "Hiện ở góc trên và trong khung chat"))
                cho_anh = st.empty()   # chỗ hiện ảnh (ảnh hiện tại hoặc ảnh mới chọn)
                tep = st.file_uploader("Chọn ảnh mới", type=["jpg", "jpeg", "png", "webp"], key="tai_anh",
                                       label_visibility="collapsed")
                if tep is None:
                    cho_anh.markdown(gd.anh_xem_truoc(anh_nho_b64(hs.get("anh"), 240), "Ảnh hiện tại",
                                                      hs.get("ho_ten", "")), unsafe_allow_html=True)
                else:
                    cho_anh.markdown(gd.anh_xem_truoc(base64.b64encode(tep.getvalue()).decode(), "Ảnh mới"),
                                     unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    if c1.button("Lưu ảnh", type="primary", width="stretch", key="luu_anh"):
                        ok, tb = xt.luu_anh(ND_ID, tep.getvalue())
                        if ok:
                            bao(tb)
                            st.session_state.pop("tai_anh", None)
                            st.rerun()
                        st.error(tb)
                    if c2.button("Huỷ", width="stretch", key="huy_anh"):
                        st.session_state.pop("tai_anh", None)
                        st.rerun()
                if tep is None and hs.get("anh"):
                    if st.button("Xoá ảnh hiện tại", width="stretch", key="xoa_anh"):
                        xt.xoa_anh(ND_ID)
                        bao("Đã xoá ảnh đại diện.")
                        st.rerun()
                html('<div class="cn-chu-nho">Ảnh được tự cắt vuông ở giữa · JPG, PNG, WEBP · tối đa 5 MB</div>')

        # ---------------- Thông tin cá nhân
        with phai:
            with st.container(key="khung_thong_tin"):
                html(gd.dau_muc_ca_nhan("nguoi", "Thông tin cá nhân", "Giúp Bồ Nông gợi ý giá đúng nơi, đúng cây của bạn"))
                with st.form("form_ho_so", border=False):
                    c1, c2 = st.columns(2)
                    ho_ten = c1.text_input("Họ và tên", value=hs.get("ho_ten", ""), max_chars=60)
                    sdt = c2.text_input("Số điện thoại", value=hs.get("so_dien_thoai") or "", placeholder="0912345678",
                                        max_chars=13)
                    c3, c4 = st.columns(2)
                    tinh = c3.text_input("Tỉnh / thành phố", value=hs.get("tinh") or "", placeholder="Ví dụ: An Giang",
                                         max_chars=60)
                    vai_tro = c4.selectbox("Bạn là", xt.VAI_TRO,
                                           index=xt.VAI_TRO.index(hs["vai_tro"]) if hs.get("vai_tro") in xt.VAI_TRO else 0)
                    cay = st.multiselect("Cây trồng / mặt hàng chính", xt.CAY_TRONG, default=hs.get("cay_trong") or [],
                                         placeholder="Chọn một hoặc nhiều")
                    if st.form_submit_button("Lưu thông tin", type="primary"):
                        ok, kq_ = xt.cap_nhat_ho_so(ND_ID, ho_ten, sdt, tinh, vai_tro, cay)
                        if ok:
                            st.session_state.nguoi_dung["ho_ten"] = ho_ten.strip()
                            bao(kq_)
                            st.rerun()
                        for loi in kq_:
                            st.error(loi)

        # ---------------- Đăng nhập & bảo mật (bấm mới mở)
        with st.container(key="khung_bao_mat"):
            html(gd.dau_muc_ca_nhan("khoa", "Đăng nhập & bảo mật", "Bấm vào từng mục để thay đổi"))

            d1, n1 = st.columns([4.2, 1], vertical_alignment="center")
            d1.markdown(gd.dong_bao_mat("thu", "Email đăng nhập", hs.get("email", ""), mo == "email"),
                        unsafe_allow_html=True)
            n1.button("Đóng" if mo == "email" else "Đổi email", key="nut_mo_email", width="stretch",
                      on_click=bat_tat, args=("email",))
            if mo == "email":
                with st.container(key="mo_doi_email"):
                    with st.form("form_doi_email", clear_on_submit=True, border=False):
                        c1, c2 = st.columns(2)
                        email_moi = c1.text_input("Email mới", placeholder="ten@gmail.com")
                        mk_e = c2.text_input("Mật khẩu hiện tại", type="password", key="mk_doi_email")
                        if st.form_submit_button("Xác nhận đổi email", type="primary"):
                            ok, tb = xt.doi_email(ND_ID, email_moi, mk_e)
                            if ok:
                                st.session_state.nguoi_dung["email"] = email_moi.strip().lower()
                                st.session_state.mo_bao_mat = None
                                bao(tb)
                                st.rerun()
                            st.error(tb)
                    if VIP and VIP.get("la_thanh_vien"):
                        st.caption("Bạn đang dùng VIP trong gói Nhóm theo email này. Đổi email sẽ mất quyền VIP đó.")

            d2, n2 = st.columns([4.2, 1], vertical_alignment="center")
            d2.markdown(gd.dong_bao_mat("khoa", "Mật khẩu", "••••••••", mo == "mat_khau"), unsafe_allow_html=True)
            n2.button("Đóng" if mo == "mat_khau" else "Đổi mật khẩu", key="nut_mo_mk", width="stretch",
                      on_click=bat_tat, args=("mat_khau",))
            if mo == "mat_khau":
                with st.container(key="mo_doi_mk"):
                    with st.form("form_doi_mk", clear_on_submit=True, border=False):
                        c1, c2, c3 = st.columns(3)
                        mk_cu = c1.text_input("Mật khẩu hiện tại", type="password", key="mk_cu")
                        mk_moi = c2.text_input("Mật khẩu mới", type="password", key="mk_moi",
                                               help="Ít nhất 8 ký tự, có cả chữ và số.")
                        mk_lai = c3.text_input("Nhập lại mật khẩu mới", type="password", key="mk_lai")
                        if st.form_submit_button("Xác nhận đổi mật khẩu", type="primary"):
                            ok, tb = xt.doi_mat_khau(ND_ID, mk_cu, mk_moi, mk_lai, st.session_state.get("ve"))
                            if ok:
                                st.session_state.mo_bao_mat = None
                                bao(tb[0])
                                st.rerun()
                            for loi in tb:
                                st.error(loi)

            d3, n3 = st.columns([4.2, 1], vertical_alignment="center")
            d3.markdown(gd.dong_bao_mat("ra", "Đăng xuất", "Thoát tài khoản trên thiết bị này", False),
                        unsafe_allow_html=True)
            n3.button("Đăng xuất", key="nut_dang_xuat", width="stretch", on_click=dang_xuat)


def trang_nong_trai():
    """Trò chơi trồng cây nhận xu."""
    html(gd.css_nong_trai())
    html(gd.css_canh_nong_trai())
    # chấm các lần đoán giá đã có giá phiên mới
    try:
        for kq_dd in nt.cham_du_doan(ND_ID, df):
            if kq_dd["ket_qua"] == "dung":
                bao(f"🎯 Bạn đoán đúng giá {kq_dd['nong_san'].lower()}! +{nt.XU_DOAN_DUNG} xu.")
                st.session_state.nt_xu_bay = st.session_state.get("nt_xu_bay", 0) + nt.XU_DOAN_DUNG
            else:
                bao(f"Lần đoán giá {kq_dd['nong_san'].lower()} chưa đúng. Thử lại hôm nay nhé!")
    except Exception as loi:
        st.warning(f"Chưa chấm được phần đoán giá: {loi}")
    if st.session_state.get("nt_xu_bay"):
        html(gd.xu_bay(st.session_state.pop("nt_xu_bay")))

    so_o = nt.O_THEO_HANG.get(HANG, 1)
    with st.container(key="trang_nong_trai"):

        @st.fragment(run_every=30)          # tự cập nhật đồng hồ, tiến độ mỗi 30 giây
        def ruong_cay():
            ng = nt.nguoi_choi(ND_ID)
            nv = nt.nhiem_vu(ND_ID)
            theo_vt = {d["vi_tri"]: d for d in nt.ruong(ND_ID, HANG)}
            cac_o = [theo_vt[v] for v in nt.THU_TU_VE]          # vẽ: trái · giữa · phải
            html(gd.canh_nong_trai(cac_o, nt.CAY, nt.GIAI_DOAN, ng, nv["xu_thu_hom_nay"],
                                   nt.TRAN_XU_THU_HOACH_NGAY, so_o, st.session_state.pop("nt_vua_tuoi", None),
                                   st.session_state.get("nt_chon")))
            for o, d in zip(st.columns(3, gap="medium"), cac_o):
                vt = d["vi_tri"]
                with o:
                    if not d["mo"]:
                        html(gd.nut_link(f"Mở bằng {'VIP Mùa Vàng' if vt == 1 else 'VIP Bội Thu'}", "?trang=vip",
                                         nhat=True))
                    elif not d["cay"] and st.session_state.get("nt_chon") != vt:
                        # dấu + nằm ngay trên luống đất trống trong khung cảnh
                        if st.button("＋", key=f"nt_cong_{vt}"):
                            st.session_state.nt_chon = vt
                            st.rerun(scope="fragment")
                    elif not d["cay"]:
                        # bảng chọn 3 hạt giống bật lên trên luống
                        with st.container(key=f"nt_chon_{vt}"):
                            html('<div class="chon-hat-td">🌱 Chọn hạt giống</div>')
                            if st.button("✕", key=f"nt_dong_{vt}", help="Đóng"):
                                st.session_state.pop("nt_chon", None)
                                st.rerun(scope="fragment")
                            for o2, (ma, c) in zip(st.columns(3, gap="small"), nt.CAY.items()):
                                if o2.button(f"{c['ten']}\n{c['gio']} giờ", key=f"nt_gieo_{vt}_{ma}",
                                             width="stretch"):
                                    ok, tb = nt.gieo(ND_ID, vt, ma, HANG)
                                    (bao if ok else st.error)(tb)
                                    if ok:
                                        st.session_state.pop("nt_chon", None)
                                        st.rerun()
                    elif d["giai_doan"] == 3:
                        if st.button("🧺 Thu hoạch", key=f"nt_thu_{vt}", width="stretch"):
                            ok, tb, xu = nt.thu_hoach(ND_ID, vt, HANG)
                            if ok:
                                bao(tb)
                                if xu:
                                    st.session_state.nt_xu_bay = xu
                                st.rerun()
                            st.error(tb)
                    elif d["tuoi_duoc"]:
                        if st.button(f"💧 Tưới nước · nhanh {d['phut_bot']} phút", key=f"nt_tuoi_{vt}", width="stretch"):
                            ok, tb = nt.tuoi(ND_ID, vt, HANG)
                            if ok:
                                bao(tb)
                                st.session_state.nt_vua_tuoi = vt
                                st.rerun()
                            st.error(tb)
                    else:
                        chu = ("💧 Đã tưới đủ 3 lần" if d["da_tuoi"] >= nt.TUOI_TOI_DA else
                               f"💧 Đất còn ẩm · tưới lại sau {max(d['cho_tuoi_giay'] // 60, 1)} phút")
                        st.button(chu, key=f"nt_tuoi_{vt}", width="stretch", disabled=True)

        ruong_cay()
        cot_nv, cot_dd, cot_kho = st.columns(3, gap="medium")
        with st.expander("📖 Cách chơi"):
            st.markdown(
                f"- Bấm dấu **＋** trên luống trống rồi **chọn hạt giống**: Lúa 2 giờ · Hồ tiêu 4 giờ · Cà phê 8 giờ.\n"
                "- Cây qua 4 giai đoạn: hạt → nảy mầm → đang lớn → chín.\n"
                "- **Tưới nước giúp cây lớn nhanh:** mỗi lần tưới bớt 15% thời gian trồng; 30 phút tưới được 1 lần, "
                "tối đa 3 lần cho mỗi cây.\n"
                f"- **Thu hoạch** được kinh nghiệm và +{nt.XU_THU_HOACH} xu (tối đa {nt.TRAN_XU_THU_HOACH_NGAY} xu/ngày).\n"
                f"- Làm đủ **nhiệm vụ hôm nay**: +{nt.XU_NHIEM_VU} xu · **Đoán giá** đúng: +{nt.XU_DOAN_DUNG} xu · "
                f"**Lên cấp**: +{nt.XU_LEN_CAP} xu.\n"
                "- Luống giữa luôn mở · luống trái mở bằng VIP Mùa Vàng · luống phải mở bằng VIP Bội Thu trở lên.\n"
                "- Xu nhận từ nông trại dùng được 30 ngày, như các xu được tặng khác.")

        with cot_nv:
            nv = nt.nhiem_vu(ND_ID)
            html(gd.the_nhiem_vu(nv))
            if nv["xong"] and not nv["da_nhan"]:
                if st.button(f"🎁 Nhận {nt.XU_NHIEM_VU} xu thưởng", key="nt_nhan_nv", type="primary", width="stretch"):
                    ok, tb = nt.nhan_thuong_nhiem_vu(ND_ID)
                    if ok:
                        bao(tb)
                        st.session_state.nt_xu_bay = nt.XU_NHIEM_VU
                        st.rerun()
                    st.error(tb)
            elif nv["da_nhan"]:
                st.caption("✅ Đã nhận thưởng nhiệm vụ hôm nay.")

        with cot_dd, st.container(key="khung_doan_gia"):
            st.markdown(f"**🎯 Đoán giá phiên tới** · đúng được +{nt.XU_DOAN_DUNG} xu")
            if nt.da_doan_hom_nay(ND_ID):
                st.caption("Hôm nay bạn đã đoán. Kết quả được chấm khi có giá phiên mới.")
            else:
                ns_doan = st.segmented_control("Nông sản", ["Lúa", "Cà phê", "Hồ tiêu"], default="Lúa",
                                               key="nt_ns_doan", label_visibility="collapsed") or "Lúa"
                st.caption(f"Giá trung bình {ns_doan.lower()} phiên tới so với phiên mới nhất sẽ…")
                for o, (ma, chu) in zip(st.columns(3), [("tang", "▲ Tăng"), ("ngang", "＝ Ngang"),
                                                        ("giam", "▼ Giảm")]):
                    if o.button(chu, key=f"doan_{ma}", width="stretch"):
                        ok, tb = nt.doan_gia(ND_ID, df, ns_doan, ma)
                        (bao if ok else st.error)(tb)
                        if ok:
                            st.rerun()
            html(gd.lich_su_doan(nt.du_doan_gan_day(ND_ID, 4)))
        with cot_kho:
            html(gd.the_kho(nt.nguoi_choi(ND_ID)["kho"], nt.CAY))



# ================================================================ DIỄN ĐÀN
LA_QT = xt.la_quan_tri(ND_ID)


@st.cache_data(max_entries=400)
def anh_hien_thi_b64(anh: bytes, co: int = 960) -> str:
    """Ảnh thu nhỏ (base64) để hiện trong bài / sản phẩm cho nhẹ trang."""
    im = Image.open(io.BytesIO(anh)).convert("RGB")
    im.thumbnail((co, co))
    bo_dem = io.BytesIO()
    im.save(bo_dem, format="JPEG", quality=82, optimize=True)
    return base64.b64encode(bo_dem.getvalue()).decode()


def luoi_anh(cac_anh: list, khoa: str):
    """Khung ảnh kiểu Facebook: 1 ảnh · 2 ảnh cạnh nhau · 3 ảnh (giữa to, 2 bên nhỏ) · 4 ảnh lưới · 5+ ảnh có ô +N.
    Bấm vào ảnh để xem to, bấm ✕ hoặc ra ngoài để đóng."""
    if cac_anh:
        html(gd.khung_anh([anh_hien_thi_b64(a) for a in cac_anh], khoa))


def _anh_tac_gia(anh) -> str:
    return anh_nho_b64(anh, 96) if anh else ""


def nut_tuy_chon(loai: str, muc: dict, khoa: str):
    """Nút ⋯ cạnh mỗi nội dung: xoá (của mình / quản trị) · báo cáo · khôi phục (quản trị)."""
    with st.popover("⋯", help="Tuỳ chọn"):
        la_minh = muc["nguoi_dung_id"] == ND_ID
        if la_minh or LA_QT:
            if st.button("🗑️ Xoá" + ("" if la_minh else " (quản trị)"), key=f"dd_xoa_{khoa}", width="stretch"):
                ok, tb = dd.xoa(ND_ID, loai, muc["id"], LA_QT)
                (bao if ok else st.error)(tb)
                if ok:
                    st.rerun()
        if not la_minh:
            if st.button("🚩 Báo cáo", key=f"dd_bc_{khoa}", width="stretch"):
                ok, tb = dd.bao_cao(ND_ID, loai, muc["id"])
                (bao if ok else st.error)(tb)
                if ok:
                    st.rerun()
        if LA_QT and muc.get("an"):
            if st.button("👁️ Hiện lại", key=f"dd_kp_{khoa}", width="stretch"):
                bao(dd.khoi_phuc(loai, muc["id"])[1])
                st.rerun()


@st.dialog("Sản phẩm", width="large")
def hop_dat_hang(sp_id: int):
    """Hộp sản phẩm: xem chi tiết & hướng dẫn → điền giao hàng → thanh toán (chế độ thử)."""
    ma = st.session_state.get("dd_ma_don")
    d = dd.lay_don_cho(ma) if ma else None
    if d and d["trang_thai"] == "cho":                       # bước 2: thanh toán (chế độ thử)
        trai, phai = st.columns([1, 1.5], vertical_alignment="center")
        with trai:
            html(gd.qr_mau(d["ma_don"]))
            st.caption("Mã QR mẫu (chế độ thử) — không quét được")
        with phai:
            html("".join(f'<div class="tt-dong"><span>{a}</span><b>{b}</b></div>' for a, b in [
                ("Sản phẩm", f"{gd.e(d['ten_sp'])} × {d['so_luong']} {gd.e(d['don_vi'])}"),
                ("Số tiền", vx.tien(d["so_tien"])),
                ("Giao đến", f"{gd.e(d['ho_ten'])} · {gd.e(d['so_dien_thoai'])}"),
                ("Địa chỉ", gd.e(d["dia_chi"])),
                ("Nội dung chuyển khoản", f"BONONG {d['ma_don']}"),
                ("Giữ đơn đến", f"{d['het_han_luc']:%H:%M %d/%m/%Y}")]))
        if vx.CHE_DO_THU:
            html('<div class="che-do-thu"><b>Chế độ thử:</b> ứng dụng chưa thu tiền thật và chưa giao hàng thật. '
                 'Bấm <b>Giả lập đã thanh toán</b> để xem đơn hàng chạy như thế nào.</div>')
        b1, b2 = st.columns(2)
        if vx.CHE_DO_THU and b1.button("✅ Giả lập đã thanh toán", type="primary", width="stretch", key="dd_gia_lap"):
            ok, tb = dd.gia_lap_thanh_toan_don(ND_ID, d["ma_don"])
            st.session_state.pop("dd_ma_don", None)
            (bao if ok else st.error)(tb)
            if ok:
                st.balloons()
                st.rerun()
        if b2.button("Huỷ đơn", width="stretch", key="dd_huy_don"):
            bao(dd.huy_don_cho(ND_ID, d["ma_don"])[1])
            st.session_state.pop("dd_ma_don", None)
            st.rerun()
        return
    sp = dd.lay_san_pham(sp_id)
    if not sp:
        st.warning("Sản phẩm không còn.")
        return
    cac_anh = [a for _, a in dd.anh_san_pham(sp_id)]
    if st.session_state.get("dd_buoc") != "dat":           # bước 0: xem chi tiết sản phẩm
        trai, phai = st.columns([1, 1.15], gap="large")
        with trai:
            if cac_anh:
                luoi_anh(cac_anh[:1], f"spct_{sp_id}")
                if len(cac_anh) > 1:
                    luoi_anh(cac_anh[1:], f"spct2_{sp_id}")
            else:
                html(gd.the_san_pham(sp))
        with phai:
            html(gd.dau_chi_tiet_sp(sp))
            if sp["con_hang"] and not sp["an"]:
                if st.button("🛒 Đặt hàng sản phẩm này", type="primary", width="stretch", key="dd_sang_dat"):
                    st.session_state.dd_buoc = "dat"
                    st.rerun(scope="fragment")
            else:
                st.warning("Sản phẩm đang tạm hết hàng.")
        t1, t2, t3 = st.tabs(["📋 Chi tiết sản phẩm", "🧑‍🌾 Hướng dẫn sử dụng", "⚠️ Lưu ý an toàn"])
        t1.markdown(sp.get("chi_tiet") or sp["mo_ta"] or "Đang cập nhật.")
        t2.markdown(sp.get("huong_dan") or "Đang cập nhật. Vui lòng làm theo hướng dẫn trên bao bì.")
        t3.markdown(sp.get("luu_y") or "Đọc kỹ nhãn trước khi dùng. Để xa tầm tay trẻ em.")
        st.caption("Liều lượng chỉ để tham khảo — luôn làm theo nhãn trên bao bì và hướng dẫn của cán bộ khuyến nông địa phương.")
        return
    if st.button("← Quay lại xem sản phẩm", key="dd_quay_lai"):     # bước 1: điền thông tin giao hàng
        st.session_state.dd_buoc = "xem"
        st.rerun(scope="fragment")
    html(gd.the_san_pham(sp, anh_nho_b64(cac_anh[0], 480) if cac_anh else ""))
    hs = ho_so_hien_tai()
    with st.form("dd_form_dat"):
        c1, c2 = st.columns([1, 2])
        sl = c1.number_input(f"Số lượng ({sp['don_vi']})", min_value=1, max_value=999, value=1, step=1)
        c2.markdown(f"<div style='padding-top:30px'>Tạm tính: <b style='color:#C2410C;font-size:1.2rem'>"
                    f"{gd.so(sp['gia'])} đ × số lượng</b></div>", unsafe_allow_html=True)
        ho_ten = st.text_input("Họ tên người nhận", value=hs.get("ho_ten") or st.session_state.nguoi_dung["ho_ten"])
        sdt = st.text_input("Số điện thoại", value=hs.get("so_dien_thoai") or "", placeholder="0912 345 678")
        dia_chi = st.text_input("Địa chỉ giao hàng", value=hs.get("tinh") or "",
                                placeholder="Số nhà / ấp, xã, huyện, tỉnh")
        ghi_chu = st.text_input("Ghi chú (không bắt buộc)", placeholder="Ví dụ: giao buổi sáng")
        if st.form_submit_button("Tạo đơn hàng", type="primary", width="stretch"):
            ok, kq = dd.tao_don_cho(ND_ID, sp_id, sl, ho_ten, sdt, dia_chi, ghi_chu)
            if ok:
                st.session_state.dd_ma_don = kq
                st.rerun(scope="fragment")
            st.error(kq)


@st.dialog("Sản phẩm", width="large")
def hop_sua_san_pham(sp_id):
    sp = dd.lay_san_pham(sp_id) if sp_id else {"ten": "", "danh_muc": dd.DANH_MUC[0], "gia": 100_000, "don_vi": "",
                                               "mo_ta": "", "phu_hop": "", "con_hang": 1, "an": 0, "anh": None,
                                               "chi_tiet": "", "huong_dan": "", "luu_y": ""}
    st.markdown("#### " + ("Sửa sản phẩm" if sp_id else "Thêm sản phẩm mới"))
    with st.form("dd_form_sp"):
        ten = st.text_input("Tên sản phẩm", value=sp["ten"])
        c1, c2, c3 = st.columns(3)
        dm = c1.selectbox("Danh mục", dd.DANH_MUC, index=dd.DANH_MUC.index(sp["danh_muc"])
                          if sp["danh_muc"] in dd.DANH_MUC else 0)
        gia = c2.number_input("Giá (đồng)", min_value=1, max_value=1_000_000_000, value=int(sp["gia"]), step=1000)
        don_vi = c3.text_input("Đơn vị tính", value=sp["don_vi"], placeholder="bao 50 kg")
        mo_ta = st.text_area("Mô tả ngắn", value=sp["mo_ta"], height=90)
        phu_hop = st.text_input("Hợp với cây", value=sp["phu_hop"], placeholder="Lúa, Cà phê, Hồ tiêu")
        st.caption("Ba ô dưới viết được gạch đầu dòng: bắt đầu dòng bằng “- ” hoặc “1. ”; chữ đậm: **chữ**.")
        chi_tiet = st.text_area("📋 Chi tiết sản phẩm (thành phần, quy cách, công dụng)", value=sp.get("chi_tiet") or "", height=120)
        huong_dan = st.text_area("🧑‍🌾 Hướng dẫn sử dụng", value=sp.get("huong_dan") or "", height=140)
        luu_y = st.text_area("⚠️ Lưu ý an toàn", value=sp.get("luu_y") or "", height=100)
        c4, c5 = st.columns(2)
        con_hang = c4.checkbox("Còn hàng", value=bool(sp["con_hang"]))
        an = c5.checkbox("Ẩn khỏi Chợ", value=bool(sp["an"]))
        hien_co = dd.anh_san_pham(sp_id) if sp_id else []
        xoa_ids = []
        if hien_co:
            st.markdown(f"**Ảnh hiện có ({len(hien_co)})** · tích vào ảnh muốn xoá")
            for i in range(0, len(hien_co), 4):
                for o, (aid, a) in zip(st.columns(4), hien_co[i:i + 4]):
                    o.image(a, width="stretch")
                    if o.checkbox("Xoá ảnh này", key=f"dd_xoa_anh_sp_{aid}_{i}"):
                        xoa_ids.append(aid)
        anh = st.file_uploader(f"Thêm ảnh sản phẩm (chọn được nhiều ảnh · tối đa {dd.SO_ANH_SP} ảnh/sản phẩm)",
                               type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if st.form_submit_button("💾 Lưu sản phẩm", type="primary", width="stretch"):
            ok, tb = dd.luu_san_pham(sp_id, ten, dm, gia, don_vi, mo_ta, phu_hop, con_hang, an,
                                     [f.getvalue() for f in (anh or [])], xoa_ids, chi_tiet, huong_dan, luu_y)
            if ok:
                bao(tb)
                st.rerun()
            st.error(tb)


def tab_phong_chat():
    @st.fragment(run_every=5)          # tự nhận tin mới mỗi 5 giây
    def khung():
        ds = dd.ds_tin(60)
        with st.container(height=470, key="khung_chat"):
            if not ds:
                html(gd.chat_trong())
            for t in ds:
                la_minh = t["nguoi_dung_id"] == ND_ID
                o_tin, o_nut = st.columns([24, 1], vertical_alignment="center")
                with o_tin:
                    html(gd.bong_bong_tin(t, la_minh, dd.hang_nguoi(t["nguoi_dung_id"], t["email"]),
                                          _anh_tac_gia(t["anh"]), dd.luc_tuong_doi(t["tao_luc"])))
                with o_nut:
                    nut_tuy_chon("tin", t, f"tin_{t['id']}")
            html('<span id="cuoi-chat"></span>')
        moi_nhat = ds[-1]["id"] if ds else 0
        components.html(f"""<script>/*{moi_nhat}*/
            setTimeout(function() {{
              const d = window.parent.document, a = d.getElementById('cuoi-chat');
              if (!a || window.parent.__bnChat === {moi_nhat}) return;
              window.parent.__bnChat = {moi_nhat};
              for (let e = a.parentElement; e; e = e.parentElement) {{
                const s = getComputedStyle(e).overflowY;
                if ((s === 'auto' || s === 'scroll') && e.scrollHeight > e.clientHeight) {{ e.scrollTop = e.scrollHeight; break; }}
              }}
            }}, 250);</script>""", height=0)
        with st.container(key="dd_o_chat"):
            tin = st.chat_input("Nhắn gì đó cho bà con…", max_chars=dd.DAI_TOI_DA["tin"], key="dd_chat_vao")
        if tin:
            ok, tb = dd.gui_tin(ND_ID, tin)
            if not ok:
                st.toast(tb, icon="⏳")
            st.rerun(scope="fragment")
        st.caption("Tin nhắn hiện với mọi người · gửi cách nhau ít nhất 5 giây · tối đa 100 tin/ngày · "
                   "từ thô tục tự bị che · bấm ⋯ để xoá tin của bạn hoặc báo cáo tin xấu.")

    khung()


NHAN_CHU_DE = {"🌐 Chung": "Chung", "🌾 Lúa": "Lúa", "☕ Cà phê": "Cà phê", "🌿 Hồ tiêu": "Hồ tiêu"}


def o_soan_bai():
    """Ô đăng bài gọn: avatar + câu hỏi · nội dung · chọn chủ đề · thêm ảnh · Đăng."""
    hs = ho_so_hien_tai()
    ten = st.session_state.nguoi_dung["ho_ten"]
    with st.container(key="dd_soan"):
        html(gd.dau_o_soan(ten, ND_ID, _anh_tac_gia(hs.get("anh"))))
        with st.form("dd_form_bai", clear_on_submit=True, border=False):
            noi_dung = st.text_area("Nội dung bài viết", height=96, max_chars=dd.DAI_TOI_DA["bai"],
                                    label_visibility="collapsed",
                                    placeholder=f"{ten.split()[-1]} ơi, chia sẻ giá cả, kinh nghiệm mùa vụ hay câu hỏi với bà con nhé…")
            html('<div class="soan-nhan">Chủ đề</div>')
            nhan = st.segmented_control("Chủ đề", list(NHAN_CHU_DE), default="🌐 Chung", key="dd_cd_moi",
                                        label_visibility="collapsed")
            c_anh, c_dang = st.columns([3, 1], vertical_alignment="center")
            anh = c_anh.file_uploader("Thêm ảnh", type=["jpg", "jpeg", "png"], accept_multiple_files=True,
                                      label_visibility="collapsed", key="dd_anh_moi")
            dang = c_dang.form_submit_button("Đăng bài  ➤", type="primary", width="stretch")
        html(f'<div class="soan-goi-y">📷 Tối đa {dd.SO_ANH_BAI} ảnh · ✍️ tối đa {gd.so(dd.DAI_TOI_DA["bai"])} ký tự · '
             '🤝 Lịch sự, không quảng cáo, từ thô tục tự bị che</div>')
        if dang:
            ok, tb = dd.dang_bai(ND_ID, noi_dung, NHAN_CHU_DE.get(nhan or "", "Chung"), [f.getvalue() for f in (anh or [])])
            if ok:
                bao(tb)
                st.rerun()
            st.error(tb)


def the_bai_viet(b: dict):
    with st.container(key=f"dd_bai_{b['id']}"):
        dau, nut = st.columns([20, 1])
        with dau:
            html(gd.dau_bai(b, dd.hang_nguoi(b["nguoi_dung_id"], b["email"]), _anh_tac_gia(b["anh_nd"]),
                            dd.luc_tuong_doi(b["tao_luc"])))
        with nut:
            nut_tuy_chon("bai", b, f"bai_{b['id']}")
        if b["so_anh"]:
            luoi_anh(dd.anh_bai(b["id"]), f"bai_{b['id']}")
        html(gd.dong_dem_bai(b["so_tim"], b["so_bl"], b["da_tim"]))
        mo = st.session_state.setdefault("dd_mo_bl", set())
        with st.container(key=f"dd_hd_{b['id']}"):
            c1, c2 = st.columns(2, gap="small")
            if c1.button("❤️ Đã thích" if b["da_tim"] else "🤍 Thích", key=f"dd_tim_{b['id']}", width="stretch"):
                dd.tha_tim(ND_ID, b["id"])
                st.rerun()
            if c2.button("💬 Bình luận", key=f"dd_mobl_{b['id']}", width="stretch"):
                mo.symmetric_difference_update({b["id"]})
                st.rerun()
        if b["id"] in mo:
            with st.container(key=f"dd_khung_bl_{b['id']}"):
                for c in dd.ds_binh_luan(b["id"], xem_an=LA_QT):
                    o_bl, o_nut = st.columns([20, 1], vertical_alignment="center")
                    with o_bl:
                        html(gd.dong_binh_luan(c, dd.hang_nguoi(c["nguoi_dung_id"], c["email"]),
                                               _anh_tac_gia(c["anh"]), dd.luc_tuong_doi(c["tao_luc"])))
                    with o_nut:
                        nut_tuy_chon("bl", c, f"bl_{c['id']}")
                with st.form(f"dd_form_bl_{b['id']}", clear_on_submit=True, border=False):
                    o1, o2 = st.columns([6, 1], vertical_alignment="center")
                    bl = o1.text_input("Bình luận", placeholder="Viết bình luận…", label_visibility="collapsed",
                                       max_chars=dd.DAI_TOI_DA["bl"])
                    if o2.form_submit_button("Gửi ➤", width="stretch"):
                        ok, tb = dd.binh_luan(ND_ID, b["id"], bl)
                        if ok:
                            st.rerun()
                        st.error(tb)


def tab_bang_tin():
    trai, phai = st.columns([2.3, 1], gap="large")
    with trai:
        o_soan_bai()
        c_loc, c_xep = st.columns([3, 1.5], vertical_alignment="center")
        loc = c_loc.segmented_control("Lọc chủ đề", ["Tất cả"] + list(NHAN_CHU_DE), default="Tất cả", key="dd_loc",
                                      label_visibility="collapsed") or "Tất cả"
        xep = c_xep.segmented_control("Sắp xếp", ["🕒 Mới nhất", "🔥 Nổi bật"], default="🕒 Mới nhất", key="dd_xep",
                                      label_visibility="collapsed") or "🕒 Mới nhất"
        so_hien = st.session_state.get("dd_so_bai", 10)
        ds = dd.ds_bai(ND_ID, NHAN_CHU_DE.get(loc), "tim" if "Nổi" in xep else "moi", so_hien, xem_an=LA_QT)
        if not ds:
            html('<div class="dd-trong"><div class="dd-trong-icon">📰</div><b>Chưa có bài viết nào</b>'
                 '<span>Hãy là người đầu tiên chia sẻ với bà con!</span></div>')
        with st.container(key="dd_bang_tin"):
            for b in ds[:so_hien]:
                the_bai_viet(b)
        if len(ds) > so_hien and st.button("Xem thêm bài viết", width="stretch", key="dd_xem_them"):
            st.session_state.dd_so_bai = so_hien + 10
            st.rerun()
    with phai:
        tv = dd.thanh_vien_moi(5)
        html(gd.cot_phai_dien_dan(dd.ds_bai(ND_ID, None, "tim", 3), tv, {t["id"]: _anh_tac_gia(t["anh"]) for t in tv}))


def tab_cho():
    c_tim, c_dm = st.columns([1.3, 2.7], vertical_alignment="center")
    tu_khoa = c_tim.text_input("Tìm sản phẩm", placeholder="🔍 Tìm phân bón, thuốc, giống…", label_visibility="collapsed",
                               key="dd_tim_sp")
    dm = c_dm.segmented_control("Danh mục", ["Tất cả"] + dd.DANH_MUC, default="Tất cả", key="dd_dm",
                                label_visibility="collapsed") or "Tất cả"
    if LA_QT and st.button("➕ Thêm sản phẩm", key="dd_them_sp"):
        hop_sua_san_pham(None)
    ds = dd.ds_san_pham(None if dm == "Tất cả" else dm, tu_khoa, xem_an=LA_QT)
    if not ds:
        st.info("Không tìm thấy sản phẩm phù hợp.")
    for i in range(0, len(ds), 3):
        for o, sp in zip(st.columns(3, gap="medium"), ds[i:i + 3]):
            with o:
                html(gd.the_san_pham(sp, anh_nho_b64(sp["anh"], 480) if sp["anh"] else ""))
                n1, n2 = st.columns(2, gap="small")
                if n1.button("🔍 Xem chi tiết", key=f"dd_xem_{sp['id']}", width="stretch"):
                    st.session_state.pop("dd_ma_don", None)
                    st.session_state.dd_buoc = "xem"
                    hop_dat_hang(sp["id"])
                if n2.button("🛒 Đặt hàng" if sp["con_hang"] else "Hết hàng", key=f"dd_mua_{sp['id']}",
                             width="stretch", disabled=not sp["con_hang"] or bool(sp["an"])):
                    st.session_state.pop("dd_ma_don", None)
                    st.session_state.dd_buoc = "dat"
                    hop_dat_hang(sp["id"])
                if LA_QT and st.button("✏️ Sửa sản phẩm", key=f"dd_sua_{sp['id']}", width="stretch"):
                    hop_sua_san_pham(sp["id"])
    don = dd.ds_don(ND_ID, 20)
    with st.expander(f"📦 Đơn hàng của tôi ({len(don)})"):
        if not don:
            st.caption("Bạn chưa có đơn hàng nào.")
        for d in don:
            html(gd.the_don_cho(d, dd.TRANG_THAI_DON[d["trang_thai"]]))
            if d["trang_thai"] == "cho" and st.button(f"Tiếp tục thanh toán đơn {d['ma_don']}", key=f"dd_tt_{d['ma_don']}"):
                st.session_state.dd_ma_don = d["ma_don"]
                st.session_state.dd_buoc = "dat"
                hop_dat_hang(d["san_pham_id"])
    st.caption("Chợ do Bồ Nông quản lý · giá là giá mẫu · đơn hàng đang ở chế độ thử, chưa thu tiền và chưa giao hàng thật.")


def tab_quan_tri():
    st.markdown("#### 🚩 Nội dung bị ẩn do báo cáo")
    an = dd.ds_bi_an()
    if not an:
        st.caption("Không có nội dung nào bị ẩn.")
    for m in an:
        o1, o2, o3 = st.columns([6, 1, 1], vertical_alignment="center")
        o1.markdown(f"**{dd.TEN_LOAI[m['loai']].capitalize()}** của **{m['ho_ten']}** · {m['so_bc']} báo cáo · "
                    f"{dd.luc_tuong_doi(m['tao_luc'])}\n\n> {m['noi_dung'][:200]}")
        if o2.button("Hiện lại", key=f"qt_kp_{m['loai']}_{m['id']}", width="stretch"):
            bao(dd.khoi_phuc(m["loai"], m["id"])[1])
            st.rerun()
        if o3.button("Xoá", key=f"qt_xoa_{m['loai']}_{m['id']}", width="stretch"):
            bao(dd.xoa(ND_ID, m["loai"], m["id"], True)[1])
            st.rerun()
    st.markdown("#### 📦 Đơn hàng Chợ")
    don = dd.ds_don(None, 50)
    if not don:
        st.caption("Chưa có đơn hàng.")
    for d in don:
        o1, o2 = st.columns([6, 1.3], vertical_alignment="center")
        with o1:
            html(gd.the_don_cho(d, dd.TRANG_THAI_DON[d["trang_thai"]]))
        if d["trang_thai"] == "da_tt" and o2.button("Đã giao", key=f"qt_giao_{d['ma_don']}", width="stretch"):
            bao(dd.danh_dau_da_giao(d["ma_don"])[1])
            st.rerun()


def trang_dien_dan():
    try:
        so_anh_moi = dd.nap_anh_va_huong_dan()   # ảnh mới trong data/anh_san_pham + hướng dẫn mẫu
        if so_anh_moi and LA_QT:
            st.toast(f"Đã nạp {so_anh_moi} ảnh sản phẩm mới từ thư mục data/anh_san_pham.", icon="🖼️")
    except Exception as loi:
        st.warning(f"Chưa nạp được ảnh sản phẩm: {loi}")
    html(gd.css_dien_dan())
    html(gd.dau_dien_dan(dd.thong_ke()))
    cac_muc = [("bang_tin", "📰", "Bảng tin", tab_bang_tin), ("chat", "💬", "Phòng chat", tab_phong_chat),
               ("cho", "🛒", "Chợ nông nghiệp", tab_cho)]
    if LA_QT:
        so_an = dd.so_bi_an()
        cac_muc.append(("quan_tri", "🛡️", "Quản trị" + (f" · {so_an}" if so_an else ""), tab_quan_tri))
    chon = st.session_state.get("dd_tab", "bang_tin")
    if chon not in [m[0] for m in cac_muc]:
        chon = "bang_tin"
    with st.container(key="dd_trang"):
        with st.container(key="dd_nav"):
            do_rong = [len(m[2]) + 6 for m in cac_muc]
            for o, (ma, bt, ten, _) in zip(st.columns(do_rong + [max(10, 110 - sum(do_rong))], gap="small"), cac_muc):
                if o.button(f"{bt}  {ten}", key=f"dd_tab_{'on_' if ma == chon else ''}{ma}", width="stretch",
                            type="primary" if ma == chon else "secondary"):
                    st.session_state.dd_tab = ma
                    st.rerun()
        dict((m[0], m[3]) for m in cac_muc)[chon]()

TRANG_CON = {"vi": trang_vi, "vip": trang_vip, "tro_ly": trang_tro_ly, "ca_nhan": trang_ca_nhan,
             "nong_trai": trang_nong_trai, "dien_dan": trang_dien_dan}


def dieu_huong_nhanh():
    """Chuyển trang KHÔNG tải lại cả trang web (nhanh hơn nhiều, nhất là trên Streamlit Cloud).
    Các nút ẩn bên dưới làm việc chuyển trang; một đoạn JavaScript bắt cú bấm vào các đường link
    ?trang=... rồi bấm hộ nút ẩn tương ứng."""
    with st.container(key="nav_an"):
        for ma in ["trang_chu", *TRANG_CON]:
            if st.button(ma, key=f"nav_{ma}"):
                st.query_params.clear()
                if ma != "trang_chu":
                    st.query_params["trang"] = ma
                st.rerun()
    html("<style>.st-key-nav_an { display:none !important; }</style>")
    components.html("""<script>
    (function () {
      const w = window.parent, d = w.document;
      if (d.__bnDieuHuong) return;
      d.__bnDieuHuong = true;
      d.addEventListener("click", function (e) {
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return;   // mở tab mới thì để bình thường
        const a = e.target.closest && e.target.closest("a");
        if (!a) return;
        const h = a.getAttribute("href") || "";
        if (!h.startsWith("?")) return;
        const p = new URLSearchParams(h.slice(1));
        let dich = p.get("trang");
        if (!dich) {
          const khoa = [...p.keys()];
          if (khoa.length === 0 || (khoa.length === 1 && khoa[0] === "ns")) dich = "trang_chu"; else return;
        }
        const nut = d.querySelector(".st-key-nav_" + dich + " button");
        if (!nut) return;
        e.preventDefault(); e.stopPropagation();
        nut.click();
        const cuon = d.querySelector('[data-testid="stMain"]') || d.scrollingElement;
        if (cuon) cuon.scrollTo({ top: 0, behavior: "smooth" });
      }, true);
    })();
    </script>""", height=0)


dieu_huong_nhanh()
if st.query_params.get("trang") in TRANG_CON:
    ve_thanh_tren(MAC_DINH)
    TRANG_CON[st.query_params.get("trang")]()
    if st.query_params.get("trang") != "tro_ly":   # trang trợ lý tự đặt chân trang dưới ô hỏi
        chan_trang()
    st.stop()

if "nong_san" not in st.session_state:
    # Mở từ đường link "Chi tiết →" (?ns=…&loai=…&kv=…) thì vào thẳng trang đó
    ns_link = st.query_params.get("ns")
    st.session_state.nong_san = ns_link if ns_link in NONG_SAN else MAC_DINH
    st.session_state.loai_link = st.query_params.get("loai")
    st.session_state.kv_link = st.query_params.get("kv")


def link_chi_tiet(nong_san, loai, khu_vuc):
    return "?" + urlencode({"ns": nong_san, "loai": loai, "kv": khu_vuc})


def vi_tri(ds, gia_tri):
    return ds.index(gia_tri) if gia_tri in ds else 0


nong_san = st.session_state.nong_san
ve_thanh_tren(nong_san)   # Trang chủ · số xu · VIP · tên · Đăng xuất
dam, dam_hon, nhat = gd.CHU_DE[nong_san]

# ================================================================ Đầu trang: logo, rồi 3 thẻ chọn nông sản
html(gd.hero_dau(logo_base64(300), logo_chu_base64(), TEN_APP,
                 "Giá tham khảo thị trường trong nước · cập nhật mỗi ngày · dự báo "
                 "<b>ngày mai</b>, <b>7</b> và <b>30 ngày</b> tới"))

cac_the = [{"ten": ten, "mo_ta": mo_ta, "link": "?" + urlencode({"ns": ten})}
           for ten, mo_ta in NONG_SAN.items()]
html(gd.chon_nong_san(cac_the, nong_san))

for _cb in st.session_state.get("canh_bao_moi", []):
    st.warning(_cb)
if st.session_state.get("canh_bao_moi"):
    st.button("Đã xem cảnh báo", key="da_xem_cb", on_click=lambda: st.session_state.pop("canh_bao_moi", None))


html(f'<div class="ten-nong-san"><span class="hinh-nho">{gd.gon(gd.HINH_VE[nong_san])}</span>'
     f'Giá {TEN_NGAN[nong_san]} hôm nay</div>'
     f'<div class="mo-ta-muc" style="margin:0 0 .4rem">{gd.e(NONG_SAN[nong_san])}</div>')

# --- Chọn giống / khu vực (loại có số liệu mới nhất xếp trước)
phan = df[df["nong_san"] == nong_san]
moi_nhat = phan.groupby("loai")["ngay"].max()
ds_loai = sorted(moi_nhat.index, key=lambda x: (-moi_nhat[x].value, x))
c1, c2, _ = st.columns([1, 1, 1])
loai = c1.selectbox("Giống / loại", ds_loai, disabled=len(ds_loai) == 1,
                    index=vi_tri(ds_loai, st.session_state.get("loai_link")))
ds_khu_vuc = sorted(phan.loc[phan["loai"] == loai, "khu_vuc"].unique())
khu_vuc = c2.selectbox("Khu vực", ds_khu_vuc, disabled=len(ds_khu_vuc) == 1,
                       index=vi_tri(ds_khu_vuc, st.session_state.get("kv_link")))
# giữ đường link luôn khớp với lựa chọn (tải lại trang vẫn đúng chỗ)
st.query_params.update({"ns": nong_san, "loai": loai, "kv": khu_vuc})

chuoi = lay_chuoi_gia(df, nong_san, loai, khu_vuc)
ngay_cuoi = chuoi["ngay"].iloc[-1]
gia_nay = chuoi["gia"].iloc[-1]
if ngay_cuoi < df["ngay"].max():
    st.warning(f"Lưu ý: {loai} chỉ có số liệu đến ngày {ngay_cuoi:%d/%m/%Y}, "
               "nên các mốc dự báo được tính từ ngày đó.")

try:
    kq = tinh_du_bao(nong_san, loai, khu_vuc, dau_vet_du_lieu())
except Exception as loi:
    st.error(f"Không tính được dự báo: {loi}")
    st.stop()

# --- 4 ô giá
html(gd.hang_o_gia(nong_san, loai, khu_vuc, chuoi))
html(f'<div class="chu-thich">Giá ngày {ngay_cuoi:%d/%m/%Y}. Mỗi "phiên" là một ngày có giá.</div>')

# --- 3 ô dự báo
html(gd.tieu_de_muc(
    "Giá dự báo",
    f"Dự báo giá {gd.e(loai.lower())} tại {gd.e(khu_vuc)} dựa trên "
    "diễn biến giá các ngày gần đây. <b>Khoảng có thể (90%)</b>: trong quá khứ, giá thật rơi vào "
    "khoảng này khoảng 9/10 lần."))
KHOA_DB = vx.khoa_du_bao(nong_san, loai, khu_vuc)
XEM_7 = vx.co_quyen(ND_ID, "du_bao_7", KHOA_DB, HANG)     # 7 ngày: Mùa Vàng, hoặc 30 xu
XEM_30 = vx.co_quyen(ND_ID, "du_bao_30", KHOA_DB, HANG)   # 30 ngày: Bội Thu, hoặc 50 xu
XEM_SO_NGAY = 30 if XEM_30 else (7 if XEM_7 else 1)       # số ngày dự báo được xem
o_khoa = {}
if not XEM_7:
    o_khoa[7] = "Từ gói <b>Mùa Vàng</b><br>hoặc mở bằng <b>30 xu</b> (dùng 7 ngày)"
if not XEM_30:
    o_khoa[30] = "Từ gói <b>Bội Thu</b><br>hoặc mở bằng <b>50 xu</b> (dùng 7 ngày)"
html(gd.hang_o_du_bao(kq, gia_nay, MOC_DU_BAO, khoa=o_khoa))
if o_khoa:
    c_mo, c_mo30, c_vip = st.columns(3, vertical_alignment="center")
    if not XEM_7 and c_mo.button("🔓 Mở 7 ngày · 30 xu", type="primary", width="stretch", key="mo_du_bao"):
        hop_mo_khoa("du_bao", KHOA_DB, f"{loai} · {khu_vuc}")
    if c_mo30.button("🔓 Mở cả 30 ngày · 50 xu", width="stretch", key="mo_du_bao_30"):
        hop_mo_khoa("du_bao_30", KHOA_DB, f"{loai} · {khu_vuc}")
    with c_vip:
        html(gd.nut_link("Lên VIP" if HANG == 0 else "Nâng lên Bội Thu", "?trang=vip"))
if HANG < 2:
    _han = vx.han_mo_bang_xu(ND_ID, "du_bao_30" if XEM_30 else "du_bao_7", KHOA_DB)
    if _han:
        html(gd.da_mo_khoa(f"Đã mở bằng xu: dự báo {'7 & 30' if XEM_30 else '7'} ngày cho "
                           f"{gd.e(loai)} · {gd.e(khu_vuc)} đến {_han:%H:%M %d/%m/%Y}"))
html(gd.ghi_chu_gia(nong_san))

# --- Cảnh báo giá tuỳ chọn (Bội Thu trở lên)
if HANG >= vx.HANG_TOI_THIEU["canh_bao"]:
    with st.expander("🔔 Cảnh báo giá tuỳ chọn — báo khi giá chạm mức bạn đặt"):
        with st.form("form_canh_bao", clear_on_submit=False, border=False):
            k1, k2, k3 = st.columns([1.2, 1, 0.8], vertical_alignment="bottom")
            kieu = k1.selectbox("Báo khi giá", ["lên từ", "xuống còn"], key="cb_kieu")
            nguong = k2.number_input("Mức giá (đ/kg)", min_value=0, value=int(gia_nay), step=100, key="cb_nguong")
            if k3.form_submit_button("Đặt cảnh báo", type="primary", width="stretch"):
                ok, tb = vx.them_canh_bao(ND_ID, nong_san, loai, khu_vuc,
                                          "tren" if kieu == "lên từ" else "duoi", nguong)
                (bao(tb) or st.rerun()) if ok else st.error(tb)
        ds_cb = vx.ds_canh_bao(ND_ID)
        st.caption(f"Kiểm tra mỗi khi có phiên giá mới · tối đa {vx.SO_CANH_BAO_TOI_DA} cảnh báo · "
                   f"bạn đang đặt {len(ds_cb)}.")
        for cb in ds_cb:
            a, b = st.columns([5, 1], vertical_alignment="center")
            a.markdown(f"**{cb['loai']} · {cb['khu_vuc']}** — báo khi giá "
                       f"{'≥' if cb['kieu'] == 'tren' else '≤'} **{gd.so(cb['nguong'])} đ/kg**")
            if b.button("Xoá", key=f"xoa_cb_{cb['id']}", width="stretch"):
                vx.xoa_canh_bao(ND_ID, cb["id"])
                st.rerun()

# ---------------------------------------------------------------- Biểu đồ
ten_bd = f"{TEN_NGAN[nong_san]} {khu_vuc}" if nong_san != "Lúa" else loai.replace("Lúa tươi ", "lúa ")
html(gd.tieu_de_muc(
    f"Biểu đồ giá {ten_bd} theo ngày",
    "Chọn mốc 7, 30 hoặc 90 ngày để xem xu hướng. Di chuột hoặc chạm vào đường giá để xem "
    "mức giá và ngày tại từng thời điểm. Đường nét đứt màu cam là giá dự báo."))

with st.container(border=True):
    so_ngay_xem = st.segmented_control(
        "Khoảng thời gian", options=[7, 30, 90, 365, 0], default=90,
        format_func=lambda x: {365: "1 năm 🔒", 0: "Tất cả 🔒"}.get(x, f"{x} ngày") if not VIP
        else {365: "1 năm", 0: "Tất cả"}.get(x, f"{x} ngày"),
        label_visibility="collapsed")
    so_ngay_xem = 90 if so_ngay_xem is None else so_ngay_xem
    if so_ngay_xem in (365, 0) and not VIP:
        han_ls = vx.mo_khoa_con_han(ND_ID, "lich_su", nong_san)
        if han_ls:
            html(gd.da_mo_khoa(f"Đã mở lịch sử giá {TEN_NGAN[nong_san]} đến {han_ls:%H:%M %d/%m/%Y}"))
        else:
            html(gd.khung_khoa("Lịch sử giá dài ngày đang bị khoá",
                               f"Mở toàn bộ lịch sử giá {TEN_NGAN[nong_san]} trong 30 ngày với <b>50 xu</b>, "
                               "hoặc xem không giới hạn với <b>VIP</b>. Dưới đây là biểu đồ 90 ngày."))
            k1, k2, _ = st.columns([1.15, 1.15, 1.7])
            if k1.button("🔓 Mở lịch sử · 50 xu", type="primary", width="stretch", key="mo_lich_su"):
                hop_mo_khoa("lich_su", nong_san, f"Toàn bộ lịch sử giá {TEN_NGAN[nong_san]}")
            with k2:
                html(gd.nut_link("Xem gói VIP", "?trang=vip", nhat=True))
            so_ngay_xem = 90
    xem = chuoi if so_ngay_xem == 0 else chuoi[chuoi["ngay"] > ngay_cuoi - pd.Timedelta(days=so_ngay_xem)]
    db = kq.bang.head(min(XEM_SO_NGAY, so_ngay_xem or 30))
    x_noi = [ngay_cuoi] + list(db["ngay"])

    bd = go.Figure()
    bd.add_trace(go.Scatter(
        x=xem["ngay"], y=xem["gia"], mode="lines", name=khu_vuc if nong_san != "Lúa" else loai,
        line=dict(color=gd.DUONG_GIA, width=2.6, shape="linear"),
        fill="tozeroy", fillcolor="rgba(27,127,59,0.08)",
        hovertemplate="%{y:,.0f} đồng/kg<extra></extra>",
    ))
    bd.add_trace(go.Scatter(
        x=x_noi + x_noi[::-1],
        y=[gia_nay] + list(db["cao"]) + (list(db["thap"]) + [gia_nay])[::-1],
        fill="toself", fillcolor="rgba(232,116,59,0.12)", line=dict(width=0),
        name="Khoảng có thể", hoverinfo="skip", showlegend=False,
    ))
    bd.add_trace(go.Scatter(
        x=x_noi[1:], y=list(db["du_bao"]), mode="lines", name="Dự báo",
        line=dict(color=gd.CAM, width=2.4, dash="dash"),
        hovertemplate="Dự báo: %{y:,.0f} đồng/kg<extra></extra>",
    ))
    bd.add_trace(go.Scatter(  # nối liền điểm cuối thật với dự báo
        x=x_noi[:2], y=[gia_nay, db["du_bao"].iloc[0]], mode="lines", showlegend=False,
        line=dict(color=gd.CAM, width=2.4, dash="dash"), hoverinfo="skip",
    ))
    bd.add_trace(go.Scatter(  # chấm ở giá mới nhất
        x=[ngay_cuoi], y=[gia_nay], mode="markers", showlegend=False, hoverinfo="skip",
        marker=dict(color=gd.DUONG_GIA, size=11, line=dict(color="white", width=2.5)),
    ))
    y_min = min(xem["gia"].min(), db["thap"].min())
    y_max = max(xem["gia"].max(), db["cao"].max())
    dem = (y_max - y_min) * 0.08 or y_max * 0.01
    bd.update_layout(
        height=420, margin=dict(l=8, r=8, t=10, b=8), separators=",.",
        plot_bgcolor="white", paper_bgcolor="white", hovermode="x unified",
        font=dict(family="Be Vietnam Pro, sans-serif", color="#3F3833", size=13),
        hoverlabel=dict(bgcolor="#241C17", bordercolor="#241C17",
                        font=dict(color="white", family="Be Vietnam Pro, sans-serif", size=14)),
        showlegend=False,
        yaxis=dict(gridcolor="#EFEAE6", zeroline=False, range=[y_min - dem, y_max + dem],
                   tickformat=",.0f"),
        xaxis=dict(showgrid=False, tickformat="%d/%m", hoverformat="%d/%m/%Y",
                   showspikes=True, spikemode="across", spikethickness=1, spikedash="dot",
                   spikecolor="#B9A99C", linecolor="#E5DED8"),
    )
    st.plotly_chart(bd, config={"displaylogo": False, "displayModeBar": False})
    html(f'<div class="chu-thich">Đơn vị: đồng/kg {gd.e(loai.lower())} tại {gd.e(khu_vuc)}. '
         "Ngày không có báo giá được giữ mức gần nhất."
         + ("" if XEM_SO_NGAY == 30 else f" Đường dự báo chỉ hiện {'ngày mai' if XEM_SO_NGAY == 1 else '7 ngày'}; "
              "mở khoá để xem đủ 30 ngày.") + "</div>")

# ---------------------------------------------------------------- Bảng giá mới nhất
ngay_moi = phan["ngay"].max()
if nong_san == "Lúa":
    cot_ss, ten_cot = "loai", "Giống lúa"
    cung = phan
else:
    cot_ss, ten_cot = "khu_vuc", "Khu vực giá"
    cung = phan[phan["loai"] == loai]

cac_dong = []
for ten, nhom in cung.groupby(cot_ss):
    nhom = nhom.sort_values("ngay")
    if nhom["ngay"].iloc[-1] < ngay_moi:      # chỉ lấy nơi có giá cùng ngày mới nhất
        continue
    if nong_san == "Lúa":
        ten_hien, phu = ten.replace("Lúa tươi ", ""), f"Lúa tươi · {nhom['khu_vuc'].iloc[-1]}"
        link = link_chi_tiet(nong_san, ten, nhom["khu_vuc"].iloc[-1])
        dang_xem = ten == loai
    else:
        ten_hien, phu = gd.tach_ten_khu_vuc(ten, nong_san)
        link = link_chi_tiet(nong_san, loai, ten)
        dang_xem = ten == khu_vuc
    cac_dong.append({"ten": ten_hien, "phu": phu, "gia_nay": nhom["gia"].iloc[-1],
                     "gia_truoc": nhom["gia"].iloc[-2] if len(nhom) > 1 else None,
                     "link": link, "dang_xem": dang_xem})
cac_dong.sort(key=lambda d: -d["gia_nay"])

ten_ds = ", ".join(d["ten"] for d in cac_dong)
html(gd.tieu_de_muc(
    f"Bảng giá {TEN_NGAN[nong_san]} trong nước ngày {ngay_moi:%d/%m/%Y}",
    f"Giá {TEN_NGAN[nong_san]} mới nhất tại {gd.e(ten_ds)} — những "
    f"{'giống' if nong_san == 'Lúa' else 'khu vực'} đang có dữ liệu từ nguồn — kèm mức tăng giảm "
    "so với phiên trước. Bấm <b>Chi tiết →</b> để xem biểu đồ và dự báo của từng nơi."))
lan_cuoi = doc_trang_thai().get("lan_cuoi")
chan = (f"Đơn vị: đồng/kg {gd.e(loai.lower()) if nong_san != 'Lúa' else 'lúa tươi'} · "
        f"Báo giá ngày {ngay_moi:%d/%m/%Y}"
        + (f" · Cập nhật {pd.Timestamp(lan_cuoi):%H:%M} ngày {pd.Timestamp(lan_cuoi):%d/%m/%Y}"
           if lan_cuoi else "") + ".")
html(gd.bang_gia_hom_nay(cac_dong, ten_cot, f"Giá {TEN_NGAN[nong_san]} hôm nay", chan))

# --- Thông báo biến động (Mùa Vàng trở lên): ngay dưới bảng giá trong nước
if HANG >= vx.HANG_TOI_THIEU["thong_bao"]:
    _bd = pt.bien_dong(df, 0.5)
    html(gd.the_bien_dong(_bd, f"Phiên mới nhất · {df['ngay'].max():%d/%m/%Y}"))
    if _bd and not st.session_state.get("da_bao_bien_dong"):
        st.session_state.da_bao_bien_dong = True
        st.toast(f"Có {len(_bd)} biến động giá đáng chú ý ở phiên mới nhất.", icon="🔔")

# ---------------------------------------------------------------- Giá cà phê thế giới
if nong_san == "Cà phê":
    tg = tai_the_gioi(dau_vet_du_lieu())
    if not tg.empty:
        html(gd.tieu_de_muc(
            "Giá cà phê thế giới",
            "Giá kỳ hạn <b>Robusta sàn London</b> (USD/tấn) và <b>Arabica sàn New York</b> (cent/lb). "
            "Cà phê Việt Nam chủ yếu là Robusta nên giá trong nước đi rất sát giá London: biến động "
            "London phiên hôm trước thường phản ánh vào giá trong nước sáng hôm sau."))
        html(gd.hang_o_the_gioi(tg))
        st.write("")
        if not VIP:
            html(gd.khung_khoa("Biểu đồ giá cà phê thế giới dành cho VIP",
                               "Gói Miễn phí xem giá mới nhất ở các ô phía trên. Lên <b>VIP</b> để xem "
                               "biểu đồ đầy đủ theo thời gian."))
            _, k_vip, _ = st.columns([1, 1.2, 1])
            with k_vip:
                html(gd.nut_link("Xem gói VIP", "?trang=vip"))
        else:
            with st.container(border=True):
                so_ngay_tg = st.segmented_control(
                    "Khoảng thời gian (thế giới)", options=[90, 180, 365, 0], default=180, key="tg_khoang",
                    format_func=lambda x: "Tất cả" if x == 0 else f"{x} ngày",
                    label_visibility="collapsed")
                so_ngay_tg = 180 if so_ngay_tg is None else so_ngay_tg
                tg_xem = tg if so_ngay_tg == 0 else tg[tg["ngay"] > tg["ngay"].max() - pd.Timedelta(days=so_ngay_tg)]
                # để trống những đoạn thiếu số liệu (không tự nối liền)
                day_du = pd.date_range(tg_xem["ngay"].min(), tg_xem["ngay"].max())
                tg_xem = tg_xem.set_index("ngay").reindex(day_du)
                tg_xem.index.name = "ngay"
                tg_xem = tg_xem.reset_index()
                cot_r, cot_a = st.columns(2)
                for o, cot, ten, don_vi, mau in [(cot_r, "robusta", "Robusta · London", "USD/tấn", "#5B3A24"),
                                                  (cot_a, "arabica", "Arabica · New York", "cent/lb", "#C2570C")]:
                    bd_tg = go.Figure(go.Scatter(
                        x=tg_xem["ngay"], y=tg_xem[cot], mode="lines", connectgaps=False,
                        line=dict(color=mau, width=2.2), fill="tozeroy",
                        fillcolor="rgba(91,58,36,0.07)" if cot == "robusta" else "rgba(194,87,12,0.07)",
                        hovertemplate=f"%{{y:,.{0 if cot == 'robusta' else 2}f}} {don_vi}<extra></extra>"))
                    s_ok = tg_xem[cot].dropna()
                    dem = (s_ok.max() - s_ok.min()) * 0.08 if len(s_ok) else 0
                    bd_tg.update_layout(
                        title=dict(text=f"{ten} ({don_vi})", font=dict(size=15)), height=330,
                        margin=dict(l=8, r=8, t=44, b=8), separators=",.", plot_bgcolor="white",
                        paper_bgcolor="white", hovermode="x unified", showlegend=False,
                        font=dict(family="Be Vietnam Pro, sans-serif", color="#3F3833", size=12),
                        hoverlabel=dict(bgcolor="#241C17", font=dict(color="white")),
                        yaxis=dict(gridcolor="#EFEAE6", range=[s_ok.min() - dem, s_ok.max() + dem]
                                   if len(s_ok) else None),
                        xaxis=dict(showgrid=False, tickformat="%d/%m/%y", hoverformat="%d/%m/%Y"))
                    o.plotly_chart(bd_tg, config={"displaylogo": False, "displayModeBar": False},
                                   key=f"bd_{cot}")
                # báo những đoạn thiếu số liệu dài hơn 5 ngày
                co = tg_xem.dropna(subset=["robusta"])["ngay"]
                khoang_trong = [(a, b) for a, b in zip(co[:-1], co[1:]) if (b - a).days > 5]
                chu_trong = "; ".join(f"{a + pd.Timedelta(days=1):%d/%m/%Y} – {b - pd.Timedelta(days=1):%d/%m/%Y}"
                                      for a, b in khoang_trong)
                html('<div class="chu-thich">Kỳ hạn là tháng giao hàng của hợp đồng đang giao dịch nhiều '
                     'nhất. Ngày cuối tuần giữ giá phiên gần nhất.'
                     + (f" <b>Chưa có số liệu:</b> {chu_trong} (đoạn để trống trên biểu đồ)." if chu_trong else "")
                     + "</div>")

# ---------------------------------------------------------------- Giá hồ tiêu thế giới
if nong_san == "Hồ tiêu":
    tgt = tai_tieu_the_gioi(dau_vet_du_lieu())
    if not tgt.empty:
        ngay_tgt = tgt["ngay"].max()
        html(gd.tieu_de_muc(
            "Giá hồ tiêu thế giới",
            "Giá <b>xuất khẩu hồ tiêu</b> (FOB, USD/tấn) của Việt Nam, Indonesia, Brazil và Malaysia do "
            "Cộng đồng Hồ tiêu Quốc tế (<b>IPC</b>) công bố. Giá IPC thường đổi theo từng đợt, giúp nhìn "
            "xu hướng chung và so sánh sức cạnh tranh của tiêu Việt Nam."))
        html(gd.hang_o_tieu_the_gioi(tgt))
        st.write("")
        html(gd.bang_tieu_cac_nuoc(
            tgt, f"Đơn vị: USD/tấn, giá FOB · Số liệu ngày {ngay_tgt:%d/%m/%Y}. "
                 "*Tiêu đen so với tiêu đen Việt Nam 500 g/l; tiêu trắng so với tiêu trắng ASTA Việt Nam. "
                 "Ngày không có báo giá mới giữ giá gần nhất."))
        st.write("")
        if not VIP:
            html(gd.khung_khoa("Biểu đồ giá hồ tiêu thế giới dành cho VIP",
                               "Gói Miễn phí xem giá mới nhất ở các ô phía trên. Lên <b>VIP</b> để xem "
                               "biểu đồ đầy đủ theo thời gian."))
            _, k_vip, _ = st.columns([1, 1.2, 1])
            with k_vip:
                html(gd.nut_link("Xem gói VIP", "?trang=vip"))
        else:
            with st.container(border=True):
                c_loai_t, c_khoang_t = st.columns([1, 1.4])
                with c_loai_t:
                    nhom_t = st.segmented_control(
                        "Loại tiêu", options=["Tiêu đen", "Tiêu trắng"], default="Tiêu đen",
                        key="tgt_nhom", label_visibility="collapsed") or "Tiêu đen"
                with c_khoang_t:
                    so_ngay_tgt = st.segmented_control(
                        "Khoảng thời gian (tiêu thế giới)", options=[90, 180, 365, 0], default=365,
                        key="tgt_khoang", format_func=lambda x: "Tất cả" if x == 0 else f"{x} ngày",
                        label_visibility="collapsed")
                    so_ngay_tgt = 365 if so_ngay_tgt is None else so_ngay_tgt
                xem_t = tgt[tgt["loai"].str.startswith(nhom_t)]
                if so_ngay_tgt:
                    xem_t = xem_t[xem_t["ngay"] > ngay_tgt - pd.Timedelta(days=so_ngay_tgt)]
                bd_t = go.Figure()
                for i, ((qg, loai), g) in enumerate(sorted(xem_t.groupby(["quoc_gia", "loai"]),
                                                           key=lambda x: x[0][0] != "Việt Nam")):
                    la_vn = qg == "Việt Nam"
                    bd_t.add_trace(go.Scatter(
                        x=g["ngay"], y=g["gia"], mode="lines", name=f"{qg} · {loai}",
                        line=dict(color=gd.MAU_KHU_VUC[i % len(gd.MAU_KHU_VUC)], width=3 if la_vn else 1.8,
                                  shape="hv", dash=None if la_vn else "solid"),
                        opacity=1 if la_vn else 0.75,
                        hovertemplate=f"{qg} · {loai}: " + "%{y:,.0f} USD/tấn<extra></extra>"))
                bd_t.update_layout(
                    height=400, margin=dict(l=8, r=8, t=16, b=8), separators=",.", plot_bgcolor="white",
                    paper_bgcolor="white", hovermode="x unified",
                    font=dict(family="Be Vietnam Pro, sans-serif", color="#3F3833", size=12),
                    hoverlabel=dict(bgcolor="#241C17", font=dict(color="white")),
                    legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0),
                    yaxis=dict(gridcolor="#EFEAE6", title="USD/tấn"),
                    xaxis=dict(showgrid=False, tickformat="%d/%m/%y", hoverformat="%d/%m/%Y"))
                st.plotly_chart(bd_t, config={"displaylogo": False, "displayModeBar": False}, key="bd_tieu_tg")
                html('<div class="chu-thich">Đường đậm là tiêu Việt Nam. Giá theo ngày báo đăng tin; '
                     'ngày không có báo giá mới giữ giá gần nhất.</div>')

# ---------------------------------------------------------------- Chi tiết
st.write("")
the_bang, the_nguon = st.tabs(["📅 Bảng dự báo 30 ngày", "📚 Nguồn dữ liệu"])

with the_bang:
    bang = kq.bang.copy()
    bang["thay_doi"] = ((bang["du_bao"] - gia_nay) / gia_nay * 100).map(gd.phan_tram)
    bang["ngay"] = bang["ngay"].dt.strftime("%d/%m/%Y")
    bang = bang[["ngay", "du_bao", "thay_doi", "thap", "cao"]]
    bang.columns = ["Ngày", "Giá dự báo (đ/kg)", "So với hiện tại",
                    "Thấp nhất có thể", "Cao nhất có thể"]
    if XEM_SO_NGAY > 1:
        st.dataframe(bang.head(XEM_SO_NGAY), hide_index=True, width="stretch",
                     height=min(360, 38 + 35 * XEM_SO_NGAY))
    if XEM_SO_NGAY < 30:
        html(gd.khung_khoa(f"Bảng dự báo {'30 ngày' if XEM_SO_NGAY == 1 else 'từ ngày 8 đến 30'} đang bị khoá",
                           "Mở bằng xu ở phần Giá dự báo phía trên, hoặc lên gói <b>"
                           + ("Mùa Vàng</b> (7 ngày) / <b>Bội Thu</b> (30 ngày)." if XEM_SO_NGAY == 1
                              else "Bội Thu</b> để xem đủ 30 ngày.")))
    # Xuất báo cáo: chỉ gói Đại Điền (và Nhóm)
    if HANG >= vx.HANG_TOI_THIEU["bao_cao"]:
        st.markdown("**📄 Xuất báo cáo**")
        x1, x2, _ = st.columns([1.3, 1.3, 1.4])
        tg_bc = tai_the_gioi(dau_vet_du_lieu()) if nong_san == "Cà phê" else None
        x1.download_button(
            "⬇️ Báo cáo đầy đủ (in ra PDF)",
            data=pt.bao_cao_html(TEN_APP, nong_san, loai, khu_vuc, chuoi, kq,
                                 pt.phan_tich_gia(TEN_NGAN[nong_san], chuoi, kq, 30, tg_bc),
                                 st.session_state.nguoi_dung["ho_ten"]),
            file_name=f"bao_cao_{nong_san}_{loai}_{khu_vuc}.html".replace(" ", "_").replace("/", "-"),
            mime="text/html", width="stretch", key="tai_bao_cao")
        bang_tai = bang.copy()
        bang_tai.insert(1, "Nông sản", nong_san)
        bang_tai.insert(2, "Giống / loại", loai)
        bang_tai.insert(3, "Khu vực", khu_vuc)
        x2.download_button(
            "⬇️ Bảng dự báo (mở bằng Excel)",
            data=bang_tai.to_csv(index=False).encode("utf-8-sig"),  # utf-8-sig: Excel hiện đúng tiếng Việt
            file_name=f"du_bao_{nong_san}_{loai}_{khu_vuc}.csv".replace(" ", "_").replace("/", "-"),
            mime="text/csv", width="stretch", key="tai_excel")
        st.caption("Báo cáo mở bằng trình duyệt; bấm Ctrl + P → \"Lưu dưới dạng PDF\" để có file PDF.")
    else:
        html(gd.khung_khoa("Xuất báo cáo · gói Đại Điền",
                           "Tải báo cáo đầy đủ (biểu đồ, phân tích, bảng dự báo 30 ngày) để in hoặc lưu PDF, "
                           "kèm bảng dự báo mở bằng Excel."))

with the_nguon:
    st.markdown(
        "**Lưu ý:** giá nông sản ngắn hạn lên xuống khá ngẫu nhiên. Dự báo cho biết **mức giá hợp lý** "
        "và **khoảng dao động**, không đoán trước được các cú tăng/giảm đột ngột do thời tiết, "
        "thị trường thế giới, chính sách…\n\n"
        "#### Dữ liệu\n"
        f"Giá theo ngày từ **{df['ngay'].min():%d/%m/%Y}** đến **{df['ngay'].max():%d/%m/%Y}**, "
        "đơn vị đồng/kg. Mọi giá được giữ nguyên như dataset gốc; chỉ những ngày bị thiếu hoàn "
        "toàn mới được điền tự động. Tỉnh ghi \"(cũ)\" là tên trước khi sáp nhập; phần \"nay …\" "
        "là tỉnh hiện tại."
    )
    nguon = (phan.dropna(subset=["nguon"]).groupby("nguon").size()
             .reset_index(name="n").sort_values("n", ascending=False))
    nguon.columns = ["Nguồn số liệu", "Số dòng"]
    st.dataframe(nguon, hide_index=True, width="stretch")
    with st.expander("Xem bảng giá gốc từng ngày"):
        goc = chuoi[["ngay", "gia", "trang_thai", "nguon"]].sort_values("ngay", ascending=False)
        goc = goc.assign(ngay=goc["ngay"].dt.strftime("%d/%m/%Y"))
        goc.columns = ["Ngày", "Giá (đ/kg)", "Trạng thái số liệu", "Nguồn"]
        st.dataframe(goc, hide_index=True, width="stretch")

st.write("")
khu_cap_nhat(df)
chan_trang()
