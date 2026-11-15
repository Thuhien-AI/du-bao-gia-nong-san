# -*- coding: utf-8 -*-
"""
Các khối giao diện (HTML + CSS) của trang web.
Mỗi hàm trả về một đoạn HTML; app.py chỉ việc đặt chúng lên trang.
"""

import html as _html
import math
import random

import pandas as pd

# ================================================================ Màu sắc
CAM = "#E8743B"        # mỏ bồ nông (logo)
VANG = "#F2B33D"       # hạt lúa (logo)
CHU = "#1F1A17"
CHU_PHU = "#6B625C"
VIEN = "#EFE7E1"
TANG = "#15803D"
GIAM = "#B91C1C"
DUONG_GIA = "#1B7F3B"  # màu đường giá trên biểu đồ

# Mỗi nông sản một màu chủ đạo: (đậm, đậm hơn, nhạt)
CHU_DE = {
    "Lúa": ("#2F6B22", "#1F4A16", "#F1F7EC"),
    "Cà phê": ("#5B3A24", "#3E2717", "#F7F1EC"),
    "Hồ tiêu": ("#6B2232", "#4A1622", "#FBF1F2"),
}
MAU_KHU_VUC = ["#1B7F3B", "#2563EB", "#C81E4A", "#C2570C", "#0F766E", "#7C3AED", "#A16207"]

BIEU_TUONG = {"Lúa": "🌾", "Cà phê": "☕", "Hồ tiêu": "🌶️"}

SVG_TANG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
            'stroke-linecap="round" stroke-linejoin="round"><polyline points="3 17 9 11 13 15 21 7"/>'
            '<polyline points="15 7 21 7 21 13"/></svg>')
SVG_GIAM = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
            'stroke-linecap="round" stroke-linejoin="round"><polyline points="3 7 9 13 13 9 21 17"/>'
            '<polyline points="15 17 21 17 21 11"/></svg>')
SVG_KHOA = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"><rect x="4.5" y="10.5" width="15" height="10.5" rx="2.5"/>'
            '<path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/><circle cx="12" cy="15.5" r="1.4" fill="currentColor"/></svg>')
SVG_VUONG_MIEN = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 8.5l4.2 3.6L12 5l4.8 7.1L21 8.5l-1.8 '
                  '9.5H4.8L3 8.5z"/><rect x="4.8" y="19" width="14.4" height="2" rx="1"/></svg>')
SVG_SONG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
            'stroke-linecap="round" stroke-linejoin="round"><polyline points="2 12 6 12 9 4 15 20 18 12 22 12"/></svg>')


# ================================================================ Hàm định dạng
def so(x) -> str:
    """84500 -> '84.500'."""
    return f"{x:,.0f}".replace(",", ".")


def phan_tram(x) -> str:
    return f"{x:+.1f}%".replace(".", ",")


def e(chu) -> str:
    """Thoát ký tự đặc biệt để chữ hiện đúng trong HTML."""
    return _html.escape(str(chu))


def gon(ma: str) -> str:
    """Bỏ thụt đầu dòng (Streamlit hiểu dòng thụt vào là code)."""
    return "".join(dong.strip() for dong in ma.splitlines())


# ================================================================ CSS chung
def css(nong_san: str = "Lúa") -> str:
    dam, dam_hon, nhat = CHU_DE.get(nong_san, CHU_DE["Lúa"])
    return gon(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&family=Noto+Serif:wght@500;600;700&display=swap');
:root {{ --dam:{dam}; --dam-hon:{dam_hon}; --nhat:{nhat}; }}
html, body, .stApp, .stMarkdown, button, input, textarea, select,
[data-testid="stWidgetLabel"], [data-baseweb] {{ font-family:'Be Vietnam Pro', system-ui, sans-serif; }}
.block-container {{ padding-top:1.4rem; padding-bottom:3rem; max-width:1180px; }}
#MainMenu, footer {{ visibility:hidden; }}

/* --- Đầu trang --- */
.dau-trang {{ display:flex; align-items:center; gap:14px; }}
.dau-trang img {{ border-radius:16px; box-shadow:0 2px 8px rgba(0,0,0,.08); }}
.dau-trang .ten {{ font-size:1.35rem; font-weight:800; color:{CHU}; line-height:1.2; }}
.dau-trang .phu {{ color:{CHU_PHU}; font-size:.9rem; }}
.ten-nong-san {{ font-family:'Noto Serif', Georgia, serif; font-size:2.1rem; font-weight:700;
                 color:{CHU}; margin:1.1rem 0 .2rem; }}

/* --- Tiêu đề mục --- */
.tieu-de-muc {{ font-family:'Noto Serif', Georgia, serif; font-size:1.75rem; font-weight:500;
                color:{CHU}; border-bottom:2px solid var(--dam-hon); padding-bottom:.45rem;
                margin:2.2rem 0 .6rem; line-height:1.3; }}
.mo-ta-muc {{ color:{CHU_PHU}; font-size:1rem; line-height:1.6; margin-bottom:1rem; }}

/* --- Hàng ô số liệu --- */
.hang-o {{ display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:18px; margin:.6rem 0 .4rem; }}
.hang-o.ba {{ grid-template-columns:repeat(3, minmax(0,1fr)); }}
@media (max-width: 900px) {{ .hang-o, .hang-o.ba {{ grid-template-columns:repeat(2, minmax(0,1fr)); }} }}
@media (max-width: 520px) {{ .hang-o, .hang-o.ba {{ grid-template-columns:1fr; }} }}
.o {{ position:relative; overflow:hidden; background:linear-gradient(180deg,#fff 0%, #FFFBFA 100%);
      border:1px solid {VIEN}; border-radius:18px; padding:22px 24px 20px; min-height:150px;
      box-shadow:0 1px 2px rgba(60,20,20,.04), 0 4px 14px rgba(60,20,20,.04); }}
.o .nhan {{ color:var(--dam); font-size:.82rem; font-weight:700; letter-spacing:.06em;
            text-transform:uppercase; }}
.o .so-lon {{ font-family:'Noto Serif', Georgia, serif; font-size:2.25rem; font-weight:700;
              color:{CHU}; line-height:1.15; margin:.55rem 0 .35rem; position:relative; z-index:1; }}
.o .phu {{ color:{CHU_PHU}; font-size:.95rem; line-height:1.55; position:relative; z-index:1; }}
.o .hinh-chim {{ position:absolute; right:-6px; bottom:-14px; width:96px; height:96px;
                 color:rgba(0,0,0,.07); }}
.o.noi-bat {{ background:linear-gradient(135deg, var(--dam) 0%, var(--dam-hon) 100%); border:none;
              box-shadow:0 6px 18px rgba(0,0,0,.14); }}
.o.noi-bat .nhan {{ color:rgba(255,255,255,.78); }}
.o.noi-bat .so-lon, .o.noi-bat .phu {{ color:#fff; }}
.o.noi-bat .phu {{ opacity:.88; }}
.o.noi-bat .hinh-chim {{ color:rgba(255,255,255,.14); font-size:92px; line-height:1;
                         filter:grayscale(1) brightness(3); opacity:.16; right:6px; bottom:-6px;
                         width:auto; height:auto; }}
.mui-ten {{ font-family:'Be Vietnam Pro', sans-serif; font-weight:700; margin-right:.15em; }}

.o.noi-bat .hinh-ve {{ width:104px; height:104px; right:-8px; bottom:-14px; opacity:.2;
                      filter:brightness(0) invert(1); }}
.o.noi-bat .hinh-ve svg {{ width:100%; height:100%; }}
.ten-nong-san .hinh-nho svg {{ width:44px; height:44px; vertical-align:-7px; margin-right:4px; }}

/* --- Ô dự báo --- */
.o.du-bao .ngay {{ color:{CHU_PHU}; font-size:.88rem; margin-top:.15rem; }}
.o.du-bao .doi {{ font-weight:700; font-size:1rem; margin-bottom:.7rem; }}
.o.du-bao .dong {{ display:flex; justify-content:space-between; gap:10px; font-size:.88rem;
                   border-top:1px dashed {VIEN}; padding-top:.5rem; margin-top:.5rem; }}
.o.du-bao .dong span:first-child {{ color:{CHU_PHU}; }}
.o.du-bao .dong b {{ color:{CHU}; }}
.o.du-bao.chinh {{ border:2px solid {CAM}; background:linear-gradient(180deg,#FFF6EF 0%,#fff 60%); }}
.o.du-bao.chinh .nhan {{ color:{CAM}; }}

/* --- Khung có viền (biểu đồ) --- */
div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius:18px !important;
    border-color:{VIEN} !important; background:#fff; }}
.chu-thich {{ color:{CHU_PHU}; font-size:.88rem; line-height:1.55; }}

/* --- Bảng giá hôm nay --- */
.bang-ss {{ border:1px solid {VIEN}; border-radius:18px; overflow:hidden; background:#fff;
            box-shadow:0 4px 14px rgba(60,20,20,.04); }}
.bang-ss table {{ width:100% !important; border-collapse:collapse !important; margin:0 !important;
                  border:none !important; font-size:1rem; display:table; }}
.bang-ss th, .bang-ss td {{ border:none !important; }}
.bang-ss th {{ background:var(--dam-hon); color:#fff; font-size:.8rem; font-weight:700;
               letter-spacing:.05em; text-transform:uppercase; padding:18px 22px; text-align:left; }}
.bang-ss th.phai, .bang-ss td.phai {{ text-align:right; }}
.bang-ss td {{ padding:16px 22px; border-top:1px solid #F1EAE5 !important; color:{CHU};
               vertical-align:middle; background:#fff; }}
.bang-ss tbody tr:nth-child(even) td {{ background:#FBF9F7; }}
.bang-ss tbody tr.dang-xem td {{ background:#FBF3E4; }}
.bang-ss tbody tr.dang-xem td:first-child {{ box-shadow:inset 4px 0 0 {CAM}; }}
.bang-ss .ten-kv {{ font-weight:700; font-size:1.08rem; color:var(--dam); display:flex;
                    align-items:center; gap:9px; }}
.bang-ss .cham {{ width:10px; height:10px; border-radius:50%; display:inline-block; flex:none; }}
.bang-ss .phu-kv {{ color:{CHU_PHU}; font-size:.9rem; margin:3px 0 0 19px; }}
.bang-ss .gia {{ font-weight:700; font-size:1.08rem; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.bang-ss .gia-truoc {{ font-weight:600; color:#4A423C; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.bang-ss .o-gia {{ display:flex; align-items:center; justify-content:flex-end; gap:10px; }}
.vien-tang, .vien-giam, .vien-ngang {{ display:inline-block; border-radius:999px; padding:4px 11px;
    font-size:.86rem; font-weight:700; white-space:nowrap; font-variant-numeric:tabular-nums; min-width:64px;
    text-align:center; }}
.vien-tang {{ color:{TANG}; background:#E6F4EA; }}
.vien-giam {{ color:{GIAM}; background:#FDECEC; }}
.vien-ngang {{ color:{CHU_PHU}; background:#F2EFEC; }}
.bang-ss a.chi-tiet {{ color:var(--dam); font-weight:700; text-decoration:none; white-space:nowrap; }}
.bang-ss a.chi-tiet:hover {{ text-decoration:underline; }}
.bang-ss .dang-xem-chu {{ color:{CAM}; font-weight:700; font-size:.9rem; white-space:nowrap; }}
.bang-ss .chan {{ padding:14px 22px; color:{CHU_PHU}; font-size:.88rem; border-top:1px solid #F1EAE5; }}
@media (max-width: 640px) {{ .bang-ss .an-nho {{ display:none; }}
    .bang-ss th, .bang-ss td {{ padding:12px 12px; }} }}

/* --- Trang đầu --- */
.hero {{ text-align:center; padding:2rem 1rem 1.2rem; }}
.hero img {{ border-radius:28px; box-shadow:0 6px 24px rgba(232,116,59,.18); }}
.hero h1 {{ font-family:'Noto Serif', Georgia, serif; font-size:2.3rem; font-weight:700;
            color:{CHU}; margin:1rem 0 .3rem; padding:0; }}
.hero p {{ color:{CHU_PHU}; font-size:1.08rem; margin:0; }}
.the-chon {{ position:relative; overflow:hidden; border-radius:20px; padding:26px 24px 22px;
             color:#fff; min-height:210px; box-shadow:0 8px 22px rgba(0,0,0,.12); }}
.the-chon .icon {{ position:absolute; right:10px; bottom:-8px; font-size:96px; opacity:.18;
                   filter:grayscale(1) brightness(3); }}
.the-chon .ten {{ font-family:'Noto Serif', Georgia, serif; font-size:1.7rem; font-weight:700; }}
.the-chon .mota {{ opacity:.85; font-size:.92rem; margin:.2rem 0 1rem; }}
.the-chon .nhan-gia {{ font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; opacity:.75; font-weight:700; }}
.the-chon .gia {{ font-family:'Noto Serif', Georgia, serif; font-size:1.7rem; font-weight:700; }}
.the-chon .ngay {{ font-size:.82rem; opacity:.75; margin-top:.2rem; }}

/* --- Dải đầu trang lớn: 2 logo ở giữa --- */
.hero-dau {{ position:relative; overflow:hidden; border-radius:28px; text-align:center;
    padding:clamp(22px,4vw,40px) 20px clamp(20px,3.5vw,34px); margin-bottom:26px;
    background:
      radial-gradient(rgba(255,255,255,.07) 1px, transparent 1.6px) 0 0 / 18px 18px,
      radial-gradient(circle at 12% 18%, rgba(242,179,61,.30) 0, transparent 260px),
      radial-gradient(circle at 90% 90%, rgba(232,116,59,.28) 0, transparent 300px),
      linear-gradient(135deg, #2F6B22 0%, #1F4A16 55%, #163610 100%);
    box-shadow:0 18px 40px rgba(31,74,22,.28); }}
.hero-dau .cap {{ display:flex; align-items:center; justify-content:center;
                  gap:clamp(14px,3vw,36px); flex-wrap:wrap; }}
.hero-dau .icon {{ width:clamp(92px,13vw,150px); height:auto; border-radius:28%; background:#fff;
    box-shadow:0 12px 28px rgba(0,0,0,.32), 0 0 0 4px rgba(255,255,255,.22); }}
.hero-dau .chu {{ height:clamp(84px,12.5vw,158px); width:auto; max-width:100%;
                  filter:drop-shadow(0 8px 16px rgba(0,0,0,.28)); }}
.hero-dau .khau-hieu {{ font-family:'Noto Serif', Georgia, serif; color:#FFF3DC;
    font-size:clamp(1.15rem,2.3vw,1.7rem); font-weight:600; margin-top:clamp(10px,1.6vw,18px); }}
.hero-dau .phu {{ color:rgba(255,255,255,.74); font-size:clamp(.82rem,1.3vw,.98rem); margin-top:4px; }}
.hero-dau .phu b {{ color:{VANG}; font-weight:700; }}

/* --- Dải đầu trang (logo) --- */
.thanh-dau {{ display:flex; align-items:center; gap:18px; padding:18px 24px; border-radius:22px;
              background:linear-gradient(120deg,#FFF7EE 0%,#FFFDF9 55%,#F3F8EE 100%);
              border:1px solid {VIEN}; margin-bottom:18px; }}
.thanh-dau img {{ width:76px; height:76px; border-radius:20px; flex:none;
                  box-shadow:0 4px 14px rgba(232,116,59,.22); }}
.thanh-dau .ten {{ font-family:'Noto Serif', Georgia, serif; font-size:1.85rem; font-weight:700;
                   color:{CHU}; line-height:1.2; }}
.thanh-dau .phu {{ color:{CHU_PHU}; font-size:.98rem; margin-top:4px; }}
@media (max-width: 640px) {{ .thanh-dau {{ padding:14px 16px; gap:12px; }}
    .thanh-dau img {{ width:56px; height:56px; }} .thanh-dau .ten {{ font-size:1.3rem; }} }}

/* --- 3 huy hiệu tròn chọn nông sản (điểm nhấn) --- */
@keyframes xoay-vong {{ to {{ transform:rotate(360deg); }} }}
.chon-ns-nhan {{ text-align:center; color:{CHU_PHU}; font-size:.8rem; font-weight:700;
                 letter-spacing:.16em; text-transform:uppercase; margin:8px 0 18px; }}
.chon-ns {{ display:flex; justify-content:center; align-items:flex-start; gap:clamp(18px, 7vw, 88px);
            margin-bottom:22px; flex-wrap:nowrap; }}
a.huy-hieu {{ display:flex; flex-direction:column; align-items:center; text-decoration:none !important;
              color:{CHU} !important; width:170px; transition:transform .25s ease; }}
a.huy-hieu .vanh {{ position:relative; width:128px; height:128px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    transition:transform .25s ease, filter .25s ease, opacity .25s ease; }}
a.huy-hieu .vanh::before {{ content:""; position:absolute; inset:0; border-radius:50%;
    background:var(--n); box-shadow:inset 0 0 0 2px {VIEN}; }}
a.huy-hieu .dia {{ position:relative; z-index:1; width:108px; height:108px; border-radius:50%;
    background:radial-gradient(circle at 32% 28%, #FFFFFF 0%, #FFF9F1 45%, var(--n) 100%);
    box-shadow:0 6px 16px rgba(60,20,20,.12), inset 0 -4px 10px rgba(0,0,0,.05);
    display:flex; align-items:center; justify-content:center; }}
a.huy-hieu .dia svg {{ width:76px; height:76px; }}
a.huy-hieu .ten {{ font-family:'Noto Serif', Georgia, serif; font-size:1.45rem; font-weight:700;
                   margin-top:12px; color:{CHU_PHU}; transition:color .2s ease; }}
a.huy-hieu .mo-ta {{ font-size:.8rem; color:{CHU_PHU}; text-align:center; line-height:1.4;
                     margin-top:2px; opacity:.85; }}
a.huy-hieu .gach {{ width:0; height:4px; border-radius:4px; background:var(--m); margin-top:8px;
                    transition:width .25s ease; }}
/* chưa chọn: nhỏ hơn, nhạt hơn */
a.huy-hieu:not(.dang-chon) .vanh {{ transform:scale(.86); filter:saturate(.8); opacity:.92; }}
a.huy-hieu:not(.dang-chon):hover .vanh {{ transform:scale(.95) translateY(-4px); filter:none; opacity:1; }}
a.huy-hieu:not(.dang-chon):hover .ten {{ color:var(--m); }}
a.huy-hieu:not(.dang-chon):hover .gach {{ width:28px; opacity:.5; }}
/* đang chọn: to, vòng màu xoay, dấu tick */
a.huy-hieu.dang-chon .vanh {{ transform:scale(1.06);
    filter:drop-shadow(0 12px 22px rgba(0,0,0,.18)); }}
a.huy-hieu.dang-chon .vanh::before {{ inset:-5px; box-shadow:none;
    background:conic-gradient(from 0deg, var(--m), {VANG}, {CAM}, var(--m2), var(--m));
    animation:xoay-vong 6s linear infinite; }}
a.huy-hieu.dang-chon .dia {{ box-shadow:0 0 0 5px #fff, 0 8px 18px rgba(0,0,0,.14); }}
a.huy-hieu.dang-chon .ten {{ color:var(--m); }}
a.huy-hieu.dang-chon .gach {{ width:46px; }}
a.huy-hieu .tick {{ position:absolute; z-index:2; top:4px; right:4px; width:30px; height:30px;
    border-radius:50%; background:var(--m); color:#fff; font-size:.95rem; font-weight:800;
    display:flex; align-items:center; justify-content:center; box-shadow:0 0 0 3px #fff; }}
@media (max-width: 640px) {{
  a.huy-hieu {{ width:100px; }}
  a.huy-hieu .vanh {{ width:88px; height:88px; }}
  a.huy-hieu .dia {{ width:74px; height:74px; }}
  a.huy-hieu .dia svg {{ width:46px; height:46px; }}
  a.huy-hieu .ten {{ font-size:1.05rem; }}
  a.huy-hieu .mo-ta {{ display:none; }}
  a.huy-hieu .tick {{ width:24px; height:24px; font-size:.8rem; top:0; right:0; }}
}}

/* --- Nút chọn kiểu nhóm (7/30/90 ngày) --- */
div[data-testid="stButtonGroup"] button {{ min-height:48px; padding:.5rem 1rem; border-radius:12px;
    font-size:1.02rem; font-weight:600; }}
div[data-testid="stButtonGroup"] button p {{ font-size:1.02rem; font-weight:600; }}
div[data-testid="stButtonGroup"] button[kind="segmented_controlActive"],
div[data-testid="stButtonGroup"] button[aria-checked="true"] {{ background:var(--dam) !important;
    border-color:var(--dam) !important; color:#fff !important; }}
div[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] p,
div[data-testid="stButtonGroup"] button[aria-checked="true"] p {{ color:#fff !important; }}

/* --- Nhãn mô hình được chọn --- */
.nhan-mo-hinh {{ display:flex; flex-wrap:wrap; gap:10px; margin:.2rem 0 1rem; }}
.nhan-mo-hinh .nhan {{ display:inline-flex; align-items:center; gap:8px; padding:7px 14px;
    border-radius:999px; font-size:.92rem; font-weight:600; background:#fff; border:1.5px solid {VIEN};
    color:#4A423C; }}
.nhan-mo-hinh .nhan b {{ color:var(--dam); }}
.nhan-mo-hinh .nhan.chinh {{ background:var(--dam); border-color:var(--dam); color:#fff; }}
.nhan-mo-hinh .nhan.chinh b {{ color:#FFE7B8; }}
.nhan-mo-hinh .nhan.cam {{ border-color:{CAM}; background:#FFF6EF; }}
.nhan-mo-hinh .nhan.cam b {{ color:{CAM}; }}

/* --- Bảng so sánh mô hình --- */
.bang-mh td.so {{ text-align:right; font-variant-numeric:tabular-nums; font-weight:600; white-space:nowrap; }}
.bang-mh th.so {{ text-align:right; }}
.bang-mh tr.thang td {{ background:#FFF6E8 !important; }}
.bang-mh tr.thang td:first-child {{ box-shadow:inset 4px 0 0 {CAM}; }}
.bang-mh tr.tham-khao td {{ color:{CHU_PHU}; font-style:italic; background:#FAFAF8 !important; }}
.bang-mh .ten-mh {{ font-weight:700; color:var(--dam); font-size:1.02rem; }}
.bang-mh .phu-mh {{ color:{CHU_PHU}; font-size:.86rem; margin-top:2px; font-style:normal; }}
.bang-mh .cup {{ display:inline-block; margin-left:8px; padding:2px 10px; border-radius:999px;
                 background:{CAM}; color:#fff; font-size:.75rem; font-weight:800; font-style:normal; }}
.bang-mh td.tot {{ color:{TANG}; }}

/* --- Trang đăng nhập / đăng ký --- */
.loi-chao {{ font-family:'Noto Serif', Georgia, serif; font-size:1.6rem; font-weight:700; color:{CHU};
             margin:.2rem 0 .3rem; }}
.loi-chao-phu {{ color:{CHU_PHU}; font-size:1rem; line-height:1.6; margin-bottom:1.2rem; }}
.loi-ich {{ display:flex; gap:14px; align-items:flex-start; padding:14px 16px; margin-bottom:12px;
            background:#fff; border:1px solid {VIEN}; border-radius:16px; }}
.loi-ich .bt {{ width:42px; height:42px; border-radius:12px; flex:none; display:flex; align-items:center;
                justify-content:center; font-size:22px; background:var(--nhat); }}
.loi-ich .td {{ font-weight:700; color:{CHU}; }}
.loi-ich .md {{ color:{CHU_PHU}; font-size:.9rem; margin-top:2px; line-height:1.5; }}
.thanh-tai-khoan {{ display:flex; align-items:center; justify-content:flex-end; gap:10px; flex-wrap:wrap; }}
.thanh-tai-khoan a {{ text-decoration:none !important; display:inline-flex; align-items:center; gap:9px;
    height:44px; border-radius:999px; font-weight:700; font-size:.95rem;
    transition:transform .2s ease, box-shadow .2s ease, background .2s ease, color .2s ease; }}
.thanh-tai-khoan a.nut-trang-chu {{ padding:0 18px 0 14px; color:#fff !important;
    background:linear-gradient(135deg, #46A033 0%, #2F6B22 55%, #1F4A16 100%);
    box-shadow:0 6px 14px rgba(31,74,22,.28), inset 0 1px 0 rgba(255,255,255,.25); }}
.thanh-tai-khoan a.nut-trang-chu svg {{ width:19px; height:19px; color:#FFE3A3; }}
.thanh-tai-khoan a.nut-trang-chu:hover {{ transform:translateY(-2px); box-shadow:0 10px 20px rgba(31,74,22,.35); }}
.thanh-tai-khoan a.chip-tk {{ padding:0 16px 0 5px; color:{CHU} !important; background:#fff;
    border:1.5px solid {VIEN}; box-shadow:0 2px 8px rgba(60,20,20,.05); }}
.thanh-tai-khoan a.chip-tk:hover {{ border-color:var(--dam); transform:translateY(-2px);
    box-shadow:0 8px 18px rgba(60,20,20,.10); }}
.thanh-tai-khoan .avatar {{ width:34px; height:34px; border-radius:50%; color:#fff; font-weight:800;
    display:flex; align-items:center; justify-content:center;
    background:linear-gradient(135deg, var(--dam) 0%, var(--dam-hon) 100%); }}
.st-key-nut_dang_xuat button {{ height:44px !important; min-height:44px !important; border-radius:999px !important;
    border:1.5px solid {VIEN} !important; background:#fff !important; font-weight:700 !important;
    transition:all .2s ease !important; }}
.st-key-nut_dang_xuat button p {{ font-weight:700 !important; color:{CHU_PHU} !important; }}
.st-key-nut_dang_xuat button:hover {{ border-color:{GIAM} !important; background:#FDECEC !important;
    transform:translateY(-2px); }}
.st-key-nut_dang_xuat button:hover p {{ color:{GIAM} !important; }}
div[data-testid="stForm"] {{ border:1px solid {VIEN} !important; border-radius:18px !important;
                             background:#fff; padding:1.2rem 1.3rem !important;
                             box-shadow:0 6px 20px rgba(60,20,20,.06); }}

/* --- Khung ghi chú dưới dự báo --- */
.ghi-chu-gia {{ display:flex; gap:12px; align-items:flex-start; margin-top:18px;
                background:var(--nhat); border:1px solid {VIEN}; border-left:4px solid var(--dam);
                border-radius:12px; padding:14px 18px; color:#4A423C; font-size:.95rem; line-height:1.6; }}
.ghi-chu-gia .bt {{ flex:none; width:22px; height:22px; border-radius:50%; background:var(--dam);
                    color:#fff; font-weight:700; font-size:.8rem; display:flex; align-items:center;
                    justify-content:center; margin-top:2px; font-family:'Noto Serif', Georgia, serif; }}

.chan-trang {{ text-align:center; color:{CHU_PHU}; font-size:.82rem; margin-top:2rem;
               padding-top:1rem; border-top:1px solid {VIEN}; }}
div[data-testid="stTabs"] button p {{ font-size:1rem; font-weight:600; }}
</style>""")


# ================================================================ Khối giao diện
def tieu_de_muc(tieu_de: str, mo_ta: str = "") -> str:
    return gon(f'<div class="tieu-de-muc">{e(tieu_de)}</div>'
               + (f'<div class="mo-ta-muc">{mo_ta}</div>' if mo_ta else ""))


def hang_o_gia(nong_san: str, loai: str, khu_vuc: str, chuoi: pd.DataFrame) -> str:
    """4 ô: Giá hiện tại · Biến động · Cao nhất 7 phiên · Thấp nhất 7 phiên."""
    gia = chuoi["gia"].to_numpy()
    nay, truoc = gia[-1], gia[-2]
    chenh = nay - truoc
    bay = gia[-7:]
    if chenh > 0:
        mui, mau = "↑", TANG
    elif chenh < 0:
        mui, mau = "↓", GIAM
    else:
        mui, mau = "→", CHU_PHU
    pt = chenh / truoc * 100 if truoc else 0
    return gon(f"""
<div class="hang-o">
  <div class="o noi-bat">
    <div class="nhan">Giá hiện tại</div>
    <div class="so-lon">{so(nay)}</div>
    <div class="phu">đồng/kg<br>{e(loai)} · {e(khu_vuc)}</div>
    <div class="hinh-chim hinh-ve">{gon(HINH_VE.get(nong_san, ""))}</div>
  </div>
  <div class="o">
    <div class="nhan">Biến động</div>
    <div class="so-lon" style="color:{mau}"><span class="mui-ten">{mui}</span>{so(abs(chenh))}</div>
    <div class="phu">so với phiên trước<br>({so(truoc)} đồng/kg · {phan_tram(pt)})</div>
    <div class="hinh-chim">{SVG_SONG}</div>
  </div>
  <div class="o">
    <div class="nhan">Cao nhất 7 phiên</div>
    <div class="so-lon">{so(bay.max())}</div>
    <div class="phu">đồng/kg</div>
    <div class="hinh-chim">{SVG_TANG}</div>
  </div>
  <div class="o">
    <div class="nhan">Thấp nhất 7 phiên</div>
    <div class="so-lon">{so(bay.min())}</div>
    <div class="phu">đồng/kg</div>
    <div class="hinh-chim">{SVG_GIAM}</div>
  </div>
</div>""")


THU = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def hang_o_du_bao(kq, gia_nay: float, cac_moc, khoa: dict = None) -> str:
    """Các ô dự báo (Ngày mai · 3 · 7 · 30 ngày). khoa = {số ngày: dòng chữ cách mở} cho ô bị khoá."""
    khoa = khoa or {}
    o = []
    for i, (so_ngay, nhan) in enumerate(cac_moc):
        dong = kq.bang.iloc[so_ngay - 1]
        if so_ngay in khoa:
            o.append(f"""
  <div class="o du-bao khoa">
    <div class="nhan">{e(nhan)}</div>
    <div class="ngay">{THU[dong['ngay'].weekday()]}, {dong['ngay']:%d/%m/%Y}</div>
    <div class="khoa-giua"><div class="o-khoa-icon">{SVG_KHOA}</div>
      <div class="khoa-chu">Bị khoá</div>
      <div class="khoa-phu">{khoa[so_ngay]}</div></div>
  </div>""")
            continue
        chenh = dong["du_bao"] - gia_nay
        pt = chenh / gia_nay * 100
        if abs(pt) < 0.3:
            mui, mau, chu = "→", CHU_PHU, "Gần như giữ nguyên"
        elif pt > 0:
            mui, mau, chu = "↑", TANG, f"Tăng {so(chenh)} đ"
        else:
            mui, mau, chu = "↓", GIAM, f"Giảm {so(-chenh)} đ"
        sai = kq.sai_so_theo_ngay[so_ngay - 1]
        o.append(f"""
  <div class="o du-bao {'chinh' if i == 0 else ''}">
    <div class="nhan">{e(nhan)}</div>
    <div class="ngay">{THU[dong['ngay'].weekday()]}, {dong['ngay']:%d/%m/%Y}</div>
    <div class="so-lon">{so(dong['du_bao'])}<span style="font-size:1rem;font-weight:500;color:{CHU_PHU}"> đ/kg</span></div>
    <div class="doi" style="color:{mau}"><span class="mui-ten">{mui}</span>{chu}&nbsp;<span style="color:{CHU_PHU};font-weight:500">({phan_tram(pt)})</span></div>
    <div class="dong"><span>Khoảng có thể (90%)</span><b>{so(dong['thap'])} – {so(dong['cao'])}</b></div>
    <div class="dong"><span>Sai số trung bình</span><span>± {str(round(sai, 1)).replace('.', ',')}%</span></div>
  </div>""")
    return gon(f'<div class="hang-o {"ba" if len(cac_moc) == 3 else ""}">' + "".join(o) + "</div>")


GHI_CHU_GIA = {
    "Hồ tiêu": "Giá tiêu thực tế tại đại lý có thể cao hoặc thấp hơn mức tham khảo tùy độ khô, "
               "tỷ lệ tạp chất, chất lượng hạt, quy cách sơ chế và khối lượng giao dịch. Người bán "
               "nên liên hệ điểm thu mua trước khi giao hàng để xác nhận giá và điều kiện phân loại.",
    "Cà phê": "Giá cà phê thực tế tại đại lý có thể cao hoặc thấp hơn mức tham khảo tùy độ ẩm, "
              "tỷ lệ tạp chất, tỷ lệ hạt đen vỡ, cỡ hạt và khối lượng giao dịch. Người bán nên liên "
              "hệ điểm thu mua trước khi giao hàng để xác nhận giá và điều kiện phân loại.",
    "Lúa": "Giá lúa thực tế tại ruộng có thể cao hoặc thấp hơn mức tham khảo tùy độ ẩm, tỷ lệ hạt "
           "lép, tạp chất, chất lượng hạt và khối lượng giao dịch. Người bán nên liên hệ thương lái "
           "hoặc điểm thu mua trước khi giao hàng để xác nhận giá và điều kiện phân loại.",
}


MO_TA_MO_HINH = {
    "Holt": "San bằng mũ · bám mức giá gần nhất, hợp với giá đi kiểu bậc thang",
    "ARIMA": "Chuỗi thời gian · học quy luật tăng/giảm của các ngày trước",
    "Random Forest": "Học máy · bắt quy luật phức tạp từ % thay đổi 1–30 ngày trước",
    "Giữ nguyên": "Mốc tham khảo · đoán giá giữ nguyên như hôm nay (không phải mô hình)",
}


def nhan_mo_hinh(kq) -> str:
    """Nhãn 'Mô hình được chọn' (+ nhãn giá London cho cà phê)."""
    o = [f'<span class="nhan chinh">🏆 Mô hình được chọn: <b>{e(kq.mo_hinh_chon)}</b></span>',
         f'<span class="nhan">Sai ít nhất trong 3 mô hình khi thử lại <b>{kq.so_lan_kiem_tra} lần</b>'
         ' trong 6 tháng gần nhất</span>']
    nm = kq.ngay_mai or {}
    if nm.get("dung"):
        doi = nm["london_thay_doi"]
        o.append(f'<span class="nhan cam">☕ Ngày mai: <b>{e(nm["mo_hinh"])} + giá London</b> '
                 f'(phiên gần nhất {"↑" if doi >= 0 else "↓"} {abs(doi):.1f}%)</span>'.replace(".", ","))
    elif nm.get("mo_hinh"):
        o.append(f'<span class="nhan">☕ Chưa dùng giá London cho ngày mai: {e(nm.get("ly_do", ""))}</span>')
    return gon('<div class="nhan-mo-hinh">' + "".join(o) + "</div>")


def _pt(x) -> str:
    return f"{x:.2f}%".replace(".", ",")


def bang_mo_hinh(so_sanh, mo_hinh_chon: str, chan: str) -> str:
    """Bảng so sánh sai số 3 mô hình (+ dòng tham khảo 'Giữ nguyên')."""
    cot = ["1 ngày", "7 ngày", "30 ngày", "Trung bình"]
    ba = so_sanh[so_sanh["Mô hình"] != "Giữ nguyên"]
    tot_nhat = {c: ba[c].min() for c in cot}
    hang = []
    for _, r in so_sanh.iterrows():
        ten = r["Mô hình"]
        lop = "thang" if ten == mo_hinh_chon else ("tham-khao" if ten == "Giữ nguyên" else "")
        cup = '<span class="cup">🏆 Được chọn</span>' if ten == mo_hinh_chon else ""
        o_so = "".join(
            f'<td class="so {"tot" if ten != "Giữ nguyên" and r[c] == tot_nhat[c] else ""}">{_pt(r[c])}</td>'
            for c in cot)
        hang.append(f'<tr class="{lop}"><td><div class="ten-mh">{e(ten)}{cup}</div>'
                    f'<div class="phu-mh">{e(MO_TA_MO_HINH.get(ten, ""))}</div></td>{o_so}</tr>')
    tieu_de = "".join(f'<th class="so">{c}</th>' for c in ["Ngày mai", "7 ngày", "30 ngày", "TB 1–30 ngày"])
    return gon(f'<div class="bang-ss bang-mh"><table><thead><tr><th>Mô hình</th>{tieu_de}</tr></thead>'
               f'<tbody>{"".join(hang)}</tbody></table><div class="chan">{chan}</div></div>')


def bang_ngay_mai_london(nm: dict) -> str:
    """(Cà phê) Sai số dự báo ngày mai: có / không có giá London."""
    s = nm.get("sai_so", {})
    dong = [("Holt", "Holt", None), ("ARIMA", "ARIMA (không London)", "ARIMA"),
            ("Random Forest", "Random Forest (không London)", "Random Forest")]
    hang = []
    for ten, khong, co in dong:
        co_txt = _pt(s[co]) if co else "—"
        lop = "thang" if ten == nm.get("mo_hinh") else ""
        cup = '<span class="cup">🏆 Dùng cho ngày mai</span>' if ten == nm.get("mo_hinh") else ""
        hang.append(f'<tr class="{lop}"><td><div class="ten-mh">{e(ten)}{cup}</div></td>'
                    f'<td class="so">{_pt(s[khong])}</td><td class="so {"tot" if co else ""}">{co_txt}</td></tr>')
    return gon('<div class="bang-ss bang-mh"><table><thead><tr><th>Mô hình</th>'
               '<th class="so">Không có giá London</th><th class="so">Có giá London</th></tr></thead>'
               f'<tbody>{"".join(hang)}</tbody></table><div class="chan">Sai số trung bình khi dự báo '
               f'ngày mai, thử trên {nm.get("so_ngay_thu", 0)} ngày gần đây có giá London. '
               'Holt chỉ dùng giá trong nước nên không có cột "có giá London".</div></div>')


def hang_o_the_gioi(tg) -> str:
    """3 ô: Robusta London · Arabica New York · Phiên gần nhất."""
    def o_gia(cot, ky_han, nhan, don_vi):
        s = tg.dropna(subset=[cot])
        if len(s) < 2:
            return ""
        moi, truoc = s[cot].iloc[-1], s[cot].iloc[-2]
        chenh = moi - truoc
        pt = chenh / truoc * 100
        mui, mau = ("↑", TANG) if chenh > 0 else (("↓", GIAM) if chenh < 0 else ("→", CHU_PHU))
        so_txt = (f"{moi:,.0f}" if moi >= 1000 else f"{moi:,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")
        doi_txt = (f"{abs(chenh):,.0f}" if moi >= 1000 else f"{abs(chenh):,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")
        kh = s[ky_han].iloc[-1] if ky_han in s and pd.notna(s[ky_han].iloc[-1]) else ""
        return f"""
  <div class="o"><div class="nhan">{nhan}</div>
    <div class="so-lon">{so_txt}</div>
    <div class="phu">{don_vi}{f" · kỳ hạn {e(kh)}" if kh else ""}<br>
      <b style="color:{mau}">{mui} {doi_txt} ({phan_tram(pt)})</b> so với phiên trước</div>
    <div class="hinh-chim">{SVG_SONG}</div></div>"""
    ngay = tg["ngay"].iloc[-1]
    nguon = str(tg["nguon"].iloc[-1]).split("(")[0].strip()
    return gon('<div class="hang-o ba">'
               + o_gia("robusta", "ky_han_robusta", "Robusta · sàn London", "USD/tấn")
               + o_gia("arabica", "ky_han_arabica", "Arabica · sàn New York", "cent/lb")
               + f"""<div class="o noi-bat"><div class="nhan">Phiên gần nhất</div>
    <div class="so-lon">{ngay:%d/%m/%Y}</div>
    <div class="phu">Nguồn: {e(nguon)}</div>
    <div class="hinh-chim hinh-ve">{gon(HINH_VE["Cà phê"])}</div></div>"""
               + "</div>")


def _lan_doi_gia(s):
    """s: Series giá theo ngày. Trả về (giá hiện tại, giá trước lần đổi gần nhất, ngày đổi) hoặc None."""
    s = s.dropna()
    if s.empty:
        return None
    moi = s.iloc[-1]
    doi = s[s != moi]
    if doi.empty:
        return moi, None, None
    ngay_doi = s[s.index > doi.index[-1]].index[0]
    return moi, doi.iloc[-1], ngay_doi


def hang_o_tieu_the_gioi(tg) -> str:
    """3 ô giá xuất khẩu tiêu Việt Nam (IPC): đen 500 g/l · đen 550 g/l · trắng ASTA."""
    o = []
    for loai, noi_bat in [("Tiêu đen 500 g/l", True), ("Tiêu đen 550 g/l", False), ("Tiêu trắng ASTA", False)]:
        s = tg[(tg["quoc_gia"] == "Việt Nam") & (tg["loai"] == loai)].set_index("ngay")["gia"]
        kq = _lan_doi_gia(s)
        if kq is None:
            continue
        moi, cu, ngay_doi = kq
        if cu is None:
            doi = "chưa đổi giá"
        else:
            chenh = moi - cu
            mui, mau = ("↑", TANG) if chenh > 0 else ("↓", GIAM)
            doi = (f'<b style="color:{"#fff" if noi_bat else mau}">{mui} {so(abs(chenh))} USD</b> '
                   f'ở lần đổi giá gần nhất ({ngay_doi:%d/%m/%Y})')
        o.append(f"""
  <div class="o {'noi-bat' if noi_bat else ''}"><div class="nhan">{loai} · Việt Nam</div>
    <div class="so-lon">{so(moi)}</div>
    <div class="phu">USD/tấn · ngày {s.index[-1]:%d/%m/%Y}<br>{doi}</div>
    <div class="hinh-chim {'hinh-ve' if noi_bat else ''}">{gon(HINH_VE["Hồ tiêu"]) if noi_bat else SVG_SONG}</div></div>""")
    return gon('<div class="hang-o ba">' + "".join(o) + "</div>")


CO_QUOC_GIA = {"Việt Nam": "🇻🇳", "Indonesia": "🇮🇩", "Brazil": "🇧🇷", "Malaysia": "🇲🇾"}


def bang_tieu_cac_nuoc(tg, chan: str) -> str:
    """Bảng giá xuất khẩu tiêu các nước: giá hiện tại, so với 30 ngày trước, so với tiêu Việt Nam."""
    ngay_cuoi = tg["ngay"].max()
    hang = []
    for loai_nhom, loai_moc in [("Tiêu đen", "Tiêu đen 500 g/l"), ("Tiêu trắng", "Tiêu trắng ASTA")]:
        ds = tg[tg["loai"].str.startswith(loai_nhom)]
        if ds.empty:
            continue
        moc_vn = ds[(ds["quoc_gia"] == "Việt Nam") & (ds["loai"] == loai_moc) & (ds["ngay"] == ngay_cuoi)]["gia"]
        moc_vn = moc_vn.iloc[0] if len(moc_vn) else None
        hang.append(f'<tr><td colspan="4" style="background:var(--nhat);font-weight:800;color:var(--dam-hon);'
                    f'font-size:.85rem;letter-spacing:.06em;text-transform:uppercase;padding:10px 22px">'
                    f'{loai_nhom}</td></tr>')
        cac = []
        for (qg, loai), g in ds.groupby(["quoc_gia", "loai"]):
            s = g.set_index("ngay")["gia"].sort_index()
            moi = s.iloc[-1]
            cu = s[s.index <= s.index[-1] - pd.Timedelta(days=30)]
            cu = cu.iloc[-1] if len(cu) else None
            cac.append((qg, loai, moi, cu))
        for qg, loai, moi, cu in sorted(cac, key=lambda x: (x[0] != "Việt Nam", -x[2])):
            if cu is None or cu == moi:
                vien = '<span class="vien-ngang">→ 0</span>'
            elif moi > cu:
                vien = f'<span class="vien-tang">↑ {so(moi - cu)}</span>'
            else:
                vien = f'<span class="vien-giam">↓ {so(cu - moi)}</span>'
            if qg == "Việt Nam" and loai == loai_moc:
                ss = '<span class="vien-nhan">Mốc so sánh</span>'
            elif moc_vn is None:
                ss = ""
            else:
                c = moi - moc_vn
                ss = (f'<span class="vien-tang">cao hơn {so(c)}</span>' if c > 0 else
                      f'<span class="vien-giam">thấp hơn {so(-c)}</span>' if c < 0 else
                      '<span class="vien-ngang">bằng giá</span>')
            hang.append(f"""
<tr class="{'dang-xem' if qg == 'Việt Nam' else ''}">
  <td><div class="ten-kv">{CO_QUOC_GIA.get(qg, "")} {e(qg)}</div><div class="phu-kv">{e(loai)}</div></td>
  <td class="phai"><span class="gia">{so(moi)}</span></td>
  <td class="phai an-nho">{vien}</td>
  <td class="phai">{ss}</td>
</tr>""")
    return gon(f"""
<div class="bang-ss"><table>
  <thead><tr><th>Nước · loại tiêu</th><th class="phai">Giá (USD/tấn)</th>
             <th class="phai an-nho">So với 30 ngày trước</th><th class="phai">So với tiêu Việt Nam*</th></tr></thead>
  <tbody>{''.join(hang)}</tbody>
</table><div class="chan">{chan}</div></div>""")


def css_dang_nhap() -> str:
    """CSS riêng cho trang đăng nhập: nền xanh chuyển động, khung kính mờ, hiệu ứng."""
    return gon(f"""
<style>
@keyframes troi-nen {{ 0% {{ background-position:0% 50%; }} 50% {{ background-position:100% 50%; }}
                       100% {{ background-position:0% 50%; }} }}
@keyframes vang-sang {{ 0%,100% {{ transform:translate(0,0) scale(1); opacity:.55; }}
                        50% {{ transform:translate(40px,-30px) scale(1.15); opacity:.85; }} }}
@keyframes bay-len {{ 0% {{ transform:translateY(0) rotate(0deg); opacity:0; }}
                      10% {{ opacity:.9; }} 90% {{ opacity:.9; }}
                      100% {{ transform:translateY(-115vh) rotate(360deg); opacity:0; }} }}
@keyframes nhap-nho {{ 0%,100% {{ transform:translateY(0) rotate(-2deg); }} 50% {{ transform:translateY(-10px) rotate(2deg); }} }}
@keyframes phat-sang {{ 0%,100% {{ filter:drop-shadow(0 6px 14px rgba(0,0,0,.35)) drop-shadow(0 0 0 rgba(255,214,140,0)); }}
                        50% {{ filter:drop-shadow(0 6px 14px rgba(0,0,0,.35)) drop-shadow(0 0 18px rgba(255,214,140,.55)); }} }}
@keyframes hien-len {{ from {{ opacity:0; transform:translateY(28px) scale(.98); }} to {{ opacity:1; transform:none; }} }}
@keyframes luot-sang {{ 0% {{ left:-60%; }} 60%,100% {{ left:130%; }} }}

/* nền toàn trang */
.stApp {{ background:linear-gradient(125deg, #173812 0%, #2F6B22 35%, #1F4A16 65%, #10280C 100%) !important;
          background-size:260% 260% !important; animation:troi-nen 22s ease infinite; }}
header[data-testid="stHeader"] {{ background:transparent !important; }}
.block-container {{ position:relative; z-index:2; padding-top:2.2rem !important; max-width:1100px; }}

/* vầng sáng & hạt lúa bay */
.nen-hieu-ung {{ position:fixed; inset:0; z-index:0; pointer-events:none; overflow:hidden; }}
.nen-hieu-ung .vang {{ position:absolute; border-radius:50%; filter:blur(60px);
                       animation:vang-sang 14s ease-in-out infinite; }}
.nen-hieu-ung .hat {{ position:absolute; bottom:-60px; animation:bay-len linear infinite; }}

/* logo */
.dn-dau {{ text-align:center; margin:0 0 18px; animation:hien-len .9s ease both; }}
.dn-dau .cap {{ display:flex; align-items:center; justify-content:center; gap:clamp(12px,2.5vw,26px); flex-wrap:wrap; }}
.dn-dau .icon {{ width:clamp(78px,10vw,118px); border-radius:28%; background:#fff;
                 box-shadow:0 14px 34px rgba(0,0,0,.35), 0 0 0 4px rgba(255,255,255,.22);
                 animation:nhap-nho 5s ease-in-out infinite; }}
.dn-dau .chu {{ height:clamp(70px,9.5vw,124px); max-width:100%; animation:phat-sang 4s ease-in-out infinite; }}
.dn-dau .khau-hieu {{ font-family:'Noto Serif', Georgia, serif; color:#FFF3DC; font-weight:600;
                      font-size:clamp(1.05rem,2vw,1.4rem); margin-top:10px; letter-spacing:.01em; }}
.dn-dau .phu {{ color:rgba(255,255,255,.72); font-size:.95rem; margin-top:3px; }}

/* khung đăng nhập kính mờ */
.st-key-khung_dang_nhap {{ background:rgba(255,255,255,.93) !important; backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px); }}
.st-key-khung_dang_nhap {{ border-radius:26px !important; border:1px solid rgba(255,255,255,.6) !important;
    padding:1.4rem 1.6rem 1.1rem !important;
    box-shadow:0 30px 60px rgba(0,0,0,.35), 0 0 0 1px rgba(255,255,255,.15) inset;
    animation:hien-len .9s .15s cubic-bezier(.2,.8,.2,1) both; }}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-khung_dang_nhap) {{ border:none !important;
    background:transparent !important; }}

/* thanh chuyển Đăng nhập / Đăng ký
   (nhắm theo role="tab"/"tablist" – chuẩn của trình duyệt, đúng với mọi phiên bản Streamlit) */
@keyframes nay-the {{ 0% {{ transform:scale(.94); }} 60% {{ transform:scale(1.04); }} 100% {{ transform:scale(1); }} }}
.st-key-khung_dang_nhap [role="tablist"] {{ position:relative !important; display:flex !important; gap:6px !important;
    padding:6px !important; border-radius:18px !important; overflow:visible !important;
    background:linear-gradient(180deg, #EEF4E9 0%, #F6F1EA 100%) !important;
    border:1px solid rgba(47,107,34,.12) !important;
    box-shadow:inset 0 2px 6px rgba(31,74,22,.08) !important; margin-bottom:8px !important; }}
.st-key-khung_dang_nhap [role="tablist"]::before, .st-key-khung_dang_nhap [role="tablist"]::after {{ display:none !important; }}
/* xoá gạch chân mặc định (thanh cam + đường xám) */
/* Ẩn MỌI thứ trong cụm nút không phải nút / danh sách nút / nội dung thẻ
   (thanh gạch chân cam của Streamlit nằm ở đâu cũng bị ẩn) */
.st-key-khung_dang_nhap [data-testid="stTabs"] :not([role="tablist"]):not([role="tab"]):not([role="tab"] *):not([role="tabpanel"]):not([role="tabpanel"] *):not(:has([role="tablist"], [role="tabpanel"], input, textarea, button, form, [data-testid="stVerticalBlock"], [data-testid="stMarkdownContainer"])):not([data-testid="stVerticalBlock"] *):not(form *),
.st-key-khung_dang_nhap div:has(> [role="tablist"]) :not([role="tablist"]):not([role="tab"]):not([role="tab"] *):not([role="tabpanel"]):not([role="tabpanel"] *):not(:has([role="tablist"], [role="tabpanel"], input, textarea, button, form, [data-testid="stVerticalBlock"], [data-testid="stMarkdownContainer"])):not([data-testid="stVerticalBlock"] *):not(form *),
.st-key-khung_dang_nhap [role="tablist"] > :not([role="tab"]),
.st-key-khung_dang_nhap [data-testid="stTabs"] [class*="highlight" i],
.st-key-khung_dang_nhap [role="tablist"] ~ div:empty,
.st-key-khung_dang_nhap [data-baseweb="tab-highlight"], .st-key-khung_dang_nhap [data-baseweb="tab-border"] {{ display:none !important; }}
.st-key-khung_dang_nhap [role="tab"] {{ flex:1 1 0 !important; display:flex !important; align-items:center !important;
    justify-content:center !important; gap:9px !important; min-height:50px !important;
    margin:0 !important; padding:10px 8px !important; border:none !important; border-radius:13px !important;
    background:transparent !important; box-shadow:none !important; outline:none !important; cursor:pointer;
    transition:background .3s ease, box-shadow .3s ease, transform .2s ease !important; }}
.st-key-khung_dang_nhap [role="tab"]::after {{ display:none !important; }}
.st-key-khung_dang_nhap [role="tab"], .st-key-khung_dang_nhap [role="tab"] p, .st-key-khung_dang_nhap [role="tab"] span, .st-key-khung_dang_nhap [role="tab"] div {{ color:#7A706A !important; font-weight:700 !important;
    font-size:1.04rem !important; margin:0 !important; transition:color .3s ease; }}
.st-key-khung_dang_nhap [role="tab"]::before {{ content:""; width:19px; height:19px; flex:none; background:#9A8F88;
    transition:background .3s ease;
    -webkit-mask:var(--icon) center / contain no-repeat; mask:var(--icon) center / contain no-repeat; }}
.st-key-khung_dang_nhap [role="tab"]:first-of-type {{ --icon:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222.2%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M15%203h4a2%202%200%200%201%202%202v14a2%202%200%200%201-2%202h-4%22/%3E%3Cpolyline%20points%3D%2210%2017%2015%2012%2010%207%22/%3E%3Cline%20x1%3D%2215%22%20y1%3D%2212%22%20x2%3D%223%22%20y2%3D%2212%22/%3E%3C/svg%3E"); }}
.st-key-khung_dang_nhap [role="tab"]:last-of-type {{ --icon:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222.2%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M16%2021v-2a4%204%200%200%200-4-4H6a4%204%200%200%200-4%204v2%22/%3E%3Ccircle%20cx%3D%229%22%20cy%3D%227%22%20r%3D%224%22/%3E%3Cline%20x1%3D%2219%22%20y1%3D%228%22%20x2%3D%2219%22%20y2%3D%2214%22/%3E%3Cline%20x1%3D%2222%22%20y1%3D%2211%22%20x2%3D%2216%22%20y2%3D%2211%22/%3E%3C/svg%3E"); }}
.st-key-khung_dang_nhap [role="tab"]:hover {{ background:rgba(255,255,255,.88) !important; transform:translateY(-1px); }}
.st-key-khung_dang_nhap [role="tab"]:hover, .st-key-khung_dang_nhap [role="tab"]:hover p, .st-key-khung_dang_nhap [role="tab"]:hover span, .st-key-khung_dang_nhap [role="tab"]:hover div {{ color:#2F6B22 !important; }}
.st-key-khung_dang_nhap [role="tab"]:hover::before {{ background:#2F6B22; }}
.st-key-khung_dang_nhap [role="tab"][aria-selected="true"] {{
    background:linear-gradient(135deg, #3B8A2B 0%, #2F6B22 50%, #1F4A16 100%) !important;
    box-shadow:0 8px 18px rgba(31,74,22,.35), inset 0 1px 0 rgba(255,255,255,.25) !important;
    animation:nay-the .35s ease; }}
.st-key-khung_dang_nhap [role="tab"][aria-selected="true"], .st-key-khung_dang_nhap [role="tab"][aria-selected="true"] p,
.st-key-khung_dang_nhap [role="tab"][aria-selected="true"] span, .st-key-khung_dang_nhap [role="tab"][aria-selected="true"] div {{ color:#fff !important; }}
.st-key-khung_dang_nhap [role="tab"][aria-selected="true"]::before {{ background:#FFE3A3 !important; }}
.st-key-khung_dang_nhap [role="tab"][aria-selected="true"]:hover {{ transform:none; }}
.st-key-khung_dang_nhap [role="tabpanel"] {{ padding-top:14px !important; }}

/* thanh chuyển tự làm: 2 nút trong khung "thanh_chuyen" (không dùng tabs của Streamlit) */
.st-key-thanh_chuyen {{ padding:6px !important; border-radius:18px !important;
    background:linear-gradient(180deg, #EEF4E9 0%, #F6F1EA 100%) !important;
    border:1px solid rgba(47,107,34,.12) !important;
    box-shadow:inset 0 2px 6px rgba(31,74,22,.08) !important; margin-bottom:10px; }}
.st-key-thanh_chuyen [data-testid="stHorizontalBlock"] {{ gap:6px !important; flex-wrap:nowrap !important; }}
.st-key-thanh_chuyen [data-testid="stColumn"], .st-key-thanh_chuyen [data-testid="column"] {{ min-width:0 !important; width:auto !important; flex:1 1 0 !important; }}
.st-key-thanh_chuyen button {{ width:100% !important; min-height:50px !important; border:none !important; border-radius:13px !important;
    box-shadow:none !important; outline:none !important; display:flex !important; align-items:center !important;
    justify-content:center !important; gap:9px !important;
    transition:background .3s ease, box-shadow .3s ease, transform .2s ease !important; }}
.st-key-thanh_chuyen button p {{ font-weight:700 !important; font-size:1.04rem !important; margin:0 !important; transition:color .3s ease; }}
.st-key-thanh_chuyen button::before {{ content:""; width:19px; height:19px; flex:none; transition:background .3s ease;
    -webkit-mask:var(--icon) center / contain no-repeat; mask:var(--icon) center / contain no-repeat; }}
.st-key-the_dn_on button, .st-key-the_dn_off button {{ --icon:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222.2%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M15%203h4a2%202%200%200%201%202%202v14a2%202%200%200%201-2%202h-4%22/%3E%3Cpolyline%20points%3D%2210%2017%2015%2012%2010%207%22/%3E%3Cline%20x1%3D%2215%22%20y1%3D%2212%22%20x2%3D%223%22%20y2%3D%2212%22/%3E%3C/svg%3E"); }}
.st-key-the_dk_on button, .st-key-the_dk_off button {{ --icon:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22black%22%20stroke-width%3D%222.2%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M16%2021v-2a4%204%200%200%200-4-4H6a4%204%200%200%200-4%204v2%22/%3E%3Ccircle%20cx%3D%229%22%20cy%3D%227%22%20r%3D%224%22/%3E%3Cline%20x1%3D%2219%22%20y1%3D%228%22%20x2%3D%2219%22%20y2%3D%2214%22/%3E%3Cline%20x1%3D%2222%22%20y1%3D%2211%22%20x2%3D%2216%22%20y2%3D%2211%22/%3E%3C/svg%3E"); }}
.st-key-the_dn_off button, .st-key-the_dk_off button {{ background:transparent !important; }}
.st-key-the_dn_off button p, .st-key-the_dk_off button p {{ color:#7A706A !important; }}
.st-key-the_dn_off button::before, .st-key-the_dk_off button::before {{ background:#9A8F88; }}
.st-key-the_dn_off button:hover, .st-key-the_dk_off button:hover {{ background:rgba(255,255,255,.88) !important;
    transform:translateY(-1px); }}
.st-key-the_dn_off button:hover p, .st-key-the_dk_off button:hover p {{ color:#2F6B22 !important; }}
.st-key-the_dn_off button:hover::before, .st-key-the_dk_off button:hover::before {{ background:#2F6B22; }}
.st-key-the_dn_on button, .st-key-the_dk_on button {{ background:linear-gradient(135deg, #3B8A2B 0%, #2F6B22 50%, #1F4A16 100%) !important;
    box-shadow:0 8px 18px rgba(31,74,22,.35), inset 0 1px 0 rgba(255,255,255,.25) !important;
    animation:nay-the .35s ease; cursor:default; }}
.st-key-the_dn_on button p, .st-key-the_dk_on button p {{ color:#fff !important; }}
.st-key-the_dn_on button::before, .st-key-the_dk_on button::before {{ background:#FFE3A3; }}

/* thanh chuyển – tinh chỉnh (đặt sau để đè các quy tắc phía trên) */
@keyframes luot-sang-cham {{ 0% {{ left:-70%; }} 70%,100% {{ left:140%; }} }}
.st-key-thanh_chuyen {{ padding:7px !important; border-radius:20px !important;
    background:linear-gradient(180deg, #F4F8F0 0%, #EFE9E1 100%) !important;
    border:1px solid rgba(255,255,255,.9) !important;
    box-shadow:0 1px 0 rgba(255,255,255,.9) inset, 0 -1px 0 rgba(31,74,22,.06) inset,
               0 6px 16px rgba(31,74,22,.10), 0 0 0 1px rgba(47,107,34,.10) !important;
    margin:2px 0 14px !important; }}
/* biểu tượng + chữ đi liền nhau, căn giữa */
.st-key-thanh_chuyen button > div, .st-key-thanh_chuyen button [data-testid="stMarkdownContainer"] {{ flex:0 0 auto !important;
    width:auto !important; min-width:0 !important; }}
.st-key-thanh_chuyen button {{ min-height:52px !important; border-radius:14px !important; gap:10px !important;
    position:relative !important; overflow:hidden !important; }}
.st-key-thanh_chuyen button p {{ font-size:1.06rem !important; letter-spacing:.01em; white-space:nowrap; }}
.st-key-thanh_chuyen button::before {{ width:20px !important; height:20px !important; }}
/* nút chưa chọn */
.st-key-the_dn_off button p, .st-key-the_dk_off button p {{ color:#6F665F !important; }}
.st-key-the_dn_off button:hover, .st-key-the_dk_off button:hover {{ background:#fff !important;
    box-shadow:0 4px 12px rgba(31,74,22,.10) !important; transform:translateY(-1px); }}
/* nút đang chọn: viền sáng mảnh + phát sáng + dải sáng lướt chậm */
.st-key-the_dn_on button, .st-key-the_dk_on button {{
    background:linear-gradient(135deg, #46A033 0%, #2F6B22 55%, #1F4A16 100%) !important;
    box-shadow:0 10px 22px rgba(31,74,22,.38), 0 0 0 1px rgba(255,255,255,.18) inset,
               0 1px 0 rgba(255,255,255,.35) inset !important; }}
.st-key-the_dn_on button::after, .st-key-the_dk_on button::after {{ content:""; position:absolute; top:0;
    left:-70%; width:40%; height:100%; transform:skewX(-20deg); pointer-events:none;
    background:linear-gradient(90deg, transparent, rgba(255,255,255,.28), transparent);
    animation:luot-sang-cham 4.5s ease-in-out infinite; }}

/* ===================== HIỆU ỨNG THÊM ===================== */
@property --goc {{ syntax:'<angle>'; inherits:false; initial-value:0deg; }}
@keyframes xoay-goc {{ to {{ --goc:360deg; }} }}
@keyframes chu-chay {{ 0% {{ background-position:0% 50%; }} 100% {{ background-position:200% 50%; }} }}
@keyframes vay-tay {{ 0%,60%,100% {{ transform:rotate(0); }} 10%,30% {{ transform:rotate(16deg); }}
                       20%,40% {{ transform:rotate(-10deg); }} 50% {{ transform:rotate(8deg); }} }}
@keyframes nhap-nhay {{ 0%,100% {{ opacity:.25; transform:scale(.6) rotate(0); }}
                          50% {{ opacity:1; transform:scale(1.15) rotate(45deg); }} }}
@keyframes noi-len {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:none; }} }}

/* 1. viền phát sáng chạy quanh khung */
.st-key-khung_dang_nhap {{ position:relative !important; overflow:visible !important; }}
.st-key-khung_dang_nhap::before {{ content:""; position:absolute; inset:-1.5px; border-radius:inherit; padding:2px; pointer-events:none;
    background:conic-gradient(from var(--goc), transparent 0deg, rgba(139,195,74,.95) 50deg, #F2C35B 95deg,
               #E8743B 135deg, transparent 185deg, transparent 360deg);
    -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite:xor; mask-composite:exclude; animation:xoay-goc 5.5s linear infinite; z-index:3; }}

/* 2. đèn rọi theo chuột */
.nen-hieu-ung .den {{ position:absolute; inset:0;
    background:radial-gradient(520px circle at var(--mx, 50%) var(--my, 35%), rgba(255,231,160,.16), transparent 62%);
    transition:background .08s linear; }}

/* 3. tiêu đề lấp lánh + tay vẫy + ✨ nhấp nháy */
.dn-tieu-de .chu-chay {{ background:linear-gradient(90deg, #22301F 0%, #22301F 35%, #3B8A2B 45%, #D9A12B 50%,
    #3B8A2B 55%, #22301F 65%, #22301F 100%); background-size:200% 100%; -webkit-background-clip:text;
    background-clip:text; color:transparent; animation:chu-chay 4s linear infinite; }}
.dn-tieu-de .tay {{ display:inline-block; transform-origin:70% 80%; animation:vay-tay 2.6s ease-in-out infinite; }}
.dn-tieu-de .sao {{ display:inline-block; animation:nhap-nhay 1.8s ease-in-out infinite; }}

/* 4. biểu tượng trong ô nhập */
.st-key-khung_dang_nhap input[aria-label="Email"], .st-key-khung_dang_nhap input[aria-label="Mật khẩu"], .st-key-khung_dang_nhap input[aria-label="Nhập lại mật khẩu"],
.st-key-khung_dang_nhap input[aria-label="Họ và tên"] {{ padding-left:44px !important; background-repeat:no-repeat !important;
    background-position:14px center !important; background-size:19px 19px !important; }}
.st-key-khung_dang_nhap input[aria-label="Email"] {{ background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%239A8F88%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%223%22%20y%3D%225%22%20width%3D%2218%22%20height%3D%2214%22%20rx%3D%222%22/%3E%3Cpolyline%20points%3D%223%207%2012%2013%2021%207%22/%3E%3C/svg%3E") !important; }}
.st-key-khung_dang_nhap input[aria-label="Mật khẩu"], .st-key-khung_dang_nhap input[aria-label="Nhập lại mật khẩu"] {{ background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%239A8F88%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%224%22%20y%3D%2211%22%20width%3D%2216%22%20height%3D%2210%22%20rx%3D%222%22/%3E%3Cpath%20d%3D%22M8%2011V7a4%204%200%200%201%208%200v4%22/%3E%3C/svg%3E") !important; }}
.st-key-khung_dang_nhap input[aria-label="Họ và tên"] {{ background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%239A8F88%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%228%22%20r%3D%224%22/%3E%3Cpath%20d%3D%22M4%2021v-1a6%206%200%200%201%206-6h4a6%206%200%200%201%206%206v1%22/%3E%3C/svg%3E") !important; }}

/* 5. các phần lần lượt hiện ra */
.st-key-khung_dang_nhap [data-testid="stElementContainer"], .st-key-khung_dang_nhap .stElementContainer {{ animation:noi-len .6s cubic-bezier(.2,.8,.2,1) both; }}
.st-key-khung_dang_nhap [data-testid="stElementContainer"]:nth-child(1) {{ animation-delay:.25s; }}
.st-key-khung_dang_nhap [data-testid="stElementContainer"]:nth-child(2) {{ animation-delay:.35s; }}
.st-key-khung_dang_nhap [data-testid="stElementContainer"]:nth-child(3) {{ animation-delay:.45s; }}
.st-key-khung_dang_nhap [data-testid="stElementContainer"]:nth-child(4) {{ animation-delay:.55s; }}
.st-key-khung_dang_nhap [data-testid="stElementContainer"]:nth-child(5) {{ animation-delay:.65s; }}
.st-key-khung_dang_nhap [data-testid="stElementContainer"]:nth-child(n+6) {{ animation-delay:.75s; }}

/* 6. lấp lánh quanh logo */
.dn-dau {{ position:relative; }}
.dn-dau .lap-lanh {{ position:absolute; width:14px; height:14px; pointer-events:none;
    animation:nhap-nhay 2.4s ease-in-out infinite; }}
.dn-dau .lap-lanh::before {{ content:""; position:absolute; inset:0; background:#FFE7A3;
    clip-path:polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
    filter:drop-shadow(0 0 6px rgba(255,220,130,.9)); }}

/* 7. nút chính toả sáng + mũi tên khi rê chuột */
.st-key-khung_dang_nhap button[kind="primaryFormSubmit"]:hover, .st-key-khung_dang_nhap button[data-testid="stBaseButton-primaryFormSubmit"]:hover {{
    box-shadow:0 0 0 4px rgba(232,116,59,.18), 0 16px 34px rgba(232,116,59,.55) !important; }}
.st-key-khung_dang_nhap button[kind="primaryFormSubmit"] p::after, .st-key-khung_dang_nhap button[data-testid="stBaseButton-primaryFormSubmit"] p::after {{
    content:"→"; display:inline-block; margin-left:0; max-width:0; opacity:0; overflow:hidden; vertical-align:bottom;
    transition:max-width .25s ease, margin .25s ease, opacity .25s ease; }}
.st-key-khung_dang_nhap button[kind="primaryFormSubmit"]:hover p::after, .st-key-khung_dang_nhap button[data-testid="stBaseButton-primaryFormSubmit"]:hover p::after {{
    max-width:1.2em; margin-left:.45em; opacity:1; }}

/* ô nhập */
.st-key-khung_dang_nhap div[data-baseweb="input"] {{ border-radius:12px !important; border:1.5px solid #E7DFD8 !important;
    background:#FFFCF9 !important; transition:all .2s ease; }}
.st-key-khung_dang_nhap div[data-baseweb="input"]:focus-within {{ border-color:{CAM} !important;
    box-shadow:0 0 0 4px rgba(232,116,59,.18) !important; background:#fff !important; }}
.st-key-khung_dang_nhap input {{ padding:12px 14px !important; font-size:1rem !important; }}
.st-key-khung_dang_nhap label p {{ font-weight:600 !important; color:#3F3833 !important; }}
.st-key-khung_dang_nhap div[data-testid="stForm"] {{ border:none !important; padding:0 !important;
    box-shadow:none !important; background:transparent !important; }}

/* nút */
.st-key-khung_dang_nhap button[kind="primaryFormSubmit"], .st-key-khung_dang_nhap button[data-testid="stBaseButton-primaryFormSubmit"] {{
    position:relative; overflow:hidden; border:none !important; border-radius:14px !important;
    min-height:50px; background:linear-gradient(135deg, #F08A4B 0%, {CAM} 45%, #D45F2A 100%) !important;
    box-shadow:0 10px 22px rgba(232,116,59,.38); transition:transform .2s ease, box-shadow .2s ease; }}
.st-key-khung_dang_nhap button[kind="primaryFormSubmit"] p,
.st-key-khung_dang_nhap button[data-testid="stBaseButton-primaryFormSubmit"] p {{ font-size:1.05rem !important; font-weight:800 !important; }}
.st-key-khung_dang_nhap button[kind="primaryFormSubmit"]:hover,
.st-key-khung_dang_nhap button[data-testid="stBaseButton-primaryFormSubmit"]:hover {{ transform:translateY(-2px);
    box-shadow:0 16px 30px rgba(232,116,59,.48); }}
.st-key-khung_dang_nhap button[kind="primaryFormSubmit"]::after,
.st-key-khung_dang_nhap button[data-testid="stBaseButton-primaryFormSubmit"]::after {{ content:""; position:absolute; top:0; left:-60%;
    width:45%; height:100%; transform:skewX(-20deg);
    background:linear-gradient(90deg, transparent, rgba(255,255,255,.45), transparent);
    animation:luot-sang 3.2s ease-in-out infinite; }}

.dn-tieu-de {{ font-family:'Noto Serif', Georgia, serif; font-size:1.55rem; font-weight:700; color:{CHU};
               text-align:center; margin:2px 0 2px; }}
.dn-phu {{ text-align:center; color:{CHU_PHU}; font-size:.92rem; margin-bottom:12px; }}
.dn-chan {{ text-align:center; color:rgba(255,255,255,.6); font-size:.82rem; margin-top:22px; }}
</style>""")


def nen_dang_nhap() -> str:
    """Lớp nền: vầng sáng chuyển động + hạt lúa, lá lúa bay lơ lửng."""
    import random
    ngau_nhien = random.Random(7)                  # cố định để mỗi lần tải trông giống nhau
    hat_lua = ('<svg width="{w}" height="{h}" viewBox="0 0 10 18"><ellipse cx="5" cy="9" rx="4" ry="8" '
               'fill="#F2C35B" stroke="#C98A12" stroke-width=".8"/></svg>')
    la_lua = ('<svg width="{w}" height="{h}" viewBox="0 0 12 40"><path d="M6 0 C12 12 11 28 6 40 C1 28 0 12 6 0Z" '
              'fill="#8BC34A" opacity=".85"/></svg>')
    hat = []
    for i in range(18):
        to = ngau_nhien.uniform(.7, 1.6)
        mau = la_lua.format(w=round(10 * to), h=round(32 * to)) if i % 3 == 0 else             hat_lua.format(w=round(9 * to), h=round(16 * to))
        hat.append(f'<span class="hat" style="left:{ngau_nhien.uniform(2, 98):.1f}%;'
                   f'animation-duration:{ngau_nhien.uniform(16, 32):.1f}s;'
                   f'animation-delay:-{ngau_nhien.uniform(0, 30):.1f}s;opacity:.8">{mau}</span>')
    vang = ('<span class="vang" style="width:420px;height:420px;left:-80px;top:-60px;background:rgba(242,179,61,.38)"></span>'
            '<span class="vang" style="width:480px;height:480px;right:-120px;bottom:-140px;background:rgba(232,116,59,.34);animation-delay:-6s"></span>'
            '<span class="vang" style="width:300px;height:300px;left:45%;top:35%;background:rgba(139,195,74,.22);animation-delay:-3s"></span>')
    return gon('<div class="nen-hieu-ung"><span class="den"></span>' + vang + "".join(hat) + "</div>")


def dau_trang_dang_nhap(icon_b64: str, chu_b64: str, khau_hieu: str, phu: str) -> str:
    icon = f'<img class="icon" src="data:image/png;base64,{icon_b64}" alt="Logo">' if icon_b64 else ""
    chu = f'<img class="chu" src="data:image/png;base64,{chu_b64}" alt="Bồ Nông">' if chu_b64 else ""
    lap_lanh = "".join(f'<span class="lap-lanh" style="left:{x}%;top:{y}%;animation-delay:{d}s;'
                       f'transform:scale({k})"></span>'
                       for x, y, d, k in [(30, 8, 0, 1), (68, 2, .8, .8), (73, 52, 1.5, 1.1), (26, 58, 2.1, .7),
                                          (50, 0, 1.1, .6)])
    return gon(f'<div class="dn-dau">{lap_lanh}<div class="cap">{icon}{chu}</div>'
               f'<div class="khau-hieu">{e(khau_hieu)}</div><div class="phu">{phu}</div></div>')


def loi_ich_dang_nhap() -> str:
    """Cột giới thiệu bên cạnh ô đăng nhập."""
    muc = [("🔮", "Dự báo ngày mai, 7 và 30 ngày", "Máy tự chọn mô hình dự báo tốt nhất cho từng giống, từng tỉnh."),
           ("🌾", "Lúa · Cà phê · Hồ tiêu", "Giá tham khảo trong nước theo tỉnh, kèm giá cà phê và hồ tiêu thế giới."),
           ("🔄", "Cập nhật mỗi ngày", "Giá mới được tự động lấy từ các trang báo mỗi sáng.")]
    o = "".join(f'<div class="loi-ich"><div class="bt">{bt}</div><div><div class="td">{e(td)}</div>'
                f'<div class="md">{e(md)}</div></div></div>' for bt, td, md in muc)
    return gon('<div class="loi-chao">Chào mừng bạn 👋</div>'
               '<div class="loi-chao-phu">Đăng nhập hoặc tạo tài khoản miễn phí để xem giá và dự báo '
               'giá nông sản mỗi ngày.</div>' + o)


def thanh_tai_khoan(ho_ten: str, link_trang_chu: str = "?", so_xu: int = None, vip: dict = None,
                    anh_b64: str = "", dang_o_ca_nhan: bool = False) -> str:
    """Thanh điều hướng góc trên: 🏠 Trang chủ · 🪙 số xu · 👑 VIP · ô tài khoản."""
    chu_cai = (ho_ten.strip().split()[-1][:1] if ho_ten.strip() else "?").upper()
    ten_goi = ho_ten.strip().split()[-1] if ho_ten.strip() else ""
    nha = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
           'stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 '
           '1 0 0 0 1-1V9.5"/></svg>')
    xu = ""
    if so_xu is not None:
        xu = (f'<a class="chip-xu" href="?trang=vi" target="_self" title="Ví xu · điểm danh · lịch sử">'
              f'<span class="dong-xu">xu</span><b>{so(so_xu)}</b><span class="don-vi">xu</span></a>')
    if vip:
        nhan_vip = (f'<a class="chip-vip co" href="?trang=vip" target="_self" title="{e(vip["ten"])}">'
                    f'<span class="vuong-mien">{SVG_VUONG_MIEN}</span>VIP<span class="han">đến '
                    f'{vip["ket_thuc"]:%d/%m}</span></a>')
    else:
        nhan_vip = (f'<a class="chip-vip" href="?trang=vip" target="_self" title="Xem các gói VIP">'
                    f'<span class="vuong-mien">{SVG_VUONG_MIEN}</span>Lên VIP</a>')
    return gon(f'<div class="thanh-tai-khoan">'
               f'<a class="nut-trang-chu" href="{e(link_trang_chu)}" target="_self" title="Về Trang chủ">{nha}'
               f'<span>Trang chủ</span></a>'
               f'<a class="chip-nt" href="?trang=nong_trai" target="_self" title="Nông trại · trồng cây nhận xu">'
               f'<span class="cay-nho">🌱</span>Nông trại</a>'
               f'<a class="chip-nt chip-dd" href="?trang=dien_dan" target="_self" title="Diễn đàn · trò chuyện · chợ">'
               f'<span class="cay-nho">💬</span>Diễn đàn</a>{xu}{nhan_vip}'
               f'<a class="chip-tk {"dang-chon" if dang_o_ca_nhan else ""}" href="?trang=ca_nhan" target="_self" '
               f'title="Trang cá nhân">'
               + (f'<span class="avatar co-anh"><img src="data:image/jpeg;base64,{anh_b64}" alt=""></span>' if anh_b64
                  else f'<span class="avatar">{e(chu_cai)}</span>')
               + f'<span class="ten">{e(ten_goi)}</span></a></div>')


def ghi_chu_gia(nong_san: str) -> str:
    """Khung ghi chú về giá thực tế tại đại lý (đặt dưới phần dự báo)."""
    return gon(f'<div class="ghi-chu-gia"><div class="bt">i</div>'
               f'<div>{e(GHI_CHU_GIA.get(nong_san, ""))}</div></div>')


def tach_ten_khu_vuc(khu_vuc: str, nong_san: str):
    """'Đắk Nông (cũ) – nay Lâm Đồng' -> ('Đắk Nông (cũ)', 'Nay thuộc Lâm Đồng')."""
    if " – nay " in khu_vuc:
        ten, nay = khu_vuc.split(" – nay ", 1)
        return ten, f"Nay thuộc {nay}"
    vung = {"Hồ tiêu": "Vùng trồng tiêu", "Cà phê": "Vùng trồng cà phê"}.get(nong_san, "Khu vực")
    return khu_vuc, f"{vung} {khu_vuc}"


def bang_gia_hom_nay(cac_dong: list, ten_cot: str, cot_gia: str, chan: str) -> str:
    """
    Bảng giá mới nhất kiểu báo: tên (+ dòng phụ) · giá phiên trước · giá hôm nay (+ ↑/↓) · Chi tiết.
    cac_dong: [{"ten", "phu", "gia_truoc", "gia_nay", "link", "dang_xem"}]
    """
    hang = []
    for i, d in enumerate(cac_dong):
        chenh = d["gia_nay"] - d["gia_truoc"] if d["gia_truoc"] is not None else 0
        if chenh > 0:
            vien = f'<span class="vien-tang">↑ {so(chenh)}</span>'
        elif chenh < 0:
            vien = f'<span class="vien-giam">↓ {so(-chenh)}</span>'
        else:
            vien = '<span class="vien-ngang">→ 0</span>'
        nut = ('<span class="dang-xem-chu">● Đang xem</span>' if d["dang_xem"] else
               f'<a class="chi-tiet" href="{e(d["link"])}" target="_self">Chi tiết →</a>')
        truoc = so(d["gia_truoc"]) if d["gia_truoc"] is not None else "—"
        hang.append(f"""
<tr class="{'dang-xem' if d['dang_xem'] else ''}">
  <td><div class="ten-kv"><span class="cham" style="background:{MAU_KHU_VUC[i % len(MAU_KHU_VUC)]}"></span>{e(d['ten'])}</div>
      <div class="phu-kv">{e(d['phu'])}</div></td>
  <td class="phai an-nho"><span class="gia-truoc">{truoc}</span></td>
  <td class="phai"><div class="o-gia"><span class="gia">{so(d['gia_nay'])}</span>{vien}</div></td>
  <td class="phai">{nut}</td>
</tr>""")
    return gon(f"""
<div class="bang-ss"><table>
  <thead><tr><th>{e(ten_cot)}</th><th class="phai an-nho">Giá phiên trước</th>
             <th class="phai">{e(cot_gia)}</th><th></th></tr></thead>
  <tbody>{''.join(hang)}</tbody>
</table><div class="chan">{chan}</div></div>""")


def hero_dau(icon_b64: str, chu_b64: str, khau_hieu: str, phu: str) -> str:
    """Dải đầu trang: logo bồ nông + chữ 'Bồ Nông' ở chính giữa, to và nổi bật."""
    icon = f'<img class="icon" src="data:image/png;base64,{icon_b64}" alt="Logo">' if icon_b64 else ""
    chu = f'<img class="chu" src="data:image/png;base64,{chu_b64}" alt="Bồ Nông">' if chu_b64 else ""
    return gon(f'<div class="hero-dau"><div class="cap">{icon}{chu}</div>'
               f'<div class="khau-hieu">{e(khau_hieu)}</div><div class="phu">{phu}</div></div>')


def thanh_dau(logo_b64: str, ten_app: str, phu: str) -> str:
    anh = f'<img src="data:image/png;base64,{logo_b64}">' if logo_b64 else ""
    return gon(f'<div class="thanh-dau">{anh}<div><div class="ten">{e(ten_app)}</div>'
               f'<div class="phu">{e(phu)}</div></div></div>')


# Hình vẽ riêng cho từng nông sản (hiện giống nhau trên mọi máy)
HINH_VE = {
    "Lúa": """<svg viewBox="0 0 64 64">
  <path d="M29 61 C29 46 31 31 41 11" stroke="#5E8F2B" stroke-width="2.6" fill="none" stroke-linecap="round"/>
  <path d="M29 56 C19 51 12 42 10 30 C21 34 27 43 29 56Z" fill="#7CB342"/>
  <path d="M29 56 C17 47 15 40 10 30" stroke="#5E8F2B" stroke-width="1" fill="none"/>
  <path d="M30 58 C38 52 47 50 56 50 C49 56 40 59 30 58Z" fill="#8BC34A"/>
  <g fill="#F2B33D" stroke="#C98A12" stroke-width="1">
    <ellipse cx="42" cy="9" rx="3" ry="5.6" transform="rotate(25 42 9)"/>
    <ellipse cx="46" cy="17" rx="3" ry="5.6" transform="rotate(58 46 17)"/>
    <ellipse cx="36" cy="16" rx="3" ry="5.6" transform="rotate(-22 36 16)"/>
    <ellipse cx="43" cy="25" rx="3" ry="5.6" transform="rotate(62 43 25)"/>
    <ellipse cx="33" cy="23" rx="3" ry="5.6" transform="rotate(-28 33 23)"/>
    <ellipse cx="40" cy="33" rx="3" ry="5.6" transform="rotate(64 40 33)"/>
    <ellipse cx="31" cy="31" rx="3" ry="5.6" transform="rotate(-32 31 31)"/>
    <ellipse cx="37" cy="41" rx="3" ry="5.6" transform="rotate(66 37 41)"/>
  </g></svg>""",
    "Cà phê": """<svg viewBox="0 0 64 64">
  <g transform="rotate(-28 24 36)">
    <ellipse cx="24" cy="36" rx="12.5" ry="18" fill="#6F4325"/>
    <ellipse cx="20" cy="29" rx="4" ry="8" fill="#fff" opacity=".16"/>
    <path d="M24 19 C18.5 29 29.5 42 24 53" stroke="#3B2314" stroke-width="2.6" fill="none" stroke-linecap="round"/>
  </g>
  <g transform="rotate(24 43 27)">
    <ellipse cx="43" cy="27" rx="11" ry="16" fill="#8B5A33"/>
    <ellipse cx="39.5" cy="21" rx="3.4" ry="7" fill="#fff" opacity=".18"/>
    <path d="M43 12 C38 21 48 32 43 42" stroke="#4A2C18" stroke-width="2.4" fill="none" stroke-linecap="round"/>
  </g></svg>""",
    "Hồ tiêu": """<svg viewBox="0 0 64 64">
  <path d="M24 10 C34 2 52 6 57 19 C44 24 31 21 24 10Z" fill="#6BA539"/>
  <path d="M24 10 C36 12 46 15 57 19" stroke="#4E7F25" stroke-width="1.2" fill="none"/>
  <path d="M21 8 C26 22 29 38 33 60" stroke="#5E8F2B" stroke-width="2.2" fill="none" stroke-linecap="round"/>
  <g stroke="rgba(0,0,0,.18)" stroke-width=".8">
    <circle cx="20" cy="20" r="4.4" fill="#5A7D2A"/><circle cx="29" cy="21" r="4.4" fill="#6E8F2F"/>
    <circle cx="22" cy="28.5" r="4.6" fill="#B3261E"/><circle cx="31" cy="29.5" r="4.6" fill="#8E1F1F"/>
    <circle cx="24" cy="37.5" r="4.7" fill="#C2352A"/><circle cx="33" cy="38.5" r="4.7" fill="#3E2A23"/>
    <circle cx="26" cy="46.5" r="4.6" fill="#8E1F1F"/><circle cx="35" cy="47.5" r="4.6" fill="#B3261E"/>
    <circle cx="29" cy="55" r="4.2" fill="#3E2A23"/>
  </g>
  <g fill="#fff" opacity=".35">
    <circle cx="21" cy="27" r="1.2"/><circle cx="30" cy="28" r="1.2"/><circle cx="23" cy="36" r="1.2"/>
    <circle cx="25" cy="45" r="1.2"/><circle cx="34" cy="46" r="1.2"/>
  </g></svg>""",
}


def chon_nong_san(cac_the: list, dang_chon: str) -> str:
    """3 huy hiệu tròn bấm được: [{"ten", "mo_ta", "link"}]. Huy hiệu đang chọn có vòng màu xoay."""
    o = []
    for t in cac_the:
        dam, dam_hon, nhat = CHU_DE[t["ten"]]
        chon = t["ten"] == dang_chon
        o.append(f"""
<a class="huy-hieu {'dang-chon' if chon else ''}" href="{e(t['link'])}" target="_self"
   style="--m:{dam};--m2:{dam_hon};--n:{nhat}" title="Xem giá & dự báo {e(t['ten'].lower())}">
  <div class="vanh"><div class="dia">{gon(HINH_VE[t['ten']])}</div>
    {'<div class="tick">✓</div>' if chon else ''}</div>
  <div class="ten">{e(t['ten'])}</div>
  <div class="mo-ta">{e(t['mo_ta'])}</div>
  <div class="gach"></div>
</a>""")
    return gon('<div class="chon-ns-nhan">Chọn nông sản để xem giá & dự báo</div>'
               '<div class="chon-ns">' + "".join(o) + "</div>")


def the_chon_nong_san(ten: str, mo_ta: str, khoang_gia: str, ngay) -> str:
    dam, dam_hon, _ = CHU_DE[ten]
    return gon(f"""
<div class="the-chon" style="background:linear-gradient(135deg,{dam} 0%,{dam_hon} 100%)">
  <div class="icon">{BIEU_TUONG[ten]}</div>
  <div class="ten">{e(ten)}</div>
  <div class="mota">{e(mo_ta)}</div>
  <div class="nhan-gia">Giá hiện tại</div>
  <div class="gia">{khoang_gia} <span style="font-size:.95rem;font-weight:500">đ/kg</span></div>
  <div class="ngay">Cập nhật {ngay:%d/%m/%Y}</div>
</div>""")


# ================================================================ XU & VIP
VANG_DAM = "#B7791F"


def css_vi() -> str:
    """CSS cho ví xu, gói VIP, ô bị khoá (dùng cùng css() chung)."""
    return gon(f"""
<style>
/* --- chip xu & VIP trên thanh tài khoản --- */
.thanh-tai-khoan a.chip-xu {{ padding:0 16px 0 6px; background:#FFF8E6; color:#7A4B00 !important;
    border:1.5px solid #F6DFA6; box-shadow:0 2px 8px rgba(183,121,31,.12); }}
.thanh-tai-khoan a.chip-xu:hover {{ transform:translateY(-2px); box-shadow:0 8px 18px rgba(183,121,31,.25); }}
.thanh-tai-khoan a.chip-xu b {{ font-size:1.05rem; }}
.thanh-tai-khoan a.chip-xu .don-vi {{ font-weight:600; font-size:.85rem; opacity:.8; margin-left:-4px; }}
.dong-xu {{ width:32px; height:32px; border-radius:50%; display:inline-flex; align-items:center;
    justify-content:center; font-size:.68rem; font-weight:800; color:#7A4B00; letter-spacing:-.02em;
    background:radial-gradient(circle at 35% 30%, #FFF3C4 0%, #F8C843 45%, #D99A1E 100%);
    box-shadow:inset 0 -2px 0 rgba(122,75,0,.25), 0 1px 3px rgba(122,75,0,.3); }}
.thanh-tai-khoan a.chip-vip {{ padding:0 16px 0 12px; color:{VANG_DAM} !important; background:#fff;
    border:1.5px dashed #E9C46A; }}
.thanh-tai-khoan a.chip-vip:hover {{ transform:translateY(-2px); background:#FFFBEF; }}
.thanh-tai-khoan a.chip-vip.co {{ color:#fff !important; border:none;
    background:linear-gradient(135deg,#F4C24D 0%,#D9971E 55%,#A8650E 100%);
    box-shadow:0 6px 14px rgba(168,101,14,.3), inset 0 1px 0 rgba(255,255,255,.35); }}
.thanh-tai-khoan a.chip-vip .han {{ font-weight:600; font-size:.8rem; opacity:.9; }}
.vuong-mien svg {{ width:18px; height:18px; display:block; }}

.thanh-tai-khoan a.chip-nt {{ padding:0 16px 0 10px; color:#2F6B22 !important; background:#F1F8EC;
    border:1.5px solid #CFE6C4; }}
.thanh-tai-khoan a.chip-nt:hover {{ transform:translateY(-2px); background:#E3F2DA; box-shadow:0 8px 18px -8px rgba(47,107,34,.45); }}
.thanh-tai-khoan a.chip-nt .cay-nho {{ display:inline-block; font-size:1.1rem; transform-origin:50% 90%;
    animation:dung-dua-nho 2.6s ease-in-out infinite; }}
@keyframes dung-dua-nho {{ 0%,100% {{ transform:rotate(-8deg); }} 50% {{ transform:rotate(8deg); }} }}

/* --- ô dự báo bị khoá --- */
.o.du-bao.khoa {{ background:repeating-linear-gradient(135deg,#FBF8F5 0 12px,#F6F1EC 12px 24px);
    border:1.5px dashed #DCCFC4; }}
.o.du-bao.khoa .nhan {{ color:{CHU_PHU}; }}
.khoa-giua {{ text-align:center; padding:.6rem 0 .2rem; }}
.o-khoa-icon {{ width:48px; height:48px; margin:0 auto .35rem; border-radius:14px; display:flex;
    align-items:center; justify-content:center; color:#fff;
    background:linear-gradient(135deg,#F4C24D 0%,#C9851A 100%); box-shadow:0 6px 14px rgba(168,101,14,.28); }}
.o-khoa-icon svg {{ width:26px; height:26px; }}
.khoa-chu {{ font-family:'Noto Serif', Georgia, serif; font-size:1.35rem; font-weight:700; color:{CHU}; }}
.khoa-phu {{ color:{CHU_PHU}; font-size:.86rem; line-height:1.5; margin-top:.2rem; }}
.khoa-phu b {{ color:{VANG_DAM}; }}

/* --- khung khoá (biểu đồ, bảng, nút tải) --- */
.khung-khoa {{ display:flex; gap:16px; align-items:center; padding:18px 20px; border-radius:16px;
    background:linear-gradient(135deg,#FFFBEF 0%,#FFF4DA 100%); border:1px solid #F3DDA2; margin:.4rem 0 .6rem; }}
.khung-khoa .o-khoa-icon {{ margin:0; flex:none; }}
.khung-khoa .td {{ font-weight:800; color:{CHU}; font-size:1.02rem; }}
.khung-khoa .md {{ color:#6B5A3E; font-size:.92rem; line-height:1.55; margin-top:2px; }}
.da-mo {{ display:inline-flex; gap:8px; align-items:center; background:#EEF7EA; color:#2F6B22;
    border:1px solid #CFE6C4; border-radius:999px; padding:6px 14px; font-size:.88rem; font-weight:600;
    margin:.5rem 0 .2rem; }}

/* --- nút dạng link --- */
a.nut-link {{ display:flex; align-items:center; justify-content:center; gap:8px; height:2.6rem;
    border-radius:12px; font-weight:700; text-decoration:none !important; font-size:.95rem;
    color:#fff !important; background:linear-gradient(135deg,#F4C24D 0%,#D9971E 55%,#A8650E 100%);
    box-shadow:0 6px 14px rgba(168,101,14,.25); transition:transform .2s ease; }}
a.nut-link:hover {{ transform:translateY(-2px); }}
a.nut-link svg {{ width:18px; height:18px; }}
a.nut-link.nhat {{ background:#fff; color:{VANG_DAM} !important; border:1.5px solid #E9C46A; box-shadow:none; }}

/* --- tiêu đề trang con --- */
.dau-trang-con {{ display:flex; align-items:center; gap:16px; margin:.8rem 0 .4rem; }}
.dau-trang-con .bt {{ width:58px; height:58px; border-radius:18px; display:flex; align-items:center;
    justify-content:center; flex:none; color:#fff;
    background:linear-gradient(135deg,#F4C24D 0%,#C9851A 100%); box-shadow:0 8px 18px rgba(168,101,14,.28); }}
.dau-trang-con .bt svg {{ width:32px; height:32px; }}
.dau-trang-con .bt .dong-xu {{ width:46px; height:46px; font-size:.95rem; }}
.dau-trang-con h1 {{ font-family:'Noto Serif', Georgia, serif !important; font-size:2.1rem !important;
    font-weight:700 !important; color:{CHU} !important; margin:0 !important; padding:0 !important; }}
.dau-trang-con .phu {{ color:{CHU_PHU}; font-size:.98rem; }}

/* --- thẻ ví --- */
.the-vi {{ position:relative; overflow:hidden; border-radius:22px; padding:26px 28px; color:#fff;
    background:linear-gradient(135deg,#2F6B22 0%,#1F4A16 70%); box-shadow:0 12px 28px rgba(31,74,22,.28); }}
.the-vi:after {{ content:""; position:absolute; right:-40px; top:-40px; width:200px; height:200px; border-radius:50%;
    background:radial-gradient(circle,#F8C84355 0%,transparent 70%); }}
.the-vi .nhan {{ font-size:.8rem; letter-spacing:.08em; text-transform:uppercase; opacity:.8; font-weight:700; }}
.the-vi .so {{ font-family:'Noto Serif', Georgia, serif; font-size:3rem; font-weight:700; line-height:1.1;
    margin:.3rem 0; display:flex; align-items:center; gap:12px; }}
.the-vi .so .dong-xu {{ width:44px; height:44px; font-size:.9rem; }}
.the-vi .so small {{ font-size:1.1rem; font-weight:500; opacity:.85; }}
.the-vi .phu {{ opacity:.9; font-size:.93rem; line-height:1.6; }}
.the-vi .canh-bao {{ display:inline-block; margin-top:10px; background:rgba(255,255,255,.14);
    border:1px solid rgba(255,255,255,.25); padding:5px 12px; border-radius:999px; font-size:.85rem; }}
.o-nho {{ background:#fff; border:1px solid {VIEN}; border-radius:16px; padding:16px 18px; height:100%; }}
.o-nho .td {{ font-weight:800; color:{CHU}; }}
.o-nho .md {{ color:{CHU_PHU}; font-size:.9rem; line-height:1.55; margin-top:4px; }}
.chuoi-ngay {{ display:flex; gap:6px; margin:.7rem 0 .2rem; }}
.chuoi-ngay span {{ flex:1; height:30px; border-radius:8px; display:flex; align-items:center; justify-content:center;
    font-size:.75rem; font-weight:700; background:#F3EEE9; color:{CHU_PHU}; }}
.chuoi-ngay span.co {{ background:linear-gradient(135deg,#F8C843 0%,#D99A1E 100%); color:#5A3800; }}
.chuoi-ngay span.thuong {{ border:1.5px dashed #E9C46A; }}

/* --- thẻ gói VIP (bản mới: 4 tầng + dải Nhóm) --- */
@property --goc-vip {{ syntax:'<angle>'; inherits:false; initial-value:0deg; }}
@keyframes xoay-vip {{ to {{ --goc-vip:360deg; }} }}
@keyframes bay-vip {{ 0%,100% {{ transform:translateY(0) rotate(0deg); }} 50% {{ transform:translateY(-7px) rotate(-3deg); }} }}
@keyframes noi-vip {{ from {{ opacity:0; transform:translateY(26px) scale(.97); }} to {{ opacity:1; transform:none; }} }}
@keyframes lap-vip {{ 0%,100% {{ opacity:0; transform:scale(.3) rotate(0deg); }} 50% {{ opacity:1; transform:scale(1) rotate(90deg); }} }}
@keyframes vang-chay {{ to {{ background-position:200% center; }} }}
@keyframes nhip-vip {{ 0%,100% {{ box-shadow:0 0 0 0 var(--hao); }} 50% {{ box-shadow:0 0 0 10px transparent; }} }}
.cac-goi {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:18px; margin:1.4rem 0 .5rem;
    align-items:stretch; }}
@media (max-width: 1050px) {{ .cac-goi {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
@media (max-width: 580px) {{ .cac-goi {{ grid-template-columns:1fr; }} }}
.goi-vo {{ position:relative; border-radius:24px; padding:1.5px; background:{VIEN};
    animation:noi-vip .7s cubic-bezier(.2,.8,.2,1) backwards;
    transform:perspective(1100px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) translateY(var(--ty,0px));
    transition:transform .55s cubic-bezier(.2,.8,.2,1); will-change:transform; }}
.goi-vo.nghieng {{ transition:transform .12s linear; }}
.goi-vo:nth-child(2) {{ animation-delay:.08s; }} .goi-vo:nth-child(3) {{ animation-delay:.16s; }}
.goi-vo:nth-child(4) {{ animation-delay:.24s; }}
.goi-vo:hover {{ --ty:-10px; }}
.goi-vo.mau {{ background:linear-gradient(160deg, var(--m1) 0%, transparent 45%, transparent 70%, var(--m2) 100%); }}
.goi {{ position:relative; overflow:hidden; height:100%; box-sizing:border-box; border-radius:22.5px;
    background:#fff; padding:26px 22px 22px; display:flex; flex-direction:column;
    box-shadow:0 2px 6px rgba(60,20,20,.04), 0 14px 32px -12px rgba(60,20,20,.12);
    transition:box-shadow .35s ease; }}
.goi-vo:hover .goi {{ box-shadow:0 26px 50px -18px var(--bong, rgba(60,20,20,.25)); }}
.goi:before {{ content:""; position:absolute; inset:0 0 auto 0; height:120px; pointer-events:none;
    background:radial-gradient(120% 100% at 50% 0%, var(--nen) 0%, transparent 70%); }}
.goi:after {{ content:""; position:absolute; top:0; left:-60%; width:45%; height:100%; pointer-events:none;
    background:linear-gradient(105deg, transparent, rgba(255,255,255,.55), transparent);
    transform:skewX(-18deg) translateX(-120%); transition:transform .9s ease; }}
.goi-vo:hover .goi:after {{ transform:skewX(-18deg) translateX(520%); }}
.goi .icon-goi {{ position:relative; width:64px; height:64px; border-radius:20px; display:flex; align-items:center;
    justify-content:center; color:#fff; background:linear-gradient(140deg, var(--m1), var(--m2));
    box-shadow:0 12px 24px -8px var(--bong), inset 0 1px 0 rgba(255,255,255,.35);
    animation:bay-vip 3.8s ease-in-out infinite; }}
.goi-vo:nth-child(2) .icon-goi {{ animation-delay:-.9s; }} .goi-vo:nth-child(3) .icon-goi {{ animation-delay:-1.8s; }}
.goi-vo:nth-child(4) .icon-goi {{ animation-delay:-2.7s; }}
.goi .icon-goi svg {{ width:34px; height:34px; }}
.goi .hang {{ font-size:.72rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--m2);
    margin-top:1.1rem; }}
.goi .ten {{ font-family:'Noto Serif', Georgia, serif; font-size:1.42rem; font-weight:700; color:{CHU};
    margin-top:.15rem; line-height:1.25; }}
.goi .ky {{ color:{CHU_PHU}; font-size:.88rem; margin-top:.1rem; }}
.goi .gia {{ font-family:'Noto Serif', Georgia, serif; font-size:2.15rem; font-weight:700; color:{CHU};
    margin:1rem 0 0; line-height:1.1; letter-spacing:-.01em; }}
.goi .gia small {{ font-size:1rem; font-weight:600; color:{CHU_PHU}; margin-left:3px; }}
.goi .thang {{ color:{CHU_PHU}; font-size:.85rem; margin-top:.25rem; min-height:1.3em; }}
.goi .thang b {{ color:var(--m2); }}
.goi .vach {{ height:1px; margin:1.05rem 0 .4rem;
    background:linear-gradient(90deg, transparent, {VIEN} 15%, {VIEN} 85%, transparent); }}
.goi ul {{ list-style:none; padding:0; margin:0; font-size:.9rem; color:#3F3833; flex:1; }}
.goi li {{ display:flex; gap:10px; align-items:flex-start; padding:6px 0; line-height:1.45; }}
.goi li .dau {{ flex:none; width:20px; height:20px; border-radius:50%; display:flex; align-items:center;
    justify-content:center; font-size:.7rem; font-weight:900; margin-top:1px; color:#fff;
    background:linear-gradient(140deg, var(--m1), var(--m2)); }}
.goi li.khong {{ color:#B5AAA1; }}
.goi li.khong .dau {{ background:#EFE8E2; color:#B5AAA1; }}
.goi .ruy-bang {{ position:absolute; top:16px; right:16px; z-index:2; font-size:.72rem; font-weight:800;
    padding:5px 11px; border-radius:999px; color:#fff; background:linear-gradient(135deg, var(--m1), var(--m2));
    box-shadow:0 6px 14px -4px var(--bong); }}
.goi .dang-dung {{ position:absolute; top:16px; right:16px; z-index:2; font-size:.72rem; font-weight:800;
    padding:5px 11px; border-radius:999px; color:#2F6B22; background:#EAF6E4; border:1px solid #CBE6BE; }}
.goi .dang-dung:before {{ content:"● "; color:#46A033; }}

/* màu từng tầng */
.goi-vo.t-mien-phi {{ --m1:#5CC24A; --m2:#2F7A24; --nen:#EEF8EA; --bong:rgba(47,122,36,.35); --hao:rgba(47,122,36,.35); }}
.goi-vo.t-mua-vang {{ --m1:#FFD25C; --m2:#D48A06; --nen:#FFF6DB; --bong:rgba(212,138,6,.42); --hao:rgba(212,138,6,.4); }}
.goi-vo.t-boi-thu {{ --m1:#34D399; --m2:#047857; --nen:#E6F8F0; --bong:rgba(4,120,87,.38); --hao:rgba(4,120,87,.35); }}

/* Đại Điền: thẻ tối, viền vàng-cam xoay, lấp lánh */
.goi-vo.t-dai-dien {{ --m1:#FFB648; --m2:#E8743B; --bong:rgba(232,116,59,.55); --hao:rgba(232,116,59,.45);
    padding:2.5px; background:conic-gradient(from var(--goc-vip), #E8743B, #FFD25C, #3B2A12, #FFB648, #E8743B);
    animation:noi-vip .7s cubic-bezier(.2,.8,.2,1) .24s backwards, xoay-vip 5s linear infinite;
    box-shadow:0 22px 50px -18px rgba(232,116,59,.6); }}
@media (min-width: 1051px) {{ .goi-vo.t-dai-dien {{ --ty:-14px; }} .goi-vo.t-dai-dien:hover {{ --ty:-22px; }} }}
.t-dai-dien .goi {{ background:radial-gradient(130% 90% at 80% 0%, #3A2A12 0%, #17120C 55%, #0E0C09 100%);
    color:#F5EBDD; border-radius:21.5px; }}
.t-dai-dien .goi:before {{ background:radial-gradient(90% 70% at 50% 0%, rgba(255,182,72,.22) 0%, transparent 70%); }}
.t-dai-dien .goi:after {{ background:linear-gradient(105deg, transparent, rgba(255,214,140,.28), transparent); }}
.t-dai-dien .goi .ten, .t-dai-dien .goi .gia {{ color:#FFF4E2; }}
.t-dai-dien .goi .gia {{ background:linear-gradient(90deg,#FFE7A8,#FFB648,#FFF1C9,#FFB648,#FFE7A8);
    background-size:200% auto; -webkit-background-clip:text; background-clip:text; color:transparent;
    animation:vang-chay 4s linear infinite; }}
.t-dai-dien .goi .hang {{ color:#FFB648; }}
.t-dai-dien .goi .ky, .t-dai-dien .goi .thang, .t-dai-dien .goi .gia small {{ color:#C9B79F; }}
.t-dai-dien .goi .thang b {{ color:#FFD25C; }}
.t-dai-dien .goi .vach {{ background:linear-gradient(90deg, transparent, rgba(255,182,72,.35), transparent); }}
.t-dai-dien .goi ul {{ color:#EDE2D2; }}
.t-dai-dien .goi .icon-goi {{ animation:bay-vip 3.8s ease-in-out infinite, nhip-vip 2.4s ease-out infinite; }}
.t-dai-dien .tia {{ position:absolute; width:14px; height:14px; pointer-events:none; color:#FFD25C;
    animation:lap-vip 2.8s ease-in-out infinite; }}
.t-dai-dien .tia svg {{ width:100%; height:100%; display:block; }}
.t-dai-dien .tia.a {{ top:22px; left:100px; }} .t-dai-dien .tia.b {{ top:96px; right:28px; width:10px; height:10px; animation-delay:.9s; }}
.t-dai-dien .tia.c {{ top:178px; right:66px; width:8px; height:8px; animation-delay:1.7s; }}
.t-dai-dien .tia.d {{ bottom:80px; left:20px; width:9px; height:9px; animation-delay:.5s; }}

/* dải VIP Nhóm */
.goi-nhom {{ position:relative; overflow:hidden; display:flex; align-items:center; gap:22px; flex-wrap:wrap;
    margin:1.6rem 0 .5rem; padding:22px 26px; border-radius:22px; color:#fff;
    background:linear-gradient(120deg,#1F4A16 0%,#2F6B22 45%,#0F766E 100%);
    box-shadow:0 18px 40px -18px rgba(15,118,110,.6); animation:noi-vip .7s .32s cubic-bezier(.2,.8,.2,1) backwards; }}
.goi-nhom:after {{ content:""; position:absolute; right:-80px; top:-80px; width:260px; height:260px; border-radius:50%;
    background:radial-gradient(circle, rgba(255,210,92,.28) 0%, transparent 70%); }}
.goi-nhom .icon-goi {{ width:60px; height:60px; border-radius:18px; flex:none; display:flex; align-items:center;
    justify-content:center; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.25);
    animation:bay-vip 4s ease-in-out infinite; }}
.goi-nhom .icon-goi svg {{ width:32px; height:32px; }}
.goi-nhom .giua {{ flex:1; min-width:220px; position:relative; z-index:1; }}
.goi-nhom .ten {{ font-family:'Noto Serif', Georgia, serif; font-size:1.35rem; font-weight:700; }}
.goi-nhom .md {{ opacity:.88; font-size:.92rem; line-height:1.55; margin-top:2px; }}
.goi-nhom .phai {{ text-align:right; position:relative; z-index:1; }}
.goi-nhom .gia {{ font-family:'Noto Serif', Georgia, serif; font-size:1.9rem; font-weight:700; line-height:1.1; }}
.goi-nhom .gia small {{ font-size:.95rem; font-weight:500; opacity:.8; }}
.goi-nhom .thang {{ font-size:.85rem; opacity:.85; }}
.goi-nhom .ruy-bang {{ display:inline-block; margin-top:6px; font-size:.72rem; font-weight:800; padding:4px 10px;
    border-radius:999px; background:#FFD25C; color:#5A3800; }}

/* ===== hiệu ứng nâng cao ===== */
@keyframes nut-chay {{ from {{ background-position:100% 0; }} to {{ background-position:-150% 0; }} }}
@keyframes ve-net {{ to {{ stroke-dashoffset:0; }} }}
@keyframes vong-lan {{ from {{ opacity:.9; transform:scale(.9); }} to {{ opacity:0; transform:scale(1.45); }} }}
@keyframes noi-li {{ from {{ opacity:0; transform:translateX(-10px); }} to {{ opacity:1; transform:none; }} }}
@keyframes troi-cuc {{ 0%,100% {{ transform:translate(0,0) scale(1); }} 33% {{ transform:translate(60px,-30px) scale(1.12); }}
    66% {{ transform:translate(-40px,25px) scale(.92); }} }}
@keyframes hat-len {{ 0% {{ transform:translateY(0) rotate(0deg); opacity:0; }} 12% {{ opacity:.85; }}
    85% {{ opacity:.55; }} 100% {{ transform:translateY(-560px) rotate(280deg); opacity:0; }} }}
@keyframes nhip-nut {{ 0%,100% {{ filter:drop-shadow(0 0 0 rgba(232,116,59,0)); }}
    50% {{ filter:drop-shadow(0 0 16px rgba(232,116,59,.75)); }} }}
@keyframes dong-chay {{ to {{ background-position:-200% 0; }} }}
@keyframes nhun {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-4px); }} }}
@keyframes bui-vang {{ 0% {{ transform:translate(0,0); opacity:0; }} 20% {{ opacity:1; }}
    100% {{ transform:translate(var(--dx,20px),-95px); opacity:0; }} }}

/* sân khấu: cụm ánh sáng mờ trôi + hạt lúa, lá non bay lên phía sau các thẻ */
.san-vip {{ position:relative; padding:4px 0 6px; isolation:isolate; }}
.san-vip .cuc-quang {{ position:absolute; z-index:-1; border-radius:50%; opacity:.75;
    animation:troi-cuc 16s ease-in-out infinite; pointer-events:none; }}
.san-vip .cuc-quang.a {{ width:340px; height:340px; left:-60px; top:40px; background:radial-gradient(circle, #CDEFC0 0%, rgba(205,239,192,0) 68%); }}
.san-vip .cuc-quang.b {{ width:300px; height:300px; left:38%; top:-40px; background:radial-gradient(circle, #FFE8AE 0%, rgba(255,232,174,0) 68%); animation-delay:-5s; }}
.san-vip .cuc-quang.c {{ width:360px; height:360px; right:-80px; top:120px; background:radial-gradient(circle, #FFD3B0 0%, rgba(255,211,176,0) 68%); animation-delay:-10s; }}
.san-vip .hat {{ position:absolute; z-index:-1; bottom:-10px; width:7px; height:13px;
    border-radius:50% 50% 50% 50% / 60% 60% 40% 40%; background:linear-gradient(180deg,#FFE08A,#D9A21E);
    opacity:0; animation:hat-len linear infinite; pointer-events:none; }}
.san-vip .hat.la {{ width:10px; height:10px; border-radius:0 70% 0 70%; background:linear-gradient(135deg,#8ED67A,#2F7A24); }}

/* đốm sáng đi theo chuột trong thẻ */
.goi .den {{ position:absolute; inset:0; pointer-events:none; opacity:0; transition:opacity .3s ease; z-index:0;
    background:radial-gradient(240px circle at var(--px,50%) var(--py,0%), var(--nen-den), transparent 65%); }}
.goi-vo:hover .goi .den {{ opacity:1; }}
.goi-vo.t-mien-phi {{ --nen-den:rgba(92,194,74,.16); }} .goi-vo.t-mua-vang {{ --nen-den:rgba(255,196,60,.24); }}
.goi-vo.t-boi-thu {{ --nen-den:rgba(52,211,153,.2); }} .goi-vo.t-dai-dien {{ --nen-den:rgba(255,170,70,.24); }}
.goi .icon-goi, .goi .hang, .goi .ten, .goi .ky, .goi .gia, .goi .thang, .goi .vach, .goi ul {{ position:relative; z-index:1; }}

/* icon: tự vẽ nét khi mở trang, xoay nhẹ + vòng sáng khi rê chuột */
.icon-goi svg * {{ stroke-dasharray:100; stroke-dashoffset:100; animation:ve-net 1.5s cubic-bezier(.6,0,.2,1) .45s forwards; }}
.goi-vo:nth-child(2) .icon-goi svg * {{ animation-delay:.6s; }} .goi-vo:nth-child(3) .icon-goi svg * {{ animation-delay:.75s; }}
.goi-vo:nth-child(4) .icon-goi svg * {{ animation-delay:.9s; }}
.goi .icon-goi svg {{ transition:transform .45s cubic-bezier(.3,1.6,.5,1); }}
.goi-vo:hover .goi .icon-goi svg {{ transform:scale(1.16) rotate(-9deg); }}
.goi .icon-goi:after {{ content:""; position:absolute; inset:-5px; border-radius:24px; border:2px solid var(--m1); opacity:0; }}
.goi-vo:hover .goi .icon-goi:after {{ animation:vong-lan .9s ease-out; }}

/* danh sách quyền lợi hiện lần lượt; rê chuột thì dấu tích nhún */
.goi li {{ animation:noi-li .5s ease backwards; }}
.goi li:nth-child(1) {{ animation-delay:.55s; }} .goi li:nth-child(2) {{ animation-delay:.65s; }}
.goi li:nth-child(3) {{ animation-delay:.75s; }} .goi li:nth-child(4) {{ animation-delay:.85s; }}
.goi li:nth-child(5) {{ animation-delay:.95s; }} .goi li:nth-child(6) {{ animation-delay:1.05s; }}
.goi-vo:hover .goi li .dau {{ animation:nhun .6s ease; }}
.goi-vo:hover .goi li:nth-child(2) .dau {{ animation-delay:.06s; }}
.goi-vo:hover .goi li:nth-child(3) .dau {{ animation-delay:.12s; }}
.goi-vo:hover .goi li:nth-child(4) .dau {{ animation-delay:.18s; }}

/* Mùa Vàng: bụi vàng bay lên từ icon */
.t-mua-vang .bui {{ position:absolute; z-index:2; left:58px; top:78px; width:5px; height:5px; border-radius:50%;
    background:#FFC53D; box-shadow:0 0 6px #FFD25C; animation:bui-vang 3.2s ease-out infinite; pointer-events:none; }}
.t-mua-vang .bui.b2 {{ --dx:30px; animation-delay:.6s; left:72px; }}
.t-mua-vang .bui.b3 {{ --dx:-14px; animation-delay:1.3s; left:46px; width:4px; height:4px; }}
.t-mua-vang .bui.b4 {{ --dx:46px; animation-delay:2s; left:82px; width:3px; height:3px; }}
.t-mua-vang .bui.b5 {{ --dx:8px; animation-delay:2.6s; }}

/* nút Đại Điền: toả sáng theo nhịp */
.st-key-mua_dai_dien {{ animation:nhip-nut 2.4s ease-in-out infinite; }}

/* dải Nhóm: màu chảy + chồng hình đại diện */
.goi-nhom {{ background-image:linear-gradient(110deg,#1F4A16 0%,#2F6B22 25%,#0F766E 50%,#2F6B22 75%,#1F4A16 100%);
    background-size:200% 100%; animation:noi-vip .7s .32s cubic-bezier(.2,.8,.2,1) backwards, dong-chay 10s linear infinite; }}
.chong-avatar {{ display:flex; margin-top:10px; }}
.chong-avatar span {{ width:30px; height:30px; border-radius:50%; margin-left:-8px; display:flex; align-items:center;
    justify-content:center; font-size:.72rem; font-weight:800; color:#fff; border:2px solid rgba(255,255,255,.9);
    animation:nhun 2.4s ease-in-out infinite; box-shadow:0 4px 10px rgba(0,0,0,.18); }}
.chong-avatar span:first-child {{ margin-left:0; }}
.chong-avatar span:nth-child(2) {{ animation-delay:.2s; }} .chong-avatar span:nth-child(3) {{ animation-delay:.4s; }}
.chong-avatar span:nth-child(4) {{ animation-delay:.6s; }} .chong-avatar span:nth-child(5) {{ animation-delay:.8s; }}

/* máy yếu / người dùng tắt chuyển động: bỏ hiệu ứng */
@media (prefers-reduced-motion: reduce) {{
  .san-vip *, .goi-vo, .goi-nhom, .goi-nhom *, .st-key-mua_dai_dien, [class*="st-key-mua_"] button {{ animation:none !important; }}
  .icon-goi svg * {{ stroke-dashoffset:0; }} }}

/* nút mua dưới mỗi thẻ */
.st-key-goi_mien_phi button, .st-key-mua_mua_vang button, .st-key-mua_boi_thu button,
.st-key-mua_dai_dien button, .st-key-mua_nhom button {{ height:50px !important; border-radius:16px !important;
    border:none !important; font-weight:800 !important; transition:transform .2s ease, box-shadow .2s ease, filter .2s !important; }}
.st-key-goi_mien_phi button p, .st-key-mua_mua_vang button p, .st-key-mua_boi_thu button p,
.st-key-mua_dai_dien button p, .st-key-mua_nhom button p {{ font-weight:800 !important; font-size:.98rem !important; }}
.st-key-mua_mua_vang button, .st-key-mua_boi_thu button, .st-key-mua_dai_dien button, .st-key-mua_nhom button {{
    color:#fff !important; }}
.st-key-mua_mua_vang button p, .st-key-mua_boi_thu button p, .st-key-mua_dai_dien button p,
.st-key-mua_nhom button p {{ color:#fff !important; }}
.st-key-mua_mua_vang button {{ background-image:linear-gradient(110deg,#D48A06 0%,#FFD25C 30%,#FFEDB5 45%,#FFD25C 60%,#D48A06 100%) !important;
    background-size:250% 100% !important; animation:nut-chay 4s linear infinite;
    box-shadow:0 10px 22px -10px rgba(212,138,6,.7) !important; }}
.st-key-mua_boi_thu button {{ background-image:linear-gradient(110deg,#047857 0%,#34D399 30%,#9AF3CF 45%,#34D399 60%,#047857 100%) !important;
    background-size:250% 100% !important; animation:nut-chay 4s linear infinite;
    box-shadow:0 10px 22px -10px rgba(4,120,87,.7) !important; }}
.st-key-mua_dai_dien button {{ background-image:linear-gradient(110deg,#C8541E 0%,#FFB648 30%,#FFE3A8 45%,#FFB648 60%,#C8541E 100%) !important;
    background-size:250% 100% !important; animation:nut-chay 4s linear infinite;
    box-shadow:0 12px 26px -10px rgba(232,116,59,.85) !important; }}
.st-key-mua_nhom button {{ background-image:linear-gradient(110deg,#0F766E 0%,#2F6B22 30%,#6FC7A0 45%,#2F6B22 60%,#0F766E 100%) !important;
    background-size:250% 100% !important; animation:nut-chay 4s linear infinite;
    box-shadow:0 10px 22px -10px rgba(15,118,110,.7) !important; }}
.st-key-mua_mua_vang button:hover, .st-key-mua_boi_thu button:hover, .st-key-mua_dai_dien button:hover,
.st-key-mua_nhom button:hover {{ transform:translateY(-3px); filter:brightness(1.07); }}
.st-key-goi_mien_phi button {{ background:#EEF8EA !important; }}
.st-key-goi_mien_phi button p {{ color:#2F7A24 !important; }}

/* --- bảng quyền lợi / độ tin cậy --- */
.bang-ql {{ border:1px solid {VIEN}; border-radius:16px; overflow:hidden; background:#fff; }}
.bang-ql table {{ width:100% !important; border-collapse:collapse !important; margin:0 !important; font-size:.95rem; }}
.bang-ql th, .bang-ql td {{ border:none !important; padding:12px 16px; text-align:left; }}
.bang-ql th {{ background:#2F2620; color:#fff; font-size:.8rem; letter-spacing:.05em; text-transform:uppercase; }}
.bang-ql th.vip {{ background:linear-gradient(135deg,#D9971E,#A8650E); }}
.bang-ql tr:nth-child(even) td {{ background:#FCFAF8; }}
.bang-ql td.vip {{ font-weight:700; color:#7A4B00; background:#FFFBEF !important; }}
.bang-ql td.khong {{ color:#B8ADA4; }}

/* --- bảng quyền lợi 4 gói --- */
.bang-ql th.g {{ text-align:center; }} .bang-ql td.co, .bang-ql td.khong {{ text-align:center; }}
.bang-ql td.co {{ color:#2F7A24; font-weight:900; font-size:1.15rem; }}
.bang-ql td:not(:first-child) {{ text-align:center; }}

/* --- 4 ô dự báo: gọn hơn cho vừa --- */
.hang-o:not(.ba) .o.du-bao {{ padding:20px 18px 18px; }}
.hang-o:not(.ba) .o.du-bao .so-lon {{ font-size:1.95rem; }}
.hang-o:not(.ba) .o.du-bao .doi {{ font-size:.92rem; }}
.hang-o:not(.ba) .o.du-bao .dong {{ font-size:.8rem; flex-direction:column; gap:2px; }}
.hang-o:not(.ba) .o.du-bao .dong span:last-child, .hang-o:not(.ba) .o.du-bao .dong b {{ font-size:.9rem; }}
.hang-o:not(.ba) .khoa-phu {{ font-size:.82rem; }}

/* --- AI phân tích giá --- */
.khung-ai {{ position:relative; overflow:hidden; border-radius:18px; padding:18px 22px; margin:1rem 0 .4rem;
    background:linear-gradient(135deg,#F3F8FF 0%,#FFFFFF 60%); border:1px solid #DCE8FB;
    box-shadow:0 8px 24px -14px rgba(37,99,235,.35); }}
.khung-ai:before {{ content:""; position:absolute; inset:0 auto 0 0; width:4px;
    background:linear-gradient(180deg,#2563EB,#7C3AED,#E8743B); }}
.ai-dau {{ display:flex; gap:12px; align-items:center; margin-bottom:8px; color:{CHU}; }}
.ai-bt {{ width:38px; height:38px; border-radius:12px; display:flex; align-items:center; justify-content:center;
    font-weight:900; font-size:.85rem; color:#fff; background:linear-gradient(135deg,#2563EB,#7C3AED);
    box-shadow:0 6px 14px -4px rgba(124,58,237,.5); }}
.ai-phu {{ color:{CHU_PHU}; font-size:.85rem; }}
.pt-dong {{ display:grid; grid-template-columns:170px 1fr; gap:12px; padding:8px 0; border-top:1px dashed #DCE8FB; font-size:.95rem; }}
.pt-td {{ font-weight:700; color:#1E3A8A; }} .pt-nd {{ color:#3F3833; line-height:1.55; }}
@media (max-width: 640px) {{ .pt-dong {{ grid-template-columns:1fr; gap:2px; }} }}

.ai-dau.chat {{ margin:2px 0 6px; }}
.ai-nhan {{ margin-left:10px; font-size:.75rem; font-weight:700; padding:3px 9px; border-radius:999px;
    background:#F3EEE9; color:{CHU_PHU}; }}
.ai-nhan.co {{ background:#E7F6EC; color:#15803D; }}
.st-key-khung_chat_ai {{ background:linear-gradient(180deg,#FBFCFF 0%,#FFFFFF 40%) !important; border-color:#DCE8FB !important; }}
.st-key-khung_chat_ai [data-testid="stChatMessage"] {{ border-radius:14px; }}
.st-key-khung_chat_ai button p {{ font-size:.86rem !important; }}

/* --- nút tròn Trợ lý Bồ Nông (góc dưới bên phải) --- */
@keyframes song-lan {{ 0% {{ transform:scale(1); opacity:.55; }} 100% {{ transform:scale(1.75); opacity:0; }} }}
@keyframes noi-bong {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-6px); }} }}
@keyframes chao-ban {{ 0%,8% {{ opacity:0; transform:translateX(8px); }} 14%,86% {{ opacity:1; transform:none; }}
    100% {{ opacity:0; transform:translateX(8px); }} }}
a.nut-bo-nong {{ position:fixed; right:28px; bottom:28px; z-index:999990; width:72px; height:72px; border-radius:50%;
    display:flex; align-items:center; justify-content:center; background:#fff; text-decoration:none !important;
    border:3px solid #fff; box-shadow:0 14px 30px -8px rgba(232,116,59,.6), 0 0 0 2px #F2B33D;
    animation:noi-bong 3.2s ease-in-out infinite; transition:box-shadow .25s ease; }}
a.nut-bo-nong img {{ width:100%; height:100%; border-radius:50%; object-fit:cover; position:relative; z-index:1;
    transition:transform .35s cubic-bezier(.3,1.6,.5,1); }}
a.nut-bo-nong:hover img {{ transform:scale(1.1) rotate(-8deg); }}
a.nut-bo-nong:hover {{ box-shadow:0 18px 36px -8px rgba(232,116,59,.75), 0 0 0 3px #E8743B; }}
a.nut-bo-nong .song {{ position:absolute; inset:-3px; border-radius:50%; border:2px solid #E8743B;
    animation:song-lan 2.4s ease-out infinite; pointer-events:none; }}
a.nut-bo-nong .song.b {{ animation-delay:1.2s; border-color:#F2B33D; }}
.cham-xanh {{ position:absolute; z-index:2; right:2px; bottom:4px; width:15px; height:15px; border-radius:50%;
    background:#22C55E; border:3px solid #fff; }}
a.nut-bo-nong .bong-chu {{ position:absolute; right:86px; white-space:nowrap; background:#1F1A17; color:#fff;
    font-size:.86rem; font-weight:700; padding:9px 14px; border-radius:14px 14px 4px 14px;
    box-shadow:0 8px 20px rgba(0,0,0,.2); pointer-events:none; opacity:0; animation:chao-ban 6s ease 1.2s 1 both; }}
a.nut-bo-nong:hover .bong-chu {{ animation:none; opacity:1; transform:none; }}
@media (max-width: 640px) {{ a.nut-bo-nong {{ width:60px; height:60px; right:16px; bottom:16px; }}
    a.nut-bo-nong .bong-chu {{ display:none; }} }}

/* --- ô tài khoản có ảnh + Trang cá nhân --- */
.thanh-tai-khoan .avatar.co-anh {{ background:#fff; overflow:hidden; padding:0; }}
.thanh-tai-khoan .avatar.co-anh img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.thanh-tai-khoan a.chip-tk.dang-chon {{ border-color:var(--dam); box-shadow:0 0 0 3px rgba(47,107,34,.15); }}
@keyframes vong-anh {{ to {{ transform:rotate(360deg); }} }}
.the-ho-so {{ position:relative; overflow:hidden; display:flex; gap:24px; align-items:center; flex-wrap:wrap;
    padding:26px 28px; margin:.6rem 0 1.2rem; border-radius:24px; color:#fff;
    background:radial-gradient(120% 140% at 100% 0%, #46A033 0%, #2F6B22 45%, #1F4A16 100%);
    box-shadow:0 18px 40px -20px rgba(31,74,22,.8); animation:noi-vip .6s cubic-bezier(.2,.8,.2,1) backwards; }}
.the-ho-so:after {{ content:""; position:absolute; right:-70px; top:-70px; width:240px; height:240px; border-radius:50%;
    background:radial-gradient(circle, rgba(242,179,61,.35) 0%, transparent 70%); }}
.hs-anh {{ position:relative; flex:none; width:112px; height:112px; border-radius:50%; padding:4px;
    background:conic-gradient(#F2B33D, #E8743B, #FFE29A, #F2B33D); }}
.hs-anh:before {{ content:""; position:absolute; inset:-6px; border-radius:50%; border:2px dashed rgba(255,255,255,.35);
    animation:vong-anh 18s linear infinite; }}
.hs-anh img, .hs-anh span {{ width:100%; height:100%; border-radius:50%; object-fit:cover; display:flex;
    align-items:center; justify-content:center; border:3px solid #fff; box-sizing:border-box; }}
.hs-anh span {{ background:linear-gradient(135deg,#5CB446,#1F4A16); font-size:2.8rem; font-weight:800; }}
.hs-giua {{ position:relative; z-index:1; flex:1; min-width:220px; }}
.hs-ten {{ font-family:'Noto Serif', Georgia, serif; font-size:2rem; font-weight:700; line-height:1.2; }}
.hs-email {{ opacity:.85; margin-top:2px; }}
.hs-nhan {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:12px; }}
.hs-nhan span {{ display:inline-flex; align-items:center; gap:6px; padding:5px 12px; border-radius:999px;
    font-size:.85rem; font-weight:600; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.22); }}
.hs-nhan .hs-goi.vip {{ background:linear-gradient(135deg,#F4C24D,#C9851A); border:none; color:#fff; }}
.hs-nhan .hs-goi svg {{ width:16px; height:16px; }}
.st-key-khung_anh, .st-key-khung_thong_tin, .st-key-khung_bao_mat {{ border-radius:20px !important; }}

/* --- trang Trợ lý --- */
.duoi-o-hoi {{ text-align:center; color:{CHU_PHU}; font-size:.78rem; line-height:1.5; margin:-4px auto 2px;
    max-width:860px; }}
.duoi-o-hoi .chan {{ margin-top:2px; opacity:.85; }}
.dau-tro-ly {{ margin:.4rem 0 1rem; }}
.dau-tro-ly .quay-lai {{ display:inline-block; color:{CHU_PHU} !important; text-decoration:none !important; font-weight:600;
    font-size:.9rem; margin-bottom:.8rem; }}
.dau-tro-ly .quay-lai:hover {{ color:{CAM} !important; }}
.tl-hang {{ display:flex; gap:18px; align-items:center; padding:20px 22px; border-radius:22px;
    background:linear-gradient(135deg,#FFF6EF 0%,#FFFFFF 55%,#F3F8FF 100%); border:1px solid {VIEN};
    box-shadow:0 10px 28px -16px rgba(232,116,59,.45); }}
.tl-avatar {{ position:relative; flex:none; width:76px; height:76px; border-radius:50%; background:#fff;
    box-shadow:0 0 0 3px #fff, 0 0 0 5px #F2B33D, 0 10px 22px -8px rgba(232,116,59,.6); }}
.tl-avatar img {{ width:100%; height:100%; border-radius:50%; object-fit:cover; }}
.tl-hang h1 {{ font-family:'Noto Serif', Georgia, serif !important; font-size:1.9rem !important; font-weight:700 !important;
    color:{CHU} !important; margin:0 !important; padding:0 !important; display:inline; }}
.tl-hang .ai-nhan {{ vertical-align:6px; }}
.tl-hang .phu {{ color:{CHU_PHU}; font-size:.95rem; margin-top:4px; }}
[data-testid="stChatMessage"] {{ border-radius:16px; }}

/* --- thông báo biến động --- */
.khung-bd {{ border-radius:18px; padding:14px 18px; margin:.6rem 0 .2rem; background:#fff; border:1px solid {VIEN};
    box-shadow:0 4px 14px rgba(60,20,20,.05); }}
.bd-dau {{ display:flex; justify-content:space-between; gap:10px; align-items:center; color:{CHU}; margin-bottom:6px; }}
.bd-dau span {{ color:{CHU_PHU}; font-size:.85rem; }}
.bd-dong {{ display:grid; grid-template-columns:26px 1fr auto; gap:10px; align-items:center; padding:7px 0;
    border-top:1px dashed {VIEN}; font-size:.93rem; }}
.bd-mui {{ width:24px; height:24px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:.7rem; }}
.bd-mui.len {{ background:#E7F6EC; color:{TANG}; }} .bd-mui.xuong {{ background:#FDECEC; color:{GIAM}; }}
.bd-gia {{ white-space:nowrap; }} .bd-gia .len {{ color:{TANG}; font-weight:700; }} .bd-gia .xuong {{ color:{GIAM}; font-weight:700; }}
.bd-trong {{ color:{CHU_PHU}; font-size:.92rem; padding:6px 0; }}

/* --- thanh toán --- */
.qr-khung {{ display:flex; gap:20px; align-items:center; flex-wrap:wrap; }}
.qr-khung svg.qr {{ width:170px; height:170px; border-radius:12px; border:1px solid {VIEN}; background:#fff; padding:8px; }}
.tt-dong {{ display:flex; justify-content:space-between; gap:12px; border-bottom:1px dashed {VIEN}; padding:7px 0;
    font-size:.95rem; }}
.tt-dong span:first-child {{ color:{CHU_PHU}; }}
.che-do-thu {{ background:#FFF4DA; border:1px solid #F3DDA2; color:#6B4A00; border-radius:12px; padding:10px 14px;
    font-size:.9rem; line-height:1.5; margin:.6rem 0; }}
</style>""")


def dau_trang_con(tieu_de: str, phu: str, bieu_tuong: str = "xu") -> str:
    bt = '<span class="dong-xu">xu</span>' if bieu_tuong == "xu" else SVG_VUONG_MIEN
    return gon(f'<div class="dau-trang-con"><div class="bt">{bt}</div><div><h1>{e(tieu_de)}</h1>'
               f'<div class="phu">{phu}</div></div></div>')


def khung_khoa(tieu_de: str, mo_ta: str) -> str:
    return gon(f'<div class="khung-khoa"><div class="o-khoa-icon">{SVG_KHOA}</div>'
               f'<div><div class="td">{tieu_de}</div><div class="md">{mo_ta}</div></div></div>')


def da_mo_khoa(chu: str) -> str:
    return gon(f'<div class="da-mo">🔓 {chu}</div>')


def nut_link(chu: str, link: str, nhat: bool = False) -> str:
    return gon(f'<a class="nut-link {"nhat" if nhat else ""}" href="{e(link)}" target="_self">'
               f'{SVG_VUONG_MIEN}{e(chu)}</a>')


def the_vi(so_du: int, sap_het: int, ngay_het, vip: dict, dong_moi_xu: int) -> str:
    canh_bao = (f'<div class="canh-bao">⏳ {so(sap_het)} xu hết hạn ngày {ngay_het:%d/%m} — dùng sớm nhé</div>'
                if sap_het else "")
    trang_thai = (f"Bạn đang là <b>{e(vip['ten'])}</b> đến {vip['ket_thuc']:%d/%m/%Y} — xem mọi thứ không giới hạn."
                  if vip else "Gói Miễn phí · dùng xu để mở khoá dự báo 7 và 30 ngày.")
    return gon(f'<div class="the-vi"><div class="nhan">Số dư ví xu</div>'
               f'<div class="so"><span class="dong-xu">xu</span>{so(so_du)} <small>xu</small></div>'
               f'<div class="phu">≈ {so(so_du * dong_moi_xu)} đ giá trị sử dụng · {trang_thai}</div>{canh_bao}</div>')


def chuoi_diem_danh(so_ngay: int, hom_nay_co: bool) -> str:
    """7 ô: các ngày đã điểm danh trong chuỗi 7 ngày hiện tại; ô thứ 7 có thưởng."""
    vi_tri = so_ngay % 7 if not (so_ngay and so_ngay % 7 == 0 and hom_nay_co) else 7
    o = "".join(f'<span class="{"co" if i < vi_tri else ""} {"thuong" if i == 6 else ""}">'
                f'{"+10" if i == 6 else "+2"}</span>' for i in range(7))
    return gon(f'<div class="chuoi-ngay">{o}</div>')


def o_nho(tieu_de: str, mo_ta: str) -> str:
    return gon(f'<div class="o-nho"><div class="td">{tieu_de}</div><div class="md">{mo_ta}</div></div>')


def _svg(*phan: str) -> str:
    phan = [x.replace("<path ", '<path pathLength="100" ').replace("<circle ", '<circle pathLength="100" ')
            for x in phan]
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round">' + "".join(phan) + "</svg>")


ICON_GOI = {
    "mien_phi": _svg('<path d="M7 20h10"/>', '<path d="M10 20c5.5-2.5.8-6.4 3-10"/>',
                     '<path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/>',
                     '<path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>'),
    "mua_vang": _svg('<path d="M2 22 16 8"/>',
                     '<path d="M3.47 12.53 5 11l1.53 1.53a3.5 3.5 0 0 1 0 4.94L5 19l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z"/>',
                     '<path d="M7.47 8.53 9 7l1.53 1.53a3.5 3.5 0 0 1 0 4.94L9 15l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z"/>',
                     '<path d="M11.47 4.53 13 3l1.53 1.53a3.5 3.5 0 0 1 0 4.94L13 11l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z"/>',
                     '<path d="M20 2h2v2a4 4 0 0 1-4 4h-2V6a4 4 0 0 1 4-4Z"/>',
                     '<path d="M11.47 17.47 13 19l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L5 19l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z"/>',
                     '<path d="M15.47 13.47 17 15l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L9 15l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z"/>',
                     '<path d="M19.47 9.47 21 11l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L13 11l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z"/>'),
    "boi_thu": _svg('<path d="M4 21v-3"/>', '<path d="M9 21v-6"/>', '<path d="M14 21v-5"/>', '<path d="M19 21v-9"/>',
                    '<path d="M3 13l5.5-5 4 3.5L20 4"/>', '<path d="M15 4h5v5"/>'),
    "dai_dien": _svg('<path d="M11.56 3.27a.5.5 0 0 1 .88 0l2.95 5.6a1 1 0 0 0 1.52.3l4.27-3.67a.5.5 0 0 1 .8.52'
                     'l-2.83 10.25a1 1 0 0 1-.96.73H5.81a1 1 0 0 1-.96-.73L2.02 6.02a.5.5 0 0 1 .8-.52l4.27 3.67'
                     'a1 1 0 0 0 1.52-.3z"/>', '<path d="M5 21h14"/>'),
    "nhom": _svg('<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>', '<circle cx="9" cy="7" r="4"/>',
                 '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>', '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
}
SAO_4_CANH = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c.6 6.4 5.6 11.4 12 12-6.4.6-11.4 5.6-12 12'
              '-.6-6.4-5.6-11.4-12-12C6.4 11.4 11.4 6.4 12 0z"/></svg>')
HANG_GOI = {"mien_phi": "Khởi đầu", "mua_vang": "Gieo hạt", "boi_thu": "Phổ biến", "dai_dien": "Tốt nhất"}
NHAN_GOI = {"boi_thu": "Tiết kiệm 12%", "dai_dien": "Tiết kiệm 24%"}
SO_THANG = {30: 1, 90: 3, 365: 12}
HAT_BAY = [(4, 11, 0, 0), (12, 14, 3, 1), (21, 10, 6, 0), (29, 13, 1.5, 1), (37, 12, 8, 0), (45, 15, 4.5, 1), (53, 11, 2, 0), (61, 13, 7, 1), (68, 12, 0.8, 0), (76, 14, 5.5, 1), (84, 10, 3.5, 0), (92, 13, 9, 1), (97, 12, 6.5, 0), (8, 15, 10, 0), (58, 16, 11, 1), (88, 15, 12, 0)]


def _the_goi(ma: str, ten: str, ky: str, gia: int, thang_txt: str, loi: list, khong: list, dang_dung: bool,
             co_vien: bool = True) -> str:
    lop = {"mien_phi": "t-mien-phi", "mua_vang": "t-mua-vang", "boi_thu": "t-boi-thu", "dai_dien": "t-dai-dien"}[ma]
    nhan = ('<div class="dang-dung">Đang dùng</div>' if dang_dung
            else (f'<div class="ruy-bang">{NHAN_GOI[ma]}</div>' if ma in NHAN_GOI else ""))
    tia = ("".join(f'<span class="tia {c}">{SAO_4_CANH}</span>' for c in "abcd") if ma == "dai_dien" else "")
    ds = ("".join(f'<li><span class="dau">✓</span><span>{e(x)}</span></li>' for x in loi)
          + "".join(f'<li class="khong"><span class="dau">✕</span><span>{e(x)}</span></li>' for x in khong))
    bui = "".join(f'<span class="bui b{i}"></span>' for i in range(1, 6)) if ma == "mua_vang" else ""
    return (f'<div class="goi-vo {lop} {"mau" if co_vien else ""}"><div class="goi"><div class="den"></div>{nhan}{tia}{bui}'
            f'<div class="icon-goi">{ICON_GOI[ma]}</div>'
            f'<div class="hang">{HANG_GOI[ma]}</div><div class="ten">{e(ten)}</div><div class="ky">{e(ky)}</div>'
            f'<div class="gia" data-gia="{gia}"><span class="so">{so(gia)}</span><small>đ</small></div>'
            f'<div class="thang">{thang_txt}</div>'
            f'<div class="vach"></div><ul>{ds}</ul></div></div>')


# quyền lợi từng gói (đúng theo bảng quyền lợi đã chốt)
QUYEN_LOI_GOI = {
    "mien_phi": (["Giá hiện tại 3 loại cây", "Dự báo giá ngày mai", "Biểu đồ giá 90 ngày",
                  "Nhận xu khi điểm danh mỗi ngày", "1 ô đất Nông trại"],
                 ["Dự báo 7 ngày", "Dự báo 30 ngày", "Thông báo biến động", "AI phân tích giá"]),
    "mua_vang": (["Dự báo 7 ngày", "Thông báo biến động giá", "Lịch sử & giá thế giới đầy đủ", "2 ô đất Nông trại"],
                 ["Dự báo 30 ngày", "AI phân tích giá", "Cảnh báo giá tuỳ chọn", "Xuất báo cáo"]),
    "boi_thu": (["Dự báo 7 & 30 ngày", "Thông báo biến động giá", "AI phân tích giá",
                 "Cảnh báo giá tuỳ chọn", "Lịch sử & giá thế giới đầy đủ", "3 ô đất Nông trại"],
                ["Xuất báo cáo"]),
    "dai_dien": (["Dự báo 7 & 30 ngày", "Thông báo biến động giá", "AI phân tích giá",
                  "Cảnh báo giá tuỳ chọn", "Xuất báo cáo (PDF & Excel)", "Lịch sử & giá thế giới đầy đủ",
                  "3 ô đất Nông trại"],
                 []),
}


def cac_the_goi_vip(goi_vip: dict, dang_dung: str = None) -> str:
    """4 thẻ: Miễn phí · Mùa Vàng · Bội Thu · Đại Điền. dang_dung: mã gói đang dùng (None = Miễn phí)."""
    co, khong = QUYEN_LOI_GOI["mien_phi"]
    o = [_the_goi("mien_phi", "Miễn phí", "Dùng mãi mãi", 0, "Không cần thanh toán", co, khong,
                  dang_dung is None, co_vien=False)]
    for ma in ["mua_vang", "boi_thu", "dai_dien"]:
        g = goi_vip[ma]
        thang = g["gia"] / SO_THANG.get(g["so_ngay"], g["so_ngay"] / 30)
        thang_txt = "Trả theo từng tháng" if g["so_ngay"] <= 31 else f"Chỉ <b>≈ {so(round(thang, -2))} đ</b> / tháng"
        co, khong = QUYEN_LOI_GOI[ma]
        o.append(_the_goi(ma, g["ten"], g["ky"], g["gia"], thang_txt, [f"Tặng {g['xu_thang']} xu mỗi tháng"] + co,
                          khong, dang_dung == ma))
    hat = "".join(f'<span class="hat{" la" if la else ""}" style="left:{x}%;animation-duration:{t}s;'
                  f'animation-delay:{d}s"></span>' for x, t, d, la in HAT_BAY)
    return gon('<div class="san-vip"><div class="cuc-quang a"></div><div class="cuc-quang b"></div>'
               '<div class="cuc-quang c"></div>' + hat + '<div class="cac-goi">' + "".join(o) + "</div></div>")


def dai_goi_nhom(g: dict, dang_dung: bool = False) -> str:
    """Dải ngang giới thiệu gói VIP Nhóm."""
    nguoi = g["gia"] / SO_THANG.get(g["so_ngay"], 12) / g["so_tk"]
    # so với 5 người cùng mua VIP Mùa Vàng (49.000 đ/tháng) suốt 12 tháng
    tiet_kiem = round((1 - nguoi / 49_000) * 100)
    return gon(f'<div class="goi-nhom"><div class="icon-goi">{ICON_GOI["nhom"]}</div>'
               f'<div class="giua"><div class="ten">{e(g["ten"])}{" · đang dùng" if dang_dung else ""}</div>'
               f'<div class="md">{g["so_tk"]} tài khoản, mỗi người đủ quyền lợi như <b>Đại Điền</b> trong {e(g["ky"].split(" ·")[0])} · '
               f'mỗi người được tặng {g["xu_thang"]} xu/tháng · hợp với hợp tác xã, đại lý, nhóm thu mua.</div>'
               '<div class="chong-avatar">' + "".join(f'<span style="background:{m}">{c}</span>' for c, m in
               [("A", "#E8743B"), ("B", "#D48A06"), ("C", "#047857"), ("D", "#2563EB"), ("E", "#7C3AED")])
               + '</div></div>'
               f'<div class="phai"><div class="gia">{so(g["gia"])}<small> đ</small></div>'
               f'<div class="thang">≈ {so(round(nguoi, -2))} đ / người / tháng</div>'
               f'<div class="ruy-bang">Tiết kiệm {tiet_kiem}%</div></div></div>')


def bang_quyen_loi() -> str:
    """Bảng so sánh quyền lợi 4 gói (giống bảng đã chốt)."""
    C, K = "✓", "—"
    dong = [("Giá hiện tại 3 loại cây", C, C, C, C), ("Dự báo ngày mai", C, C, C, C),
            ("Dự báo 7 ngày", K, C, C, C), ("Dự báo 30 ngày", K, K, C, C),
            ("Thông báo biến động", K, C, C, C), ("AI phân tích giá", K, K, C, C),
            ("Cảnh báo giá tuỳ chọn", K, K, C, C), ("Xuất báo cáo", K, K, K, C),
            ("Lịch sử giá & giá thế giới đầy đủ", K, C, C, C), ("Xu tặng mỗi tháng", K, "100", "150", "200"),
            ("Ô đất Nông trại", "1 ô", "2 ô", "3 ô", "3 ô")]
    o = lambda x, vip: f'<td class="{"khong" if x == K else ("co" if x == C else "")} {"vip" if vip else ""}">{e(x)}</td>'
    than = "".join(f'<tr><td>{e(r[0])}</td>{o(r[1], 0)}{o(r[2], 0)}{o(r[3], 0)}{o(r[4], 1)}</tr>' for r in dong)
    return gon('<div class="bang-ql"><table><thead><tr><th>Tính năng</th><th class="g">Miễn phí</th>'
               '<th class="g">Mùa Vàng</th><th class="g">Bội Thu</th><th class="g vip">Đại Điền</th></tr></thead>'
               f'<tbody>{than}</tbody></table></div>'
               '<div class="chu-thich" style="margin-top:8px">Gói thấp hơn vẫn mở thêm được bằng xu: dự báo 7 ngày '
               '<b>30 xu</b>, cả dự báo 30 ngày <b>50 xu</b> (mỗi lần dùng 7 ngày cho 1 giống hoặc 1 tỉnh). '
               'VIP Nhóm có quyền lợi như Đại Điền.</div>')


def the_phan_tich(cac_muc: list) -> str:
    """Khung 'AI phân tích giá'."""
    ds = "".join(f'<div class="pt-dong"><div class="pt-td">{e(t)}</div><div class="pt-nd">{e(c)}</div></div>'
                 for t, c in cac_muc)
    return gon(f'<div class="khung-ai"><div class="ai-dau"><span class="ai-bt">AI</span>'
               f'<div><b>AI phân tích giá</b><div class="ai-phu">Nhận định tự động từ diễn biến giá, 3 mô hình dự báo '
               f'và giá thế giới</div></div></div>{ds}</div>')


def dau_tro_ly(co_gemini: bool) -> str:
    """Đầu khung chat Trợ lý AI."""
    nhan = ('<span class="ai-nhan co">● AI đang bật</span>' if co_gemini
            else '<span class="ai-nhan">● Chế độ tự động</span>')
    return gon(f'<div class="ai-dau chat"><span class="ai-bt">AI</span><div><b>Hỏi Trợ lý Bồ Nông</b>{nhan}'
               '</div></div>')


def nut_tro_ly(link: str, icon_b64: str) -> str:
    """Nút tròn hình con bồ nông ở góc dưới bên phải: bấm vào mở trang Trợ lý AI."""
    hinh = (f'<img src="data:image/png;base64,{icon_b64}" alt="Trợ lý Bồ Nông">' if icon_b64
            else '<span style="font-size:30px">🌾</span>')
    return gon(f'<a class="nut-bo-nong" href="{e(link)}" target="_self" title="Hỏi Trợ lý Bồ Nông">'
               f'<span class="song a"></span><span class="song b"></span>{hinh}<span class="cham-xanh"></span>'
               f'<span class="bong-chu">Hỏi Trợ lý Bồ Nông 💬</span></a>')


def dau_trang_tro_ly(icon_b64: str, co_gemini: bool, link_quay_lai: str) -> str:
    """Đầu trang chatbot: hình con bồ nông + tên trợ lý + trạng thái AI."""
    hinh = f'<img src="data:image/png;base64,{icon_b64}" alt="">' if icon_b64 else "🌾"
    nhan = ('<span class="ai-nhan co">● AI đang bật</span>' if co_gemini
            else '<span class="ai-nhan">● Chế độ tự động</span>')
    return gon(f'<div class="dau-tro-ly"><a class="quay-lai" href="{e(link_quay_lai)}" target="_self">← Quay lại trang giá</a>'
               f'<div class="tl-hang"><div class="tl-avatar">{hinh}<span class="cham-xanh"></span></div>'
               f'<div><h1>Trợ lý Bồ Nông</h1>{nhan}'
               f'<div class="phu">Hỏi đáp về giá lúa, cà phê, hồ tiêu</div></div></div></div>')


def chu_duoi_o_hoi(ghi_chu: str, chan: str) -> str:
    """2 dòng chữ nhỏ nằm dưới ô nhập câu hỏi của chatbot."""
    return gon(f'<div class="duoi-o-hoi"><div>{e(ghi_chu)}</div><div class="chan">{e(chan)}</div></div>')


def the_ho_so(ho_ten: str, email: str, anh_b64: str, ten_goi: str, la_vip: bool, ngay_tao: str, so_xu: int) -> str:
    """Thẻ đầu Trang Cá Nhân: ảnh lớn, tên, email, gói, ngày tham gia, số xu."""
    chu = (ho_ten.strip().split()[-1][:1] if ho_ten.strip() else "?").upper()
    anh = (f'<img src="data:image/jpeg;base64,{anh_b64}" alt="">' if anh_b64 else f'<span>{e(chu)}</span>')
    try:
        tham_gia = pd.Timestamp(ngay_tao).strftime("%d/%m/%Y")
    except Exception:
        tham_gia = "—"
    return gon(f'<div class="the-ho-so"><div class="hs-anh">{anh}</div>'
               f'<div class="hs-giua"><div class="hs-ten">{e(ho_ten)}</div><div class="hs-email">{e(email)}</div>'
               f'<div class="hs-nhan"><span class="hs-goi {"vip" if la_vip else ""}">{SVG_VUONG_MIEN if la_vip else "🌱"} '
               f'{e(ten_goi)}</span><span>📅 Tham gia {tham_gia}</span><span>🪙 {so(so_xu)} xu</span></div></div></div>')


def the_bien_dong(ds: list, ngay_txt: str) -> str:
    """Khung 'Thông báo biến động': các giống/tỉnh đổi giá đáng chú ý ở phiên mới nhất."""
    if not ds:
        than = '<div class="bd-trong">Phiên mới nhất giá các nơi khá ổn định, không có thay đổi từ 0,5% trở lên.</div>'
    else:
        than = "".join(
            f'<div class="bd-dong"><span class="bd-mui {"len" if x["pt"] > 0 else "xuong"}">{"▲" if x["pt"] > 0 else "▼"}</span>'
            f'<div class="bd-ten"><b>{e(x["nong_san"])}</b> · {e(x["loai"])} · {e(x["khu_vuc"])}</div>'
            f'<div class="bd-gia">{so(x["gia_truoc"])} → <b>{so(x["gia"])}</b> đ '
            f'<span class="{"len" if x["pt"] > 0 else "xuong"}">({phan_tram(x["pt"])})</span></div></div>' for x in ds)
    return gon(f'<div class="khung-bd"><div class="bd-dau"><div>🔔 <b>Thông báo biến động giá</b></div>'
               f'<span>{e(ngay_txt)}</span></div>{than}</div>')


def bang_do_tin_cay(cac_dong: list) -> str:
    """cac_dong: [(tên, ngày mai %, 7 ngày %, 30 ngày %)]."""
    pt = lambda x: f"± {x:.1f}%".replace(".", ",")
    than = "".join(f'<tr><td>{e(t)}</td><td>{pt(a)}</td><td>{pt(b)}</td><td>{pt(c)}</td></tr>'
                   for t, a, b, c in cac_dong)
    return gon('<div class="bang-ql"><table><thead><tr><th>Cách dự báo</th><th>Ngày mai</th><th>7 ngày</th>'
               f'<th>30 ngày</th></tr></thead><tbody>{than}</tbody></table></div>')


def qr_mau(noi_dung: str) -> str:
    """Hình QR MẪU (không quét được) — chỉ để thử giao diện. Khi nối VietQR thật sẽ thay bằng ảnh QR của ngân hàng."""
    import hashlib
    bam = hashlib.sha256(noi_dung.encode()).digest() * 4
    n, o = 25, []
    for i in range(n):
        for j in range(n):
            goc = (i < 7 and j < 7) or (i < 7 and j >= n - 7) or (i >= n - 7 and j < 7)
            if goc:
                a, b = i % (n - 7) if i >= n - 7 else i, j % (n - 7) if j >= n - 7 else j
                den = a in (0, 6) or b in (0, 6) or (2 <= a <= 4 and 2 <= b <= 4)
            else:
                den = (bam[(i * n + j) // 8] >> ((i * n + j) % 8)) & 1
            if den:
                o.append(f'<rect x="{j}" y="{i}" width="1" height="1"/>')
    return (f'<svg class="qr" viewBox="0 0 {n} {n}" shape-rendering="crispEdges" fill="#1F1A17">'
            + "".join(o) + "</svg>")


# ================================================================ Giao diện chatbot (trang Trợ lý)
def css_chat() -> str:
    """Bong bóng chat, avatar động, ô nhập câu hỏi viền màu xoay, nút gửi, gợi ý câu hỏi."""
    return gon(f"""
<style>
@property --goc-chat {{ syntax:'<angle>'; inherits:false; initial-value:0deg; }}
@keyframes xoay-chat {{ to {{ --goc-chat:360deg; }} }}
@keyframes hien-tin {{ from {{ opacity:0; transform:translateY(16px) scale(.97); }} to {{ opacity:1; transform:none; }} }}
@keyframes nhip-av {{ 0%,100% {{ box-shadow:0 0 0 0 rgba(232,116,59,.5); }} 60% {{ box-shadow:0 0 0 9px rgba(232,116,59,0); }} }}
@keyframes bay-av {{ 0%,100% {{ transform:translateY(0) rotate(0deg); }} 50% {{ transform:translateY(-4px) rotate(-4deg); }} }}
@keyframes lap-lanh {{ 0%,100% {{ opacity:.25; transform:scale(.6); }} 50% {{ opacity:1; transform:scale(1); }} }}
@keyframes anh-gui {{ 0% {{ background-position:0% 50%; }} 100% {{ background-position:200% 50%; }} }}

/* --- tin nhắn --- */
[data-testid="stChatMessage"] {{ animation:hien-tin .5s cubic-bezier(.2,.8,.2,1) both; gap:14px !important;
    padding:14px 18px !important; border-radius:22px !important; margin:6px 0 !important; }}
[data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {{ background:#fff !important;
    border:1px solid {VIEN}; border-top-left-radius:6px !important; max-width:90%;
    box-shadow:0 10px 26px -18px rgba(60,20,20,.35); }}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {{ flex-direction:row-reverse;
    margin-left:auto !important; width:fit-content; max-width:80%; border-top-right-radius:6px !important;
    background:linear-gradient(135deg,#2F7A24 0%,#46A033 100%) !important;
    box-shadow:0 12px 24px -14px rgba(47,122,36,.7); }}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) [data-testid="stChatMessageContent"] * {{
    color:#fff !important; }}
[data-testid="stChatMessageContent"] p, [data-testid="stChatMessageContent"] li {{ font-size:1rem; line-height:1.65; }}

/* --- avatar --- */
[data-testid="stChatMessage"] img[data-testid="stChatMessageAvatarImage"] {{ width:46px !important; height:46px !important;
    min-width:46px; border-radius:50% !important; object-fit:cover; }}
[data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) img[data-testid="stChatMessageAvatarImage"] {{
    animation:bay-av 3.2s ease-in-out infinite, nhip-av 2.6s ease-out infinite; }}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) img[data-testid="stChatMessageAvatarImage"] {{
    box-shadow:0 0 0 3px rgba(255,255,255,.85); }}

/* --- gợi ý câu hỏi --- */
.st-key-goi_y_ai_0 button, .st-key-goi_y_ai_1 button, .st-key-goi_y_ai_2 button {{ border-radius:999px !important;
    border:1.5px solid #F3DDA2 !important; background:linear-gradient(135deg,#FFFBEF,#FFF4DA) !important;
    min-height:46px; transition:transform .25s ease, box-shadow .25s ease, border-color .25s ease !important;
    animation:hien-tin .5s cubic-bezier(.2,.8,.2,1) .25s both; }}
.st-key-goi_y_ai_1 button {{ animation-delay:.35s !important; }} .st-key-goi_y_ai_2 button {{ animation-delay:.45s !important; }}
.st-key-goi_y_ai_0 button p, .st-key-goi_y_ai_1 button p, .st-key-goi_y_ai_2 button p {{ color:#7A4B00 !important;
    font-weight:600 !important; }}
.st-key-goi_y_ai_0 button p:before, .st-key-goi_y_ai_1 button p:before, .st-key-goi_y_ai_2 button p:before {{
    content:"✨ "; }}
.st-key-goi_y_ai_0 button:hover, .st-key-goi_y_ai_1 button:hover, .st-key-goi_y_ai_2 button:hover {{
    transform:translateY(-3px); border-color:#E8743B !important; box-shadow:0 10px 22px -12px rgba(232,116,59,.6); }}

/* --- vùng ô hỏi ghim cuối màn hình --- */
[data-testid="stBottomBlockContainer"] {{ padding-top:14px !important; padding-bottom:16px !important;
    background:linear-gradient(180deg, rgba(255,255,255,0) 0%, #fff 28%) !important; }}
[data-testid="stChatInput"] {{ position:relative; border-radius:28px !important; border:2px solid transparent !important;
    background:linear-gradient(#fff,#fff) padding-box,
               conic-gradient(from var(--goc-chat), #E8743B, #F2B33D, #46A033, #34D399, #E8743B) border-box !important;
    animation:xoay-chat 6s linear infinite; box-shadow:0 14px 32px -16px rgba(232,116,59,.6);
    transition:box-shadow .3s ease, transform .3s ease; }}
[data-testid="stChatInput"]:focus-within {{ transform:translateY(-2px);
    box-shadow:0 0 0 6px rgba(242,179,61,.16), 0 18px 38px -16px rgba(232,116,59,.75); }}
[data-testid="stChatInput"] div {{ background-color:transparent !important; border-color:transparent !important; }}
[data-testid="stChatInput"] textarea, [data-testid="stChatInputTextArea"] {{ background:transparent !important;
    font-size:1.02rem !important; color:{CHU} !important; caret-color:#E8743B; padding-left:10px !important; }}
[data-testid="stChatInput"] textarea::placeholder {{ color:#A0938A !important; }}
[data-testid="stChatInputSubmitButton"] {{ width:44px !important; height:44px !important; border-radius:50% !important;
    border:none !important; color:#fff !important;
    background:linear-gradient(110deg,#E8743B 0%,#FFB648 40%,#FFE0A3 50%,#FFB648 60%,#E8743B 100%) !important;
    background-size:200% 100% !important; animation:anh-gui 2.8s linear infinite;
    box-shadow:0 8px 18px -6px rgba(232,116,59,.75) !important; transition:transform .3s cubic-bezier(.3,1.6,.5,1) !important; }}
[data-testid="stChatInputSubmitButton"]:hover {{ transform:scale(1.12) rotate(-14deg); }}
[data-testid="stChatInputSubmitButton"] svg {{ fill:#fff !important; color:#fff !important; }}
[data-testid="stChatInputSubmitButton"]:disabled {{ background:#EFE8E2 !important; animation:none; box-shadow:none !important; }}
[data-testid="stChatInputSubmitButton"]:disabled svg {{ fill:#B8ADA4 !important; color:#B8ADA4 !important; }}
.duoi-o-hoi {{ margin-top:10px !important; }}

/* --- tia sáng trang trí cạnh tên trợ lý --- */
.tl-hang h1:after {{ content:"✦"; margin-left:8px; font-size:1.1rem; color:#F2B33D; display:inline-block;
    animation:lap-lanh 2.2s ease-in-out infinite; }}

@media (prefers-reduced-motion: reduce) {{
  [data-testid="stChatMessage"], [data-testid="stChatMessage"] img, [data-testid="stChatInput"],
  [data-testid="stChatInputSubmitButton"] {{ animation:none !important; }} }}
</style>""")


# ================================================================ Trang Cá Nhân
ICON_CA_NHAN = {
    "anh": '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>'
           '<circle cx="12" cy="13" r="3.5"/>',
    "nguoi": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
    "khoa": '<rect x="4.5" y="10.5" width="15" height="10.5" rx="2.5"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    "thu": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/>',
    "ra": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',
}


def _icon_cn(ten: str) -> str:
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICON_CA_NHAN[ten]}</svg>')


def dau_muc_ca_nhan(icon: str, tieu_de: str, phu: str) -> str:
    return gon(f'<div class="cn-dau"><span class="cn-bt {icon}">{_icon_cn(icon)}</span>'
               f'<div><div class="cn-td">{e(tieu_de)}</div><div class="cn-phu">{e(phu)}</div></div></div>')


def anh_xem_truoc(b64: str, nhan: str, ho_ten: str = "") -> str:
    """Ảnh tròn lớn có nhãn; chưa có ảnh -> chữ cái đầu của tên."""
    chu = (ho_ten.strip().split()[-1][:1] if ho_ten.strip() else "?").upper()
    ben_trong = f'<img src="data:image/*;base64,{b64}" alt="">' if b64 else f'<div class="cn-chu-cai">{e(chu)}</div>'
    return gon(f'<div class="cn-xem-truoc">{ben_trong}<span>{e(nhan)}</span></div>')


def dong_bao_mat(icon: str, tieu_de: str, gia_tri: str, dang_mo: bool) -> str:
    return gon(f'<div class="cn-dong {"mo" if dang_mo else ""}"><span class="cn-bt nho {icon}">{_icon_cn(icon)}</span>'
               f'<div><div class="cn-dong-td">{e(tieu_de)}</div><div class="cn-dong-gt">{e(gia_tri)}</div></div></div>')


def css_ca_nhan() -> str:
    return gon(f"""
<style>
@keyframes cn-len {{ from {{ opacity:0; transform:translateY(22px); }} to {{ opacity:1; transform:none; }} }}
@keyframes cn-mo {{ from {{ opacity:0; transform:translateY(-10px) scaleY(.96); }} to {{ opacity:1; transform:none; }} }}
@keyframes cn-anh-chay {{ from {{ background-position:120% 0; }} to {{ background-position:-120% 0; }} }}
@keyframes cn-nhip {{ 0%,100% {{ box-shadow:0 8px 18px -8px var(--bong); }} 50% {{ box-shadow:0 10px 26px -6px var(--bong); }} }}

/* thẻ từng mục */
.st-key-khung_anh, .st-key-khung_thong_tin, .st-key-khung_bao_mat {{ background:#fff; border:1px solid {VIEN};
    border-radius:24px; padding:22px 24px 20px !important; box-shadow:0 2px 6px rgba(60,20,20,.03), 0 18px 40px -26px rgba(60,20,20,.25);
    animation:cn-len .6s cubic-bezier(.2,.8,.2,1) backwards; transition:transform .35s ease, box-shadow .35s ease; }}
.st-key-khung_thong_tin {{ animation-delay:.08s; }} .st-key-khung_bao_mat {{ animation-delay:.16s; margin-top:6px; }}
.st-key-khung_anh:hover, .st-key-khung_thong_tin:hover, .st-key-khung_bao_mat:hover {{ transform:translateY(-3px);
    box-shadow:0 2px 6px rgba(60,20,20,.03), 0 24px 48px -26px rgba(60,20,20,.32); }}

/* đầu mục: ô biểu tượng màu */
.cn-dau {{ display:flex; gap:14px; align-items:center; margin-bottom:14px; }}
.cn-bt {{ --bong:rgba(232,116,59,.55); flex:none; width:46px; height:46px; border-radius:15px; display:flex; align-items:center;
    justify-content:center; color:#fff; animation:cn-nhip 3s ease-in-out infinite; }}
.cn-bt svg {{ width:23px; height:23px; }}
.cn-bt.anh {{ background:linear-gradient(140deg,#FFB648,#E8743B); }}
.cn-bt.nguoi {{ --bong:rgba(47,122,36,.5); background:linear-gradient(140deg,#5CC24A,#2F7A24); }}
.cn-bt.khoa {{ --bong:rgba(37,99,235,.45); background:linear-gradient(140deg,#60A5FA,#2563EB); }}
.cn-bt.thu {{ --bong:rgba(124,58,237,.45); background:linear-gradient(140deg,#A78BFA,#7C3AED); }}
.cn-bt.ra {{ --bong:rgba(185,28,28,.4); background:linear-gradient(140deg,#F87171,#B91C1C); }}
/* nút Đăng xuất: viền đỏ, rê chuột thì nền đỏ */
.st-key-trang_ca_nhan .st-key-nut_dang_xuat button {{ border-color:#F5C2C2 !important; background:#FFF5F5 !important; }}
.st-key-trang_ca_nhan .st-key-nut_dang_xuat button p {{ color:#B91C1C !important; }}
.st-key-trang_ca_nhan .st-key-nut_dang_xuat button:hover {{ background:#B91C1C !important; border-color:#B91C1C !important;
    box-shadow:0 8px 16px -8px rgba(185,28,28,.7) !important; }}
.st-key-trang_ca_nhan .st-key-nut_dang_xuat button:hover p {{ color:#fff !important; }}
.cn-bt.nho {{ width:40px; height:40px; border-radius:13px; }} .cn-bt.nho svg {{ width:20px; height:20px; }}
.cn-td {{ font-family:'Noto Serif', Georgia, serif; font-size:1.3rem; font-weight:700; color:{CHU}; line-height:1.2; }}
.cn-phu {{ color:{CHU_PHU}; font-size:.86rem; margin-top:2px; }}
.cn-chu-nho {{ color:#A0938A; font-size:.78rem; text-align:center; margin-top:8px; }}

/* form không lồng khung */
.st-key-trang_ca_nhan div[data-testid="stForm"] {{ border:none !important; padding:0 !important; box-shadow:none !important;
    background:transparent !important; }}
/* ô nhập */
.st-key-trang_ca_nhan [data-testid="stWidgetLabel"] p {{ font-size:.84rem !important; font-weight:600 !important; color:#5E544D !important; }}
.st-key-trang_ca_nhan [data-baseweb="input"], .st-key-trang_ca_nhan [data-baseweb="select"] > div {{
    background:#FCFAF8 !important; border:1.5px solid {VIEN} !important; border-radius:13px !important;
    transition:border-color .2s ease, box-shadow .2s ease, background .2s ease !important; }}
.st-key-trang_ca_nhan [data-baseweb="input"] > div, .st-key-trang_ca_nhan [data-baseweb="input"] input,
.st-key-trang_ca_nhan [data-baseweb="base-input"] {{ background:transparent !important; }}
.st-key-trang_ca_nhan [data-baseweb="input"]:hover, .st-key-trang_ca_nhan [data-baseweb="select"] > div:hover {{ border-color:#E9C9A8 !important; }}
.st-key-trang_ca_nhan [data-baseweb="input"]:focus-within, .st-key-trang_ca_nhan [data-baseweb="select"] > div:focus-within {{
    border-color:#E8743B !important; background:#fff !important; box-shadow:0 0 0 4px rgba(232,116,59,.13) !important; }}
.st-key-trang_ca_nhan [data-baseweb="tag"] {{ background:linear-gradient(135deg,#5CC24A,#2F7A24) !important; border-radius:999px !important; }}

/* nút chính: cam chuyển màu có ánh sáng chạy */
.st-key-trang_ca_nhan button[kind="primary"], .st-key-trang_ca_nhan button[kind="primaryFormSubmit"],
.st-key-trang_ca_nhan [data-testid="stFormSubmitButton"] button {{ border:none !important; border-radius:14px !important;
    min-height:44px; padding:0 22px !important; color:#fff !important;
    background-image:linear-gradient(110deg,#E8743B 0%,#F59E52 35%,#FFD9A8 48%,#F59E52 60%,#E8743B 100%) !important;
    background-size:240% 100% !important; animation:cn-anh-chay 3.6s linear infinite;
    box-shadow:0 10px 20px -10px rgba(232,116,59,.8) !important; transition:transform .2s ease !important; }}
.st-key-trang_ca_nhan button[kind="primary"] p, .st-key-trang_ca_nhan [data-testid="stFormSubmitButton"] button p {{
    color:#fff !important; font-weight:700 !important; }}
.st-key-trang_ca_nhan button[kind="primary"]:hover, .st-key-trang_ca_nhan [data-testid="stFormSubmitButton"] button:hover {{
    transform:translateY(-2px); }}
/* nút phụ (Đổi email, Đổi mật khẩu, Huỷ...) */
.st-key-trang_ca_nhan button[kind="secondary"] {{ border-radius:999px !important; border:1.5px solid #CFE6C4 !important;
    background:#F3FAEF !important; min-height:40px; transition:all .2s ease !important; }}
.st-key-trang_ca_nhan button[kind="secondary"] p {{ color:#2F6B22 !important; font-weight:700 !important; }}
.st-key-trang_ca_nhan button[kind="secondary"]:hover {{ background:#2F6B22 !important; border-color:#2F6B22 !important;
    transform:translateY(-2px); box-shadow:0 8px 16px -8px rgba(47,107,34,.7); }}
.st-key-trang_ca_nhan button[kind="secondary"]:hover p {{ color:#fff !important; }}

/* khu tải ảnh */
.st-key-khung_anh [data-testid="stFileUploaderDropzone"] {{ border:2px dashed #F2C38E !important; border-radius:18px !important;
    background:linear-gradient(135deg,#FFFBF5,#FFF3E4) !important; padding:18px !important; transition:all .25s ease; }}
.st-key-khung_anh [data-testid="stFileUploaderDropzone"]:hover {{ border-color:#E8743B !important; background:#FFF1E2 !important;
    transform:scale(1.015); }}
.st-key-khung_anh [data-testid="stFileUploaderDropzone"] button {{ border-radius:999px !important; border:none !important;
    background:linear-gradient(135deg,#FFB648,#E8743B) !important; color:#fff !important; }}
.st-key-khung_anh [data-testid="stFileUploaderDropzone"] button p, .st-key-khung_anh [data-testid="stFileUploaderDropzone"] button svg {{
    color:#fff !important; fill:#fff !important; }}
.cn-xem-truoc {{ position:relative; width:150px; height:150px; margin:14px auto 12px; border-radius:50%; padding:4px;
    background:conic-gradient(#F2B33D,#E8743B,#FFE29A,#F2B33D); animation:cn-len .5s ease backwards; }}
.cn-xem-truoc img {{ width:100%; height:100%; border-radius:50%; object-fit:cover; border:3px solid #fff; box-sizing:border-box; }}
.cn-chu-cai {{ width:100%; height:100%; border-radius:50%; border:3px solid #fff; box-sizing:border-box; display:flex;
    align-items:center; justify-content:center; font-size:3.4rem; font-weight:800; color:#fff;
    background:radial-gradient(circle at 35% 30%, #6BCB52, #2F7A24 60%, #1F4A16); }}
.cn-xem-truoc span {{ position:absolute; left:50%; bottom:-6px; transform:translateX(-50%); background:#1F1A17; color:#fff;
    font-size:.72rem; font-weight:700; padding:3px 10px; border-radius:999px; white-space:nowrap; }}

/* dòng bảo mật + khung mở ra khi bấm */
.cn-dong {{ display:flex; gap:14px; align-items:center; padding:12px 14px; border-radius:16px; border:1px solid {VIEN};
    background:#FCFAF8; transition:all .25s ease; }}
.cn-dong.mo {{ background:#FFF7EF; border-color:#F2C38E; }}
.cn-dong-td {{ font-weight:700; color:{CHU}; }}
.cn-dong-gt {{ color:{CHU_PHU}; font-size:.9rem; letter-spacing:.02em; }}
.st-key-mo_doi_email, .st-key-mo_doi_mk {{ margin:-2px 0 10px; padding:18px 20px 6px !important; border-radius:16px;
    background:linear-gradient(180deg,#FFF7EF 0%,#FFFFFF 100%); border:1px solid #F6DCC0; border-left:4px solid #E8743B;
    transform-origin:top; animation:cn-mo .35s cubic-bezier(.2,.8,.2,1); }}

/* thẻ đầu trang: lấp lánh nhẹ */
.the-ho-so:before {{ content:""; position:absolute; inset:0; pointer-events:none;
    background:linear-gradient(105deg, transparent 40%, rgba(255,255,255,.12) 50%, transparent 60%);
    background-size:250% 100%; animation:cn-anh-chay 6s linear infinite; }}
@media (prefers-reduced-motion: reduce) {{ .st-key-trang_ca_nhan *, .the-ho-so:before {{ animation:none !important; }} }}
</style>""")


# ================================================================ NÔNG TRẠI BỒ NÔNG
# ---------------- Vẽ cây trưởng thành giống cây thật (lá có khối, bóng sáng, hạt/trái căng mọng)

VIEN = 'stroke="#1E4D16" stroke-width=".6" stroke-opacity=".55"'

def _la_dai(x0, y0, dx, dy, cong, rong, fill, vien=True):
    """Lá dài cong (lúa): gốc (x0,y0) -> ngọn (x0+dx, y0+dy), độ cong 'cong'."""
    mx, my = x0 + dx * .5 + cong, y0 + dy * .5
    nx, ny = -dy, dx
    L = math.hypot(nx, ny) or 1
    nx, ny = nx / L * rong / 2, ny / L * rong / 2
    return (f'<path d="M{x0 - nx:.1f} {y0 - ny:.1f} Q{mx - nx * 1.6:.1f} {my - ny * 1.6:.1f} {x0 + dx:.1f} {y0 + dy:.1f} '
            f'Q{mx + nx * 1.6:.1f} {my + ny * 1.6:.1f} {x0 + nx:.1f} {y0 + ny:.1f}Z" fill="{fill}" '
            + (VIEN if vien else '') + '/>')

def defs_chung():
    return ('<defs>'
            '<linearGradient id="g_luaXanh" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#2E7D32"/><stop offset="1" stop-color="#8BD45E"/></linearGradient>'
            '<linearGradient id="g_luaXanh2" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#1F6B24"/><stop offset="1" stop-color="#5DBB46"/></linearGradient>'
            '<linearGradient id="g_luaVang" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#9C7A1E"/><stop offset="1" stop-color="#F3D36B"/></linearGradient>'
            '<linearGradient id="g_luaVang2" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#7E6216"/><stop offset="1" stop-color="#D9B443"/></linearGradient>'
            '<radialGradient id="g_hatVang" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#FFF1B0"/><stop offset=".5" stop-color="#F2C230"/><stop offset="1" stop-color="#B98512"/></radialGradient>'
            '<radialGradient id="g_hatXanh" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#E9F7B8"/><stop offset=".6" stop-color="#A9CF52"/><stop offset="1" stop-color="#6E9A2C"/></radialGradient>'
            '<radialGradient id="g_laTim" cx="40%" cy="25%" r="85%"><stop offset="0" stop-color="#8EDC63"/><stop offset=".55" stop-color="#43A33A"/><stop offset="1" stop-color="#1F6B24"/></radialGradient>'
            '<radialGradient id="g_laTim2" cx="40%" cy="25%" r="85%"><stop offset="0" stop-color="#6CCB52"/><stop offset=".6" stop-color="#2F8A2B"/><stop offset="1" stop-color="#175A1C"/></radialGradient>'
            '<linearGradient id="g_tru" x1="0" x2="1"><stop offset="0" stop-color="#5C3418"/><stop offset=".45" stop-color="#A9784A"/><stop offset="1" stop-color="#4E2C14"/></linearGradient>'
            '<radialGradient id="g_do" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#FF9A8A"/><stop offset=".45" stop-color="#E0282E"/><stop offset="1" stop-color="#8E0F1A"/></radialGradient>'
            '<radialGradient id="g_cam" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#FFD39A"/><stop offset=".5" stop-color="#F08A24"/><stop offset="1" stop-color="#A9500E"/></radialGradient>'
            '<radialGradient id="g_xanhTrai" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#D8F2A0"/><stop offset=".55" stop-color="#6DB33A"/><stop offset="1" stop-color="#3B7A1E"/></radialGradient>'
            '<radialGradient id="g_laCP" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="#4FB043"/><stop offset=".6" stop-color="#1F7A2A"/><stop offset="1" stop-color="#0F4A18"/></radialGradient>'
            '<radialGradient id="g_laCP2" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="#78C85A"/><stop offset=".6" stop-color="#2F8F33"/><stop offset="1" stop-color="#16591F"/></radialGradient>'
            '</defs>')

# ---------------- LÚA
def _bong(x0, y0, h, chin, dai=1.0):
    p0 = (x0, y0); p1 = (x0 + h * 9 * dai, y0 - 13 * dai); p2 = (x0 + h * 22 * dai, y0 + 14 * dai)
    def P(t): return ((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0], (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1])
    s = (f'<path d="M{p0[0]:.1f} {p0[1]:.1f} Q{p1[0]:.1f} {p1[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}" '
         f'stroke="{"#A07F22" if chin else "#6E9A2C"}" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
    g = "g_hatVang" if chin else "g_hatXanh"
    for i in range(2, 19):
        t = i / 18
        x, y = P(t); x2, y2 = P(min(t + .02, 1))
        goc = math.degrees(math.atan2(y2 - y, x2 - x))
        for ph in (-1, 1):
            gx, gy = x + ph * 1.5, y + 1.6
            s += (f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="1.9" ry="3.1" fill="url(#{g})" stroke="#8A6410" '
                  f'stroke-width=".35" stroke-opacity=".6" transform="rotate({goc - 90 + ph * 28:.0f} {gx:.1f} {gy:.1f})"/>')
    return s

def svg_lua(chin):
    r = random.Random(3)
    s = ""
    toi, sang = (("url(#g_luaVang2)", "url(#g_luaVang)") if chin else ("url(#g_luaXanh2)", "url(#g_luaXanh)"))
    # lá lúa mảnh, dài, cong vòng ra ngoài (lớp sau đậm, lớp trước sáng)
    for lop, fill in ((0, toi), (1, sang)):
        n = 13
        for k in range(n):
            goc = -70 + k * (140 / (n - 1)) + r.uniform(-5, 5)
            dai = (80 if lop == 0 else 70) - abs(goc) * .28 + r.uniform(-5, 5)
            dx = math.sin(math.radians(goc)) * dai
            dy = -math.cos(math.radians(goc)) * dai + abs(goc) * .32      # lá ngoài rủ ngọn xuống
            s += _la_dai(60 + (k - n / 2) * .5, 101, dx, dy, goc * .22 + r.uniform(-3, 3), 2.7 if lop else 3.0, fill)
    ngon = ([(-12, 26, -1, 1.05), (-3, 20, -1, 1.1), (6, 20, 1, 1.1), (15, 26, 1, 1.05), (-20, 36, -1, .9), (23, 36, 1, .9)]
            if chin else [(-8, 24, -1, .85), (8, 24, 1, .85)])
    for dx, y, h, d in ngon:
        s += (f'<path d="M{60 + dx * .25:.1f} 100 Q{60 + dx * .6:.1f} 62 {60 + dx:.1f} {y}" '
              f'stroke="{"#B8952F" if chin else "#3E9B2F"}" stroke-width="1.8" fill="none"/>')
        s += _bong(60 + dx, y, h, chin, d)
    s += '<ellipse cx="60" cy="101" rx="13" ry="3" fill="#3B220E" opacity=".35"/>'
    return s

# ---------------- HỒ TIÊU
def _la_tim(x, y, dai, goc, g):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({goc:.0f})">'
            f'<path d="M0 0 C{-dai*.62:.1f} {-dai*.1:.1f} {-dai*.58:.1f} {-dai*.88:.1f} 0 {-dai:.1f} '
            f'C{dai*.58:.1f} {-dai*.88:.1f} {dai*.62:.1f} {-dai*.1:.1f} 0 0Z" fill="url(#{g})" {VIEN}/>'
            f'<path d="M0 -1 Q{dai*.05:.1f} {-dai*.5:.1f} 0 {-dai*.92:.1f}" stroke="#D8F5B0" stroke-width=".7" opacity=".7" fill="none"/>'
            f'<path d="M0 {-dai*.3:.1f} Q{-dai*.2:.1f} {-dai*.45:.1f} {-dai*.32:.1f} {-dai*.62:.1f} M0 {-dai*.3:.1f} '
            f'Q{dai*.2:.1f} {-dai*.45:.1f} {dai*.32:.1f} {-dai*.62:.1f}" stroke="#D8F5B0" stroke-width=".45" opacity=".5" fill="none"/>'
            f'<ellipse cx="{-dai*.18:.1f}" cy="{-dai*.62:.1f}" rx="{dai*.1:.1f}" ry="{dai*.22:.1f}" fill="#fff" opacity=".22"/></g>')

def _gie(x, y, dai, chin, r):
    s = f'<path d="M{x} {y} q.8 2.5 0 4.5" stroke="#4E7A22" stroke-width="1.1" fill="none"/>'
    n = int(dai / 2.4)
    for i in range(n):
        t = i / max(n - 1, 1)
        g = ("g_xanhTrai" if t < .3 else ("g_cam" if t < .55 else "g_do")) if chin else "g_xanhTrai"
        cy = y + 5.5 + i * 2.3
        rong = 3.4 * (1 - t * .45)
        for dx in (-rong / 2, rong / 2):
            s += f'<circle cx="{x + dx + r.uniform(-.3, .3):.1f}" cy="{cy:.1f}" r="1.75" fill="url(#{g})"/>'
    return s

def svg_tieu(chin):
    r = random.Random(5)
    s = ('<rect x="54" y="4" width="12" height="98" rx="3" fill="url(#g_tru)"/>'
         '<rect x="53" y="3" width="14" height="4" rx="2" fill="#6B3F1F"/>')
    s += ''.join(f'<path d="M55 {y} q5 2.5 10 0" stroke="#3E220E" stroke-width=".9" fill="none" opacity=".5"/>' for y in range(12, 100, 9))
    s += ('<path d="M60 100 C46 92 74 84 60 76 C46 68 74 60 60 52 C46 44 74 36 60 28 C48 22 70 14 60 8" '
          'stroke="#3E6B1A" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    la = []
    for i, y in enumerate(range(94, 10, -9)):
        ph = -1 if i % 2 else 1
        la.append((60 + ph * 5, y, 15 + r.uniform(-1.5, 2) - (96 - y) * .03, ph * (55 + r.uniform(-10, 15)), "g_laTim" if i % 3 else "g_laTim2"))
        la.append((60 - ph * 4, y - 3, 12 + r.uniform(-1, 1.5), -ph * (95 + r.uniform(-10, 10)), "g_laTim2"))
    # lá sau trước, lá trước sau
    for x, y, d, g, gid in la[1::2]:
        s += _la_tim(x, y, d, g, gid)
    for x, y, d, g, gid in la[0::2]:
        s += _la_tim(x, y, d, g, gid)
    gie = ([(41, 74), (79, 66), (39, 56), (81, 48), (42, 38), (78, 30), (36, 86), (84, 82)] if chin
           else [(42, 70), (78, 58), (41, 46), (79, 36)])
    for x, y in gie:
        s += _gie(x, y, 19 if chin else 14, chin, r)
    return s

# ---------------- CÀ PHÊ
def _la_cp(x, y, dai, goc, g):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({goc:.0f})">'
            f'<path d="M0 0 C{dai*.25:.1f} {-dai*.36:.1f} {dai*.78:.1f} {-dai*.32:.1f} {dai:.1f} 0 '
            f'C{dai*.78:.1f} {dai*.32:.1f} {dai*.25:.1f} {dai*.36:.1f} 0 0Z" fill="url(#{g})" {VIEN}/>'
            f'<path d="M1 0 L{dai*.93:.1f} 0" stroke="#BFE8A0" stroke-width=".6" opacity=".55"/>'
            f'<path d="M{dai*.18:.1f} {-dai*.14:.1f} Q{dai*.5:.1f} {-dai*.25:.1f} {dai*.8:.1f} {-dai*.08:.1f}" '
            f'stroke="#fff" stroke-width="1" opacity=".3" fill="none"/></g>')

def _chum(x, y, chin, r, n=6):
    s = ""
    for i in range(n):
        dx, dy = r.uniform(-3.6, 3.6), r.uniform(-2, 2.4)
        g = (r.choice(["g_do", "g_do", "g_do", "g_cam", "g_xanhTrai"]) if chin else "g_xanhTrai")
        s += f'<circle cx="{x + dx:.1f}" cy="{y + dy:.1f}" r="2.7" fill="url(#{g})" stroke="#5A0A12" stroke-width=".3" stroke-opacity=".4"/>'
        s += f'<circle cx="{x + dx - .8:.1f}" cy="{y + dy - .9:.1f}" r=".75" fill="#fff" opacity=".6"/>'
    return s

def svg_ca_phe(chin):
    r = random.Random(11)
    s = '<path d="M60 104 C57 92 62 84 60 70" stroke="#5C3A1E" stroke-width="5" fill="none" stroke-linecap="round"/>'
    # tán cây tròn: lá xếp theo vòng ellipse, lớp sau tối -> lớp trước sáng
    cx, cy, rx, ry = 60, 50, 44, 38
    la = []
    for lop in range(3):
        for k in range(52 - lop * 8):
            a = r.uniform(0, 2 * math.pi)
            rr = math.sqrt(r.uniform(0, 1)) * (1 - lop * .12)
            x = cx + math.cos(a) * rx * rr
            y = cy + math.sin(a) * ry * rr * .95
            goc = math.degrees(a) + r.uniform(-35, 35)
            la.append((lop, x, y, 12.5 - lop * .8 + r.uniform(-1, 1.5), goc))
    for lop, x, y, d, goc in la:
        if lop == 0:
            s += _la_cp(x, y, d, goc, "g_laCP")
    cho = [(34, 58), (50, 42), (72, 44), (86, 56), (58, 30), (42, 72), (78, 72), (60, 60), (28, 44), (92, 42), (50, 84), (70, 86)]
    chum = cho if chin else cho[:6]
    for lop, x, y, d, goc in la:
        if lop >= 1:
            s += _la_cp(x, y, d, goc, "g_laCP2" if lop == 2 else "g_laCP")
    for x, y in chum:
        s += _chum(x, y, chin, r, 7 if chin else 4)
    s += '<ellipse cx="60" cy="103" rx="14" ry="3" fill="#3B220E" opacity=".35"/>'
    return s


# Ảnh cây thật (image/cay/*.webp, đã tách nền) cho giai đoạn đang lớn và chín
_THU_MUC_ANH_CAY = __import__("pathlib").Path(__file__).parent / "image" / "cay"
_ANH_CAY = {}


def _anh_cay_that(cay: str, giai_doan: int):
    ten = {"lua": "lua", "ho_tieu": "tieu", "ca_phe": "ca_phe"}.get(cay)
    if not ten or giai_doan < 2:
        return None
    khoa = f"{ten}_{'chin' if giai_doan == 3 else 'dang_lon'}"
    if khoa not in _ANH_CAY:
        f = _THU_MUC_ANH_CAY / f"{khoa}.webp"
        _ANH_CAY[khoa] = __import__("base64").b64encode(f.read_bytes()).decode() if f.exists() else ""
    if not _ANH_CAY[khoa]:
        return None
    return (f'<img class="hinh-cay anh-that cay-{cay} gd{giai_doan}" alt="" '
            f'src="data:image/webp;base64,{_ANH_CAY[khoa]}">')


def _svg_cay(cay: str, giai_doan: int) -> str:
    """Hình cây theo loại & giai đoạn (0 hạt · 1 mầm · 2 lớn · 3 chín). Có ảnh thật thì dùng ảnh thật."""
    anh = _anh_cay_that(cay, giai_doan)
    if anh:
        return anh
    if giai_doan == 0:
        than = ('<ellipse cx="60" cy="96" rx="9" ry="6" fill="#8B5A2B"/><ellipse cx="57" cy="94" rx="3" ry="1.6" '
                'fill="#C08A55"/><path d="M60 90 q2 -6 0 -10" stroke="#5DBB46" stroke-width="2.5" fill="none" '
                'stroke-linecap="round"/>')
    elif giai_doan == 1:
        than = ('<path d="M60 98 V70" stroke="#3E9B2F" stroke-width="4" stroke-linecap="round"/>'
                '<path d="M60 78 C46 76 40 66 42 58 C52 60 59 67 60 78Z" fill="#6CCB52"/>'
                '<path d="M60 74 C72 70 78 60 76 52 C66 55 60 63 60 74Z" fill="#4FB43A"/>')
    elif cay == "lua":                       # cây lớn / chín: vẽ chi tiết như cây thật
        than = defs_chung() + svg_lua(giai_doan == 3)
    elif cay == "ho_tieu":
        than = defs_chung() + svg_tieu(giai_doan == 3)
    else:
        than = defs_chung() + svg_ca_phe(giai_doan == 3)
    return f'<svg viewBox="0 0 120 110" class="hinh-cay gd{giai_doan}">{than}</svg>'


def _thoi_gian(giay: int) -> str:
    if giay <= 0:
        return "0 phút"
    gio, phut = divmod(int(giay) // 60, 60)
    return (f"{gio} giờ " if gio else "") + f"{phut} phút"


def o_dat_nong_trai(d: dict, cay_info: dict, giai_doan_ten: list, goi_mo: str) -> str:
    """Thẻ 1 ô đất: hình cây, trạng thái, thanh tiến độ."""
    if not d["mo"]:
        return gon(f'<div class="o-dat khoa"><div class="dat"></div><div class="khoa-dat">{SVG_KHOA}</div>'
                   f'<div class="od-ten">Ô đất {d["vi_tri"] + 1}</div>'
                   f'<div class="od-tt">Mở bằng <b>{e(goi_mo)}</b></div></div>')
    if not d["cay"]:
        return gon(f'<div class="o-dat trong"><div class="dat"><span class="luong"></span></div>'
                   f'<div class="od-ten">Ô đất {d["vi_tri"] + 1} · đất trống</div>'
                   f'<div class="od-tt">Chọn hạt giống bên dưới để gieo 🌱</div></div>')
    c = cay_info[d["cay"]]
    gd_ = d["giai_doan"]
    chin = gd_ == 3
    trang_thai = ("✨ Chín rồi – thu hoạch thôi!" if chin else
                  ("💧 Đất khô – cần tưới!" if d["can_tuoi"] else f"Còn khoảng {_thoi_gian(d['con_lai_giay'])}"))
    giot = '<span class="giot g1"></span><span class="giot g2"></span><span class="giot g3"></span>' if d["can_tuoi"] else ""
    lap = '<span class="lap l1">✦</span><span class="lap l2">✦</span><span class="lap l3">✦</span>' if chin else ""
    return gon(f'<div class="o-dat {"chin" if chin else ""} {"can-tuoi" if d["can_tuoi"] else ""}">'
               f'<div class="san-khau-cay">{_svg_cay(d["cay"], gd_)}{giot}{lap}</div><div class="dat"></div>'
               f'<div class="od-ten">{ICON_CAY[d["cay"]]} {e(c["ten"])} · {e(giai_doan_ten[gd_])}</div>'
               f'<div class="od-thanh"><span style="width:{d["tien_do"] * 100:.0f}%"></span></div>'
               f'<div class="od-tt">{trang_thai}</div></div>')


def dau_nong_trai(ng: dict, xu_thu: int, tran_xu: int, so_o: int) -> str:
    pt = 100 if ng["cap_toi_da"] else ng["kn_trong_cap"] / max(ng["kn_can"], 1) * 100
    return gon(f'<div class="nt-dau"><div class="nt-may m1"></div><div class="nt-may m2"></div>'
               f'<div class="nt-mat-troi"></div><div class="nt-trai"><div class="nt-td">Nông Trại Bồ Nông</div>'
               f'<div class="nt-phu">Trồng lúa, hồ tiêu, cà phê · chăm cây, thu hoạch để nhận xu</div>'
               f'<div class="nt-cap"><span class="nt-huy-hieu">Cấp {ng["cap"]}</span><div class="nt-kn"><span '
               f'style="width:{pt:.0f}%"></span></div><span class="nt-kn-chu">'
               + ("Cấp tối đa" if ng["cap_toi_da"] else f'{ng["kn_trong_cap"]}/{ng["kn_can"]} KN')
               + f'</span></div></div><div class="nt-so"><div><b>{xu_thu}/{tran_xu}</b><span>xu thu hoạch hôm nay</span></div>'
               f'<div><b>{so_o}/3</b><span>ô đất đang mở</span></div></div></div>')


def the_nhiem_vu(nv: dict) -> str:
    dong = "".join(f'<div class="nv-dong {"xong" if x["da"] >= x["can"] else ""}"><span class="nv-dau">'
                   f'{"✓" if x["da"] >= x["can"] else ""}</span><span>{e(x["ten"])}</span><b>{x["da"]}/{x["can"]}</b>'
                   f'<div class="nv-thanh"><span style="width:{x["da"] / x["can"] * 100:.0f}%"></span></div></div>'
                   for x in nv["ds"])
    return gon(f'<div class="nt-the"><div class="nt-the-td">📋 Nhiệm vụ hôm nay <span>+3 xu</span></div>{dong}</div>')


def the_kho(kho: dict, cay_info: dict) -> str:
    o = "".join(f'<div class="kho-o"><span class="kho-bt">{ICON_CAY.get(m, c["bieu_tuong"])}</span><b>{kho.get(m, 0)}</b>'
                f'<span>{e(c["ten"])}</span></div>' for m, c in cay_info.items())
    return gon(f'<div class="nt-the"><div class="nt-the-td">🏠 Kho nông sản</div><div class="kho">{o}</div></div>')


def lich_su_doan(ds: list) -> str:
    if not ds:
        return ""
    chu = {"tang": "tăng", "ngang": "đi ngang", "giam": "giảm"}
    dong = "".join(
        f'<div class="dd-dong"><span>{pd.Timestamp(d["ngay_doan"]):%d/%m} · {e(d["nong_san"])} {chu[d["huong"]]}</span>'
        + ('<b class="cho">⏳ chờ giá mới</b>' if not d["ket_qua"] else
           ('<b class="dung">✓ Đúng · +3 xu</b>' if d["ket_qua"] == "dung" else
            f'<b class="sai">✗ Thực tế {chu.get(d["huong_that"], "")}</b>')) + "</div>" for d in ds)
    return gon(f'<div class="dd-ls">{dong}</div>')


def xu_bay(so_xu: int) -> str:
    """Hiệu ứng đồng xu bay lên + pháo giấy sau khi nhận thưởng."""
    return gon(f'<div class="xu-bay"><span class="dong-xu">xu</span>+{so_xu} xu</div>'
               '<div class="phao-giay">' + "".join(f'<i style="left:{x}%;animation-delay:{d}s;background:{m}"></i>'
                                                   for x, d, m in [(10, 0, "#F2B33D"), (22, .1, "#46A033"), (35, .2, "#E8743B"),
                                                                   (50, 0, "#2563EB"), (63, .15, "#F2B33D"), (76, .05, "#D7263D"),
                                                                   (88, .2, "#46A033")]) + "</div>")


def css_nong_trai() -> str:
    return gon(f"""
<style>
@keyframes dung-dua {{ 0%,100% {{ transform:rotate(-2.5deg); }} 50% {{ transform:rotate(2.5deg); }} }}
@keyframes ru-xuong {{ 0%,100% {{ transform:rotate(-1deg) translateY(2px); }} 50% {{ transform:rotate(1deg) translateY(3px); }} }}
@keyframes giot-roi {{ 0% {{ transform:translateY(-14px); opacity:0; }} 30% {{ opacity:1; }} 100% {{ transform:translateY(46px); opacity:0; }} }}
@keyframes lap-chin {{ 0%,100% {{ opacity:0; transform:scale(.4) rotate(0); }} 50% {{ opacity:1; transform:scale(1.1) rotate(90deg); }} }}
@keyframes may-troi {{ from {{ transform:translateX(-30px); }} to {{ transform:translateX(30px); }} }}
@keyframes troi-sang {{ 0%,100% {{ box-shadow:0 0 30px 10px rgba(255,214,90,.55); }} 50% {{ box-shadow:0 0 46px 18px rgba(255,214,90,.75); }} }}
@keyframes nt-len {{ from {{ opacity:0; transform:translateY(24px) scale(.97); }} to {{ opacity:1; transform:none; }} }}
@keyframes chin-sang {{ 0%,100% {{ box-shadow:0 0 0 0 rgba(242,179,61,0), 0 14px 30px -18px rgba(60,40,10,.4); }}
    50% {{ box-shadow:0 0 0 6px rgba(242,179,61,.28), 0 14px 30px -18px rgba(60,40,10,.4); }} }}
@keyframes xu-len {{ 0% {{ opacity:0; transform:translate(-50%,30px) scale(.6); }} 20% {{ opacity:1; transform:translate(-50%,0) scale(1.15); }}
    80% {{ opacity:1; transform:translate(-50%,-60px) scale(1); }} 100% {{ opacity:0; transform:translate(-50%,-110px) scale(.9); }} }}
@keyframes giay-roi {{ 0% {{ transform:translateY(-20px) rotate(0); opacity:1; }} 100% {{ transform:translateY(340px) rotate(540deg); opacity:0; }} }}

/* đầu trang: trời, mây, mặt trời */
.nt-dau {{ position:relative; overflow:hidden; display:flex; justify-content:space-between; align-items:flex-end; gap:20px;
    flex-wrap:wrap; padding:28px 30px 24px; margin:.6rem 0 1.2rem; border-radius:26px; color:#1F3B12;
    background:linear-gradient(180deg,#BFE6FF 0%,#E3F5FF 55%,#D6F0C2 56%,#A9DC8A 100%);
    box-shadow:0 18px 40px -24px rgba(31,74,22,.6); }}
.nt-may {{ position:absolute; height:26px; border-radius:20px; background:#fff; opacity:.9; animation:may-troi 9s ease-in-out infinite alternate; }}
.nt-may:before, .nt-may:after {{ content:""; position:absolute; background:#fff; border-radius:50%; }}
.nt-may.m1 {{ width:90px; top:22px; left:42%; }} .nt-may.m1:before {{ width:40px; height:40px; left:14px; top:-18px; }}
.nt-may.m1:after {{ width:30px; height:30px; left:46px; top:-12px; }}
.nt-may.m2 {{ width:70px; top:54px; left:64%; animation-duration:12s; opacity:.75; }}
.nt-may.m2:before {{ width:30px; height:30px; left:12px; top:-14px; }}
.nt-mat-troi {{ position:absolute; right:40px; top:22px; width:54px; height:54px; border-radius:50%;
    background:radial-gradient(circle,#FFF4B8,#FFD65A); animation:troi-sang 4s ease-in-out infinite; }}
.nt-trai {{ position:relative; z-index:1; flex:1; min-width:260px; }}
.nt-td {{ font-family:'Noto Serif', Georgia, serif; font-size:2.1rem; font-weight:700; color:#1F4A16; }}
.nt-phu {{ color:#335A22; font-size:.95rem; margin-top:2px; }}
.nt-cap {{ display:flex; align-items:center; gap:12px; margin-top:14px; max-width:460px; }}
.nt-huy-hieu {{ flex:none; padding:5px 12px; border-radius:999px; font-weight:800; font-size:.85rem; color:#fff;
    background:linear-gradient(135deg,#F4C24D,#C9851A); box-shadow:0 6px 14px -6px rgba(168,101,14,.7); }}
.nt-kn {{ flex:1; height:12px; border-radius:999px; background:rgba(255,255,255,.7); overflow:hidden; border:1px solid rgba(31,74,22,.15); }}
.nt-kn span {{ display:block; height:100%; border-radius:999px; background:linear-gradient(90deg,#5CC24A,#2F7A24); }}
.nt-kn-chu {{ font-size:.8rem; font-weight:700; color:#335A22; white-space:nowrap; }}
.nt-so {{ position:relative; z-index:1; display:flex; gap:12px; }}
.nt-so div {{ background:rgba(255,255,255,.82); border-radius:16px; padding:10px 16px; text-align:center; min-width:110px;
    box-shadow:0 6px 16px -10px rgba(31,74,22,.5); }}
.nt-so b {{ display:block; font-size:1.4rem; color:#1F4A16; }} .nt-so span {{ font-size:.75rem; color:#5E6B55; }}

/* ô đất */
.o-dat {{ position:relative; height:290px; border-radius:24px; overflow:hidden; text-align:center; padding:0 14px 14px;
    background:linear-gradient(180deg,#F2FBEA 0%,#E4F4D6 62%,#FFFFFF 62%); border:1px solid #DCEBCF;
    box-shadow:0 14px 30px -18px rgba(60,40,10,.4); display:flex; flex-direction:column; justify-content:flex-end;
    transition:transform .3s ease, box-shadow .3s ease; }}
.o-dat:hover {{ transform:translateY(-4px); }}
.o-dat .dat {{ position:absolute; left:14px; right:14px; top:154px; height:36px; border-radius:50% / 60%;
    background:radial-gradient(ellipse at 50% 30%, #A8774A 0%, #7A4E2A 70%, #5E3A1E 100%);
    box-shadow:inset 0 -4px 8px rgba(0,0,0,.25); }}
.o-dat .dat .luong {{ position:absolute; inset:9px 22px; border-top:2px dashed rgba(255,255,255,.18); border-bottom:2px dashed rgba(255,255,255,.18); }}
.san-khau-cay {{ position:absolute; left:0; right:0; top:6px; height:160px; z-index:1; }}
.hinh-cay {{ width:168px; height:156px; transform-origin:50% 92%; animation:dung-dua 3.6s ease-in-out infinite; }}
.o-dat.can-tuoi .hinh-cay {{ filter:saturate(.35) sepia(.45) brightness(1.02); animation:ru-xuong 3s ease-in-out infinite; }}
.o-dat.chin {{ animation:chin-sang 2.2s ease-in-out infinite; border-color:#F2D27A;
    background:linear-gradient(180deg,#FFF8E1 0%,#FDEFC4 62%,#FFFFFF 62%); }}
.giot {{ position:absolute; top:6px; width:7px; height:11px; border-radius:50% 50% 50% 50% / 65% 65% 35% 35%;
    background:linear-gradient(180deg,#9AD7FF,#2E8BE0); animation:giot-roi 1.6s ease-in infinite; opacity:0; }}
.giot.g1 {{ left:38%; }} .giot.g2 {{ left:52%; animation-delay:.5s; }} .giot.g3 {{ left:62%; animation-delay:1s; }}
.lap {{ position:absolute; color:#F2B33D; font-size:18px; animation:lap-chin 2s ease-in-out infinite; }}
.lap.l1 {{ left:24%; top:10px; }} .lap.l2 {{ right:22%; top:30px; animation-delay:.6s; }}
.lap.l3 {{ left:62%; top:2px; animation-delay:1.2s; font-size:13px; }}
.od-ten {{ position:relative; z-index:2; font-weight:800; color:{CHU}; font-size:.98rem; }}
.od-thanh {{ position:relative; z-index:2; height:9px; margin:8px 6px 6px; border-radius:999px; background:#EEF2E8; overflow:hidden; }}
.od-thanh span {{ display:block; height:100%; border-radius:999px; background:linear-gradient(90deg,#9BE07F,#2F7A24); }}
.o-dat.chin .od-thanh span {{ background:linear-gradient(90deg,#FFD65A,#E39B12); }}
.od-tt {{ position:relative; z-index:2; font-size:.85rem; color:{CHU_PHU}; min-height:1.2em; }}
.o-dat.can-tuoi .od-tt {{ color:#1D6FB8; font-weight:700; }} .o-dat.chin .od-tt {{ color:#B26B00; font-weight:800; }}
.o-dat.trong .od-tt {{ margin-bottom:6px; }}
.o-dat.khoa {{ background:repeating-linear-gradient(135deg,#F6F3EF 0 12px,#EFEAE4 12px 24px); border:1.5px dashed #D8CCC0; }}
.o-dat.khoa .dat {{ filter:grayscale(.7) brightness(1.1); opacity:.6; }}
.khoa-dat {{ position:absolute; left:50%; top:80px; transform:translateX(-50%); width:52px; height:52px; border-radius:16px;
    display:flex; align-items:center; justify-content:center; color:#fff; background:linear-gradient(135deg,#F4C24D,#C9851A);
    box-shadow:0 8px 18px -6px rgba(168,101,14,.6); }}
.khoa-dat svg {{ width:28px; height:28px; }}
.o-dat.khoa .od-tt b {{ color:{VANG_DAM}; }}

/* nút dưới ô đất */
.st-key-trang_nong_trai [class*="st-key-nt_"] button {{ border-radius:14px !important; min-height:42px;
    transition:transform .2s ease, box-shadow .2s ease !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_gieo_"] button {{ background:#F1F8EC !important; border:1.5px solid #CFE6C4 !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_gieo_"] button p {{ color:#2F6B22 !important; font-weight:700 !important; font-size:.88rem !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_tuoi_"] button {{ border:none !important; background:linear-gradient(135deg,#60B8FF,#1D6FB8) !important;
    box-shadow:0 10px 20px -10px rgba(29,111,184,.8) !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_thu_"] button {{ border:none !important; background:linear-gradient(135deg,#FFD65A,#E8743B) !important;
    animation:chin-sang 2s ease-in-out infinite; }}
.st-key-trang_nong_trai [class*="st-key-nt_tuoi_"] button p, .st-key-trang_nong_trai [class*="st-key-nt_thu_"] button p {{
    color:#fff !important; font-weight:800 !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_"] button:hover {{ transform:translateY(-2px) scale(1.02); }}

/* thẻ dưới: nhiệm vụ, đoán giá, kho */
.nt-the {{ background:#fff; border:1px solid {VIEN}; border-radius:20px; padding:16px 18px; margin-bottom:12px;
    box-shadow:0 12px 28px -22px rgba(60,20,20,.35); animation:nt-len .6s ease .1s backwards; }}
.nt-the-td {{ font-weight:800; color:{CHU}; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; }}
.nt-the-td span {{ font-size:.75rem; padding:3px 9px; border-radius:999px; background:#FFF4DA; color:#7A4B00; }}
.nv-dong {{ display:grid; grid-template-columns:22px 1fr auto; gap:4px 8px; align-items:center; padding:6px 0; font-size:.92rem; }}
.nv-dau {{ width:20px; height:20px; border-radius:50%; border:2px solid #D8CCC0; display:flex; align-items:center;
    justify-content:center; font-size:.7rem; font-weight:900; color:#fff; box-sizing:border-box; }}
.nv-dong.xong .nv-dau {{ background:#46A033; border-color:#46A033; }}
.nv-dong.xong span:nth-child(2) {{ color:#2F7A24; font-weight:700; }}
.nv-thanh {{ grid-column:2 / 4; height:6px; border-radius:999px; background:#F1EDE8; overflow:hidden; }}
.nv-thanh span {{ display:block; height:100%; background:linear-gradient(90deg,#9BE07F,#2F7A24); border-radius:999px; }}
.kho {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }}
.kho-o {{ text-align:center; background:#FBF8F4; border-radius:14px; padding:10px 4px; }}
.kho-bt {{ font-size:1.5rem; display:block; }} .kho-o b {{ display:block; font-size:1.2rem; color:{CHU}; }}
.kho-o span:last-child {{ font-size:.75rem; color:{CHU_PHU}; }}
.st-key-khung_doan_gia {{ background:linear-gradient(135deg,#F3F8FF,#FFFFFF); border:1px solid #DCE8FB; border-radius:20px;
    padding:16px 18px !important; margin-bottom:12px; animation:nt-len .6s ease .2s backwards; }}
.st-key-khung_doan_gia [class*="st-key-doan_"] button {{ border-radius:12px !important; min-height:40px; }}
.st-key-khung_doan_gia .st-key-doan_tang button {{ background:#E7F6EC !important; border:1.5px solid #9ED8AE !important; }}
.st-key-khung_doan_gia .st-key-doan_tang button p {{ color:{TANG} !important; font-weight:800 !important; }}
.st-key-khung_doan_gia .st-key-doan_giam button {{ background:#FDECEC !important; border:1.5px solid #F2B5B5 !important; }}
.st-key-khung_doan_gia .st-key-doan_giam button p {{ color:{GIAM} !important; font-weight:800 !important; }}
.st-key-khung_doan_gia .st-key-doan_ngang button {{ background:#F3EEE9 !important; border:1.5px solid #DCD0C4 !important; }}
.st-key-khung_doan_gia .st-key-doan_ngang button p {{ font-weight:800 !important; }}
.dd-ls {{ margin-top:8px; }} .dd-dong {{ display:flex; justify-content:space-between; gap:8px; font-size:.85rem; padding:5px 0;
    border-top:1px dashed #DCE8FB; }}
.dd-dong .dung {{ color:{TANG}; }} .dd-dong .sai {{ color:{GIAM}; }} .dd-dong .cho {{ color:{CHU_PHU}; font-weight:600; }}

/* xu bay + pháo giấy */
.xu-bay {{ position:fixed; left:50%; top:45%; z-index:999999; display:flex; align-items:center; gap:10px; padding:12px 22px;
    border-radius:999px; background:#fff; font-size:1.4rem; font-weight:900; color:#B26B00; pointer-events:none;
    box-shadow:0 16px 40px -10px rgba(168,101,14,.6); animation:xu-len 2.2s cubic-bezier(.2,.8,.2,1) forwards; }}
.xu-bay .dong-xu {{ width:38px; height:38px; font-size:.8rem; }}
.phao-giay {{ position:fixed; inset:0 0 auto 0; height:0; z-index:999998; pointer-events:none; }}
.phao-giay i {{ position:absolute; top:22vh; width:9px; height:14px; border-radius:2px; opacity:0; animation:giay-roi 1.8s ease-in forwards; }}
@media (prefers-reduced-motion: reduce) {{ .st-key-trang_nong_trai *, .nt-dau * {{ animation:none !important; }} }}
</style>""")


# Biểu tượng vẽ riêng cho 3 cây (hồ tiêu là chùm hạt tiêu, không phải quả ớt)
ICON_CAY = {
    "lua": ('<svg viewBox="0 0 48 48" class="icon-cay"><path d="M22 46 C22 32 20 20 14 8" stroke="#7DA83A" stroke-width="3" '
            'fill="none" stroke-linecap="round"/><path d="M22 40 C30 34 36 30 42 30 C36 36 30 40 22 42Z" fill="#8CC24A"/>'
            + "".join(f'<ellipse cx="{x}" cy="{y}" rx="3" ry="4.6" fill="#F0B429" stroke="#C98A12" stroke-width="1" '
                      f'transform="rotate({r} {x} {y})"/>'
                      for x, y, r in [(13, 8, -20), (18, 11, 30), (11, 14, -30), (19, 17, 30), (14, 20, -30),
                                      (21, 23, 30), (16, 26, -25)]) + '</svg>'),
    "ho_tieu": ('<svg viewBox="0 0 48 48" class="icon-cay"><path d="M30 4 C26 10 26 14 24 20" stroke="#5E8C2E" stroke-width="2.6" '
                'fill="none" stroke-linecap="round"/><path d="M30 6 C38 4 45 8 46 16 C38 18 32 14 30 6Z" fill="#4FA83A"/>'
                '<path d="M36 9 C40 10 43 12 44 15" stroke="#2F7A24" stroke-width="1.2" fill="none"/>'
                '<path d="M24 18 C22 26 20 34 18 44" stroke="#5E8C2E" stroke-width="2" fill="none" stroke-linecap="round"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="3.3" fill="{m}"/><circle cx="{x - 1}" cy="{y - 1.1}" r="1" fill="#FFFFFF" '
                          f'opacity=".55"/>' for x, y, m in [(26, 20, "#3E9B2F"), (20, 22, "#4FA83A"), (25, 26, "#6B8E23"),
                                                           (19, 28, "#C0392B"), (24, 32, "#A93226"), (18, 34, "#7B241C"),
                                                           (22, 38, "#4A2511"), (17, 40, "#2E1A0E"), (21, 44, "#2E1A0E")])
                + '</svg>'),
    "ca_phe": ('<svg viewBox="0 0 48 48" class="icon-cay"><g transform="rotate(-28 17 25)"><ellipse cx="17" cy="25" rx="10" ry="14" '
               'fill="#7A4A26"/><ellipse cx="15" cy="21" rx="4" ry="6" fill="#9C6436" opacity=".6"/><path d="M17 12 C12 20 22 30 17 38" '
               'stroke="#3E2210" stroke-width="2.4" fill="none" stroke-linecap="round"/></g><g transform="rotate(24 32 25)">'
               '<ellipse cx="32" cy="25" rx="10" ry="14" fill="#8B5530"/><ellipse cx="30" cy="21" rx="4" ry="6" fill="#B07443" '
               'opacity=".6"/><path d="M32 12 C27 20 37 30 32 38" stroke="#3E2210" stroke-width="2.4" fill="none" '
               'stroke-linecap="round"/></g></svg>'),
}


def _uri_icon(ma: str) -> str:
    from urllib.parse import quote
    svg = ICON_CAY[ma].replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1).replace(' class="icon-cay"', "")
    return 'url("data:image/svg+xml;utf8,' + quote(svg) + '")'


# ================================================================ NÔNG TRẠI: KHUNG CẢNH CHUNG 3 LUỐNG
_COI_XAY = ('<svg class="coi-xay" viewBox="0 0 80 110"><path d="M30 108 L36 40 H44 L50 108Z" fill="#F4E6D0" stroke="#C9A77A" '
            'stroke-width="2"/><path d="M33 40 L40 28 L47 40Z" fill="#D9643A"/><rect x="36" y="80" width="8" height="14" rx="2" '
            'fill="#9C6B3E"/><g class="canh-quat" style="transform-origin:40px 36px">'
            + "".join(f'<rect x="38" y="4" width="4" height="32" rx="2" fill="#FFFFFF" stroke="#C9A77A" '
                      f'transform="rotate({g} 40 36)"/>' for g in (0, 90, 180, 270)) + '<circle cx="40" cy="36" r="4" fill="#9C6B3E"/></g></svg>')
_HANG_RAO = ('<svg class="hang-rao" viewBox="0 0 200 70" preserveAspectRatio="none">'
             + "".join(f'<path d="M{x} 70 V14 l7 -9 l7 9 V70Z" fill="#E7C89A" stroke="#A97B47" stroke-width="2"/>'
                       for x in range(6, 200, 32))
             + '<rect x="0" y="26" width="200" height="8" rx="3" fill="#D4AE78" stroke="#A97B47" stroke-width="2"/>'
             '<rect x="0" y="48" width="200" height="8" rx="3" fill="#D4AE78" stroke="#A97B47" stroke-width="2"/></svg>')
_BINH_TUOI = ('<div class="binh-tuoi"><svg viewBox="0 0 90 60"><path d="M18 18 h40 a6 6 0 0 1 6 6 v24 a6 6 0 0 1 -6 6 h-40 '
              'a6 6 0 0 1 -6 -6 v-24 a6 6 0 0 1 6 -6z" fill="#4DA3FF"/><path d="M64 26 L86 14 L88 20 L66 36Z" fill="#2F7FD6"/>'
              '<path d="M24 18 a14 12 0 0 1 28 0" fill="none" stroke="#2F7FD6" stroke-width="5"/></svg>'
              + "".join(f'<i style="left:{x}px;animation-delay:{d}s"></i>' for x, d in
                        [(70, 0), (78, .15), (86, .3), (74, .45), (82, .6), (90, .75), (76, .9)]) + "</div>")


# Gà mẹ, gà con, bướm vẽ bằng SVG (emoji 🐔 trên Windows chỉ có cái đầu)
_GA_ME = '<svg viewBox="0 0 120 110" class="svg-ga"><defs><radialGradient id="gaThan" cx="45%" cy="35%" r="70%"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#FBF3E6"/><stop offset="1" stop-color="#E9D6B8"/></radialGradient><linearGradient id="gaDuoi" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#C8642A"/><stop offset="1" stop-color="#8A3B16"/></linearGradient><linearGradient id="gaCanh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3E3C8"/><stop offset="1" stop-color="#D9BC92"/></linearGradient><linearGradient id="gaMao" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF5A4E"/><stop offset="1" stop-color="#D42A22"/></linearGradient></defs><ellipse cx="60" cy="104" rx="30" ry="4" fill="rgba(40,70,20,.25)"/><g class="chan"><g class="c-trai"><path d="M52 84 L50 100" stroke="#F0A030" stroke-width="4" stroke-linecap="round"/><path d="M50 100 l-7 2 M50 100 l1 4 M50 100 l6 1" stroke="#F0A030" stroke-width="3" stroke-linecap="round"/></g><g class="c-phai"><path d="M66 84 L68 100" stroke="#E08E22" stroke-width="4" stroke-linecap="round"/><path d="M68 100 l-6 2 M68 100 l1 4 M68 100 l7 1" stroke="#E08E22" stroke-width="3" stroke-linecap="round"/></g></g><g class="than"><path d="M30 56 C14 46 8 26 18 14 C20 26 26 32 32 36 C26 22 30 8 42 4 C38 18 40 30 44 38 C44 28 50 20 58 20 C50 30 50 42 52 50Z" fill="url(#gaDuoi)"/><path d="M24 22 C24 30 28 36 33 40 M38 12 C36 22 38 30 42 38" stroke="#6E2C0E" stroke-width="1.2" fill="none" opacity=".5"/><path d="M28 58 C30 44 46 40 64 42 C68 32 70 20 82 16 C94 14 100 24 98 34 C97 40 94 44 92 48 C102 56 102 74 90 84 C78 92 50 92 38 84 C28 78 26 66 28 58Z" fill="url(#gaThan)" stroke="#CDB894" stroke-width="1.6"/><path class="canh" d="M40 60 C46 50 64 50 72 58 C76 66 72 76 62 78 C52 80 42 74 40 60Z" fill="url(#gaCanh)" stroke="#C4A57A" stroke-width="1.4"/><path d="M46 64 C52 68 60 68 68 64 M48 70 C54 74 62 74 68 70" stroke="#B8966A" stroke-width="1.3" fill="none" stroke-linecap="round"/><path d="M74 76 C80 74 86 70 88 64" stroke="#E6D3B4" stroke-width="2" fill="none" stroke-linecap="round"/></g><g class="dau"><path d="M78 18 C77 8 83 5 85 11 C86 3 93 3 93 11 C96 5 102 9 98 16 C94 18 84 20 78 18Z" fill="url(#gaMao)"/><path d="M97 26 L110 29 L97 33Z" fill="#FFB52E"/><path d="M97 30 L107 31 L97 33Z" fill="#E8901A"/><path d="M95 34 C99 36 99 44 95 45 C91 44 91 37 95 34Z" fill="url(#gaMao)"/><circle cx="89" cy="25" r="3.4" fill="#2A1A10"/><circle cx="90.2" cy="23.8" r="1.2" fill="#FFFFFF"/><ellipse cx="86" cy="32" rx="3.4" ry="2" fill="#FF8C8C" opacity=".55"/></g></svg>'
_GA_CON = '<svg viewBox="0 0 60 56" class="svg-ga-con"><defs><radialGradient id="gaCon" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#FFF6A8"/><stop offset=".55" stop-color="#FFDB4D"/><stop offset="1" stop-color="#F2B419"/></radialGradient></defs><ellipse cx="28" cy="53" rx="15" ry="2.6" fill="rgba(40,70,20,.22)"/><g class="chan"><path class="c-trai" d="M24 44 V51 l-4 1 M24 51 l3 1" stroke="#F09A2A" stroke-width="2.4" stroke-linecap="round" fill="none"/><path class="c-phai" d="M32 44 V51 l-3 1 M32 51 l4 1" stroke="#E08A1E" stroke-width="2.4" stroke-linecap="round" fill="none"/></g><g class="than"><path d="M8 32 C8 20 18 14 28 16 C30 10 36 6 42 8 C52 10 54 22 48 28 C52 40 42 48 28 47 C16 47 8 42 8 32Z" fill="url(#gaCon)"/><path d="M8 30 L2 26 L7 34Z" fill="#F2B419"/><path d="M16 32 C20 26 30 28 30 34 C26 40 18 38 16 32Z" fill="#F5C531" opacity=".85"/></g><g class="dau"><path d="M38 8 C37 3 41 1 42 5 C43 1 47 2 45 7" stroke="#F2B419" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M50 17 L57 19 L50 22Z" fill="#FF9F1C"/><circle cx="45" cy="15" r="2.4" fill="#2A1A10"/><circle cx="45.9" cy="14.2" r=".9" fill="#fff"/><ellipse cx="44" cy="21" rx="2.6" ry="1.5" fill="#FF8C8C" opacity=".6"/></g></svg>'
_BUOM = '<svg viewBox="0 0 64 52" class="svg-buom"><defs><linearGradient id="buomTren" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFB347"/><stop offset="1" stop-color="#FF6B3D"/></linearGradient><linearGradient id="buomDuoi" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFD166"/><stop offset="1" stop-color="#FF9F45"/></linearGradient></defs><g class="canh-t"><path d="M31 22 C26 8 14 0 5 4 C-1 8 2 20 10 24 C16 27 25 26 31 23Z" fill="url(#buomTren)" stroke="#3A2010" stroke-width="2"/><path d="M31 25 C22 26 12 32 13 40 C14 47 22 48 27 42 C30 38 31 31 31 25Z" fill="url(#buomDuoi)" stroke="#3A2010" stroke-width="2"/><path d="M30 22 C22 16 14 10 8 8 M30 23 C22 20 14 19 7 18 M30 26 C24 30 19 35 17 41" stroke="#3A2010" stroke-width=".9" fill="none" opacity=".7"/><circle cx="7" cy="9" r="1.6" fill="#fff"/><circle cx="4.5" cy="14" r="1.3" fill="#fff"/><circle cx="16" cy="42" r="1.3" fill="#fff"/></g><g class="canh-p"><path d="M33 22 C38 8 50 0 59 4 C65 8 62 20 54 24 C48 27 39 26 33 23Z" fill="url(#buomTren)" stroke="#3A2010" stroke-width="2"/><path d="M33 25 C42 26 52 32 51 40 C50 47 42 48 37 42 C34 38 33 31 33 25Z" fill="url(#buomDuoi)" stroke="#3A2010" stroke-width="2"/><path d="M34 22 C42 16 50 10 56 8 M34 23 C42 20 50 19 57 18 M34 26 C40 30 45 35 47 41" stroke="#3A2010" stroke-width=".9" fill="none" opacity=".7"/><circle cx="57" cy="9" r="1.6" fill="#fff"/><circle cx="59.5" cy="14" r="1.3" fill="#fff"/><circle cx="48" cy="42" r="1.3" fill="#fff"/></g><ellipse cx="32" cy="27" rx="2.6" ry="12" fill="#3A2010"/><circle cx="32" cy="14" r="3" fill="#3A2010"/><path d="M31 12 C29 6 26 3 23 2 M33 12 C35 6 38 3 41 2" stroke="#3A2010" stroke-width="1.2" fill="none" stroke-linecap="round"/><circle cx="23" cy="2.2" r="1.5" fill="#3A2010"/><circle cx="41" cy="2.2" r="1.5" fill="#3A2010"/></svg>'

_NHA_KHO = ('<svg class="nha-kho" viewBox="0 0 120 96"><path d="M8 44 L60 10 L112 44 V92 H8Z" fill="#D9483B"/>'
            '<path d="M2 46 L60 6 L118 46" fill="none" stroke="#F4F0E6" stroke-width="7" stroke-linejoin="round"/>'
            '<rect x="40" y="52" width="40" height="40" fill="#A8322A" stroke="#F4F0E6" stroke-width="4"/>'
            '<path d="M40 52 L80 92 M80 52 L40 92" stroke="#F4F0E6" stroke-width="3.5"/>'
            '<rect x="50" y="24" width="20" height="16" rx="2" fill="#FFF3C4" stroke="#F4F0E6" stroke-width="3"/></svg>')
_CAY_TO = ('<svg class="cay-to" viewBox="0 0 100 120"><rect x="44" y="64" width="12" height="54" rx="5" fill="#8B5A2B"/>'
           '<g class="tan"><circle cx="50" cy="44" r="30" fill="#4FA83A"/><circle cx="28" cy="58" r="20" fill="#3E9B2F"/>'
           '<circle cx="72" cy="58" r="20" fill="#3E9B2F"/><circle cx="42" cy="34" r="14" fill="#6CCB52"/>'
           '<circle cx="36" cy="54" r="3.4" fill="#E8463A"/><circle cx="64" cy="40" r="3.4" fill="#E8463A"/>'
           '<circle cx="58" cy="62" r="3.4" fill="#E8463A"/></g></svg>')
_PHAN_HOA = '<div class="phan-hoa">' + "".join(
    f'<i style="left:{x}%;animation-delay:{d}s;animation-duration:{t}s"></i>'
    for x, d, t in [(6, 0, 9), (17, -3, 11), (29, -6, 8), (41, -1, 10), (53, -4, 12), (66, -7, 9), (78, -2, 11),
                    (89, -5, 10), (35, -8, 13), (72, -9, 12)]) + '</div>'
_HOA_CO = '<div class="hoa-co">' + "".join(
    f'<span class="{"hoa" if i % 3 else "nhanh-co"}" style="left:{x}%;animation-delay:{-i * .37:.2f}s">'
    f'{["🌿", "🌼", "🌸", "🌿", "🌼", "🌷"][i % 6] if i % 3 else ""}</span>'
    for i, x in enumerate([1, 4, 8, 31.5, 33, 35, 64.5, 66, 68, 96, 98.5])) + '</div>'
_LAP_DAT = "".join(f'<span class="lap-dat" style="left:{x}%;animation-delay:{d}s"></span>'
                   for x, d in [(26, 0), (48, .7), (70, 1.4), (38, 2.1), (60, 2.8)])


def _thoi_gian(giay: int) -> str:
    if giay <= 0:
        return "0 phút"
    gio, phut = divmod(max(int(giay) // 60, 1), 60)
    return (f"{gio} giờ " if gio else "") + (f"{phut} phút" if phut or not gio else "")


def canh_nong_trai(cac_o: list, cay_info: dict, giai_doan_ten: list, ng: dict, xu_thu: int, tran_xu: int,
                   so_o: int, vua_tuoi: int = None, dang_chon: int = None) -> str:
    """Khung cảnh nông trại: trời, đồi, cối xay gió + 3 luống đất (trái · giữa · phải)."""
    luong = []
    for d in cac_o:
        vt = d["vi_tri"]
        if not d["mo"]:
            goi = "VIP Mùa Vàng" if vt == 1 else "VIP Bội Thu"
            luong.append(f'<div class="luong khoa"><div class="chip-tt khoa">🔒 Mở bằng {e(goi)}</div>'
                         f'<div class="cay-o"></div><div class="dat"></div>{_HANG_RAO}'
                         f'<div class="nhan-luong"><b>Luống {"trái" if vt == 1 else "phải"}</b><span>Đang khoá</span></div></div>')
            continue
        if not d["cay"]:
            chon = dang_chon == vt
            chip = "" if chon else '<div class="chip-tt">🌱 Đất trống – bấm ＋ để gieo</div>'
            luong.append(f'<div class="luong trong {"dang-chon" if chon else ""}">{chip}'
                         f'<div class="cay-o"></div><div class="dat">{_LAP_DAT}</div>'
                         f'<div class="nhan-luong"><b>{"Luống giữa" if vt == 0 else ("Luống trái" if vt == 1 else "Luống phải")}'
                         f'</b><span>Sẵn sàng gieo</span></div></div>')
            continue
        c = cay_info[d["cay"]]
        chin = d["giai_doan"] == 3
        if chin:
            chip = '<div class="chip-tt chin">✨ Chín rồi – thu hoạch!</div>'
        else:
            chip = f'<div class="chip-tt">⏳ Còn {_thoi_gian(d["con_lai_giay"])}</div>'
        giot = "".join(f'<span class="giot-tuoi" style="left:{x}%"></span>' for x in (40, 52, 62)) if d["da_tuoi"] else ""
        tuoi = _BINH_TUOI if vua_tuoi == vt else ""
        lap = ('<span class="lap l1">✦</span><span class="lap l2">✦</span><span class="lap l3">✦</span>'
               '<span class="ong o1">🐝</span><span class="ong o2">🐝</span>' if chin else "")
        nuoc = "".join('<span class="vet-nuoc"></span>' for _ in range(d["da_tuoi"]))
        luong.append(f'<div class="luong {"chin" if chin else ""} {"am" if d["da_tuoi"] else ""}">{chip}'
                     f'<div class="cay-o">{_svg_cay(d["cay"], d["giai_doan"])}{lap}{tuoi}</div>'
                     f'<div class="dat">{giot}</div>'
                     f'<div class="nhan-luong"><b>{ICON_CAY[d["cay"]]} {e(c["ten"])}</b><span>{e(giai_doan_ten[d["giai_doan"]])}</span>'
                     f'<div class="thanh-luong"><i style="width:{d["tien_do"] * 100:.0f}%"></i></div>'
                     f'<div class="so-lan-tuoi">💧 {d["da_tuoi"]}/3 lần tưới{nuoc}</div></div></div>')
    pt = 100 if ng["cap_toi_da"] else ng["kn_trong_cap"] / max(ng["kn_can"], 1) * 100
    from datetime import datetime, timedelta, timezone
    gio_vn = (datetime.now(timezone.utc) + timedelta(hours=7)).hour      # giờ Việt Nam
    buoi = "sang" if 5 <= gio_vn < 8 else ("ngay" if gio_vn < 17 else ("chieu" if gio_vn < 19 else "dem"))
    if gio_vn < 5:
        buoi = "dem"
    sao = "".join(f'<i style="left:{x}%;top:{y}px;animation-delay:{d}s"></i>' for x, y, d in
                  [(8, 30, 0), (22, 70, 1.1), (35, 24, .5), (47, 90, 1.7), (58, 40, .9), (68, 110, 2.2), (78, 20, 1.4),
                   (88, 60, .3), (15, 120, 2.6), (52, 14, 1.9), (40, 130, .7), (94, 140, 2.9)])
    return gon(f'''<div class="nt-canh {buoi}">
      <div class="sao">{sao}</div><div class="mat-trang"></div>
      <div class="troi"><div class="mat-troi"><i></i></div>
        <div class="may m1"></div><div class="may m2"></div><div class="may m3"></div>
        <span class="chim c1">〰</span><span class="chim c2">〰</span></div>
      <div class="cau-vong"></div>
      <svg class="doi xa" viewBox="0 0 1200 220" preserveAspectRatio="none">
        <path d="M0 90 C160 30 300 70 460 60 C640 46 760 0 940 40 C1060 66 1140 40 1200 50 V220 H0Z" fill="#CDEBB4"/></svg>
      <svg class="doi" viewBox="0 0 1200 220" preserveAspectRatio="none">
        <path d="M0 120 C200 40 360 60 520 110 C700 165 860 50 1200 90 V220 H0Z" fill="#B7E39A"/>
        <path d="M0 160 C240 100 420 140 640 150 C860 160 980 110 1200 140 V220 H0Z" fill="#9AD67C"/></svg>
      {_COI_XAY}{_NHA_KHO}{_CAY_TO}
      <div class="co"></div><div class="bong-may"></div><div class="bong-may b2"></div>
      <span class="buom b1">{_BUOM}</span><span class="buom b2">{_BUOM}</span><span class="buom b3">{_BUOM}</span>
      <span class="la-roi l1"></span><span class="la-roi l2"></span><span class="la-roi l3"></span>
      <div class="dan-ga"><span class="ga">{_GA_ME}</span><span class="ga con c1">{_GA_CON}</span>
        <span class="ga con c2">{_GA_CON}</span></div>
      {_PHAN_HOA}{_HOA_CO}
      <div class="bien-go"><span class="loe"><i></i></span><div class="bg-td">Nông Trại Bồ Nông</div>
        <div class="bg-cap"><span class="cap">Cấp {ng["cap"]}</span><div class="kn"><i style="width:{pt:.0f}%"></i></div>
        <span class="kn-chu">{"Tối đa" if ng["cap_toi_da"] else f'{ng["kn_trong_cap"]}/{ng["kn_can"]} KN'}</span></div></div>
      <div class="bong-so"><div><b>{xu_thu}/{tran_xu}</b><span>xu thu hoạch hôm nay</span></div>
        <div><b>{so_o}/3</b><span>luống đang mở</span></div></div>
      <div class="hang-luong">{"".join(luong)}</div>
    </div>''')


def css_canh_nong_trai() -> str:
    return gon(f"""
<style>
@keyframes nt-xoay {{ to {{ transform:rotate(360deg); }} }}
@keyframes nt-may {{ from {{ transform:translateX(-60px); }} to {{ transform:translateX(60px); }} }}
@keyframes nt-chim {{ 0% {{ transform:translate(0,0); }} 50% {{ transform:translate(140px,-14px); }} 100% {{ transform:translate(280px,4px); opacity:0; }} }}
@keyframes nt-buom {{ 0% {{ transform:translate(0,0) rotate(-8deg); }} 25% {{ transform:translate(90px,-40px) rotate(10deg); }}
    50% {{ transform:translate(200px,-10px) rotate(-6deg); }} 75% {{ transform:translate(120px,-60px) rotate(8deg); }}
    100% {{ transform:translate(0,0) rotate(-8deg); }} }}
@keyframes nt-tia {{ 0%,100% {{ box-shadow:0 0 40px 16px rgba(255,220,100,.55); }} 50% {{ box-shadow:0 0 60px 26px rgba(255,220,100,.75); }} }}
@keyframes nt-dua {{ 0%,100% {{ transform:rotate(-2.5deg); }} 50% {{ transform:rotate(2.5deg); }} }}
@keyframes nt-lap {{ 0%,100% {{ opacity:0; transform:scale(.4) rotate(0); }} 50% {{ opacity:1; transform:scale(1.15) rotate(90deg); }} }}
@keyframes nt-sang {{ 0%,100% {{ filter:drop-shadow(0 0 0 rgba(255,200,60,0)); }} 50% {{ filter:drop-shadow(0 0 14px rgba(255,200,60,.9)); }} }}
@keyframes nt-giot {{ 0% {{ transform:translateY(-6px); opacity:0; }} 40% {{ opacity:.9; }} 100% {{ transform:translateY(16px); opacity:0; }} }}
@keyframes nt-binh {{ 0% {{ opacity:0; transform:translate(30px,-20px) rotate(0deg); }} 15% {{ opacity:1; transform:translate(0,0) rotate(-28deg); }}
    80% {{ opacity:1; transform:translate(0,0) rotate(-28deg); }} 100% {{ opacity:0; transform:translate(20px,-14px) rotate(0); }} }}
@keyframes nt-mua {{ 0% {{ transform:translateY(0); opacity:0; }} 20% {{ opacity:1; }} 100% {{ transform:translateY(90px); opacity:0; }} }}
@keyframes nt-nhip {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.08); }} }}

.nt-canh {{ position:relative; height:560px; border-radius:30px; overflow:hidden; margin:.6rem 0 0;
    background:linear-gradient(180deg,#7CC8FF 0%,#B9E4FF 38%,#E6F7FF 56%);
    box-shadow:0 26px 50px -28px rgba(31,74,22,.7), inset 0 0 0 1px rgba(255,255,255,.4); }}
.nt-canh .troi {{ position:absolute; inset:0; }}
.nt-canh .mat-troi {{ position:absolute; right:70px; top:34px; width:70px; height:70px; border-radius:50%;
    background:radial-gradient(circle,#FFF7C2 0%,#FFD95A 70%); animation:nt-tia 4s ease-in-out infinite; }}
.nt-canh .mat-troi i {{ position:absolute; inset:-26px; border-radius:50%;
    background:repeating-conic-gradient(rgba(255,226,120,.55) 0 10deg, transparent 10deg 30deg); animation:nt-xoay 30s linear infinite;
    -webkit-mask:radial-gradient(circle, transparent 38px, #000 39px); mask:radial-gradient(circle, transparent 38px, #000 39px); }}
.nt-canh .may {{ position:absolute; height:30px; border-radius:30px; background:#fff; opacity:.92; animation:nt-may 14s ease-in-out infinite alternate; }}
.nt-canh .may:before, .nt-canh .may:after {{ content:""; position:absolute; background:#fff; border-radius:50%; }}
.nt-canh .may.m1 {{ width:110px; left:30%; top:40px; }} .nt-canh .may.m1:before {{ width:52px; height:52px; left:18px; top:-26px; }}
.nt-canh .may.m1:after {{ width:38px; height:38px; left:58px; top:-16px; }}
.nt-canh .may.m2 {{ width:80px; left:56%; top:92px; opacity:.8; animation-duration:18s; }}
.nt-canh .may.m2:before {{ width:36px; height:36px; left:14px; top:-18px; }}
.nt-canh .may.m3 {{ width:70px; left:8%; top:120px; opacity:.7; animation-duration:22s; }}
.nt-canh .may.m3:before {{ width:30px; height:30px; left:12px; top:-14px; }}
.nt-canh .chim {{ position:absolute; color:#3C5A6E; font-size:14px; font-weight:900; animation:nt-chim 16s linear infinite; }}
.nt-canh .chim.c1 {{ left:18%; top:70px; }} .nt-canh .chim.c2 {{ left:22%; top:86px; animation-delay:1.2s; font-size:11px; }}
.nt-canh .doi {{ position:absolute; left:0; right:0; top:150px; width:100%; height:200px; }}
.nt-canh .coi-xay {{ position:absolute; left:5%; top:150px; width:62px; height:86px; }}
.nt-canh .canh-quat {{ animation:nt-xoay 6s linear infinite; }}
.nt-canh .co {{ position:absolute; left:0; right:0; bottom:0; height:250px;
    background:linear-gradient(180deg,#8ED166 0%,#6DBB45 100%); }}
.nt-canh .co:before {{ content:""; position:absolute; inset:0; opacity:.25;
    background:repeating-linear-gradient(100deg, transparent 0 14px, rgba(255,255,255,.35) 14px 16px); }}
.nt-canh .buom {{ position:absolute; font-size:20px; animation:nt-buom 12s ease-in-out infinite; z-index:3; }}
.nt-canh .buom.b1 {{ left:12%; top:300px; }} .nt-canh .buom.b2 {{ left:62%; top:280px; animation-delay:-5s; font-size:16px; }}

/* biển gỗ + số liệu */
.nt-canh .bien-go {{ position:absolute; left:24px; top:22px; z-index:4; padding:14px 20px 14px; border-radius:16px;
    background:linear-gradient(180deg,#E9C48E,#D3A464); border:3px solid #A8743D; box-shadow:0 10px 20px -10px rgba(80,40,10,.6);
    color:#4A2C10; min-width:300px; }}
.nt-canh .bien-go:before, .nt-canh .bien-go:after {{ content:""; position:absolute; top:100%; width:8px; height:30px; background:#A8743D; }}
.nt-canh .bien-go:before {{ left:30px; }} .nt-canh .bien-go:after {{ right:30px; }}
.nt-canh .bg-td {{ font-family:'Noto Serif', Georgia, serif; font-size:1.55rem; font-weight:800; letter-spacing:.01em; }}
.nt-canh .bg-cap {{ display:flex; align-items:center; gap:10px; margin-top:8px; }}
.nt-canh .bg-cap .cap {{ padding:3px 10px; border-radius:999px; font-weight:800; font-size:.8rem; color:#fff;
    background:linear-gradient(135deg,#6BCB52,#2F7A24); }}
.nt-canh .kn {{ flex:1; height:10px; border-radius:999px; background:rgba(255,255,255,.55); overflow:hidden; }}
.nt-canh .kn i {{ display:block; height:100%; background:linear-gradient(90deg,#FFE27A,#F2A93B); border-radius:999px; }}
.nt-canh .kn-chu {{ font-size:.75rem; font-weight:800; }}
.nt-canh .bong-so {{ position:absolute; right:170px; top:28px; z-index:4; display:flex; gap:10px; }}
.nt-canh .bong-so div {{ background:rgba(255,255,255,.88); border-radius:16px; padding:8px 14px; text-align:center;
    box-shadow:0 8px 18px -10px rgba(30,60,80,.5); backdrop-filter:blur(4px); }}
.nt-canh .bong-so b {{ display:block; font-size:1.25rem; color:#1F4A16; }} .nt-canh .bong-so span {{ font-size:.72rem; color:#4E5E48; }}

/* 3 luống */
.nt-canh .hang-luong {{ position:absolute; left:0; right:0; bottom:16px; z-index:2; display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; padding:0 6px; }}
.luong {{ position:relative; height:320px; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; }}
.luong .chip-tt {{ position:absolute; top:0; left:50%; transform:translateX(-50%); white-space:nowrap; z-index:4;
    padding:6px 14px; border-radius:999px; font-size:.82rem; font-weight:800; color:#2F4A1F;
    background:rgba(255,255,255,.92); box-shadow:0 8px 18px -10px rgba(30,60,30,.55); }}
.luong .chip-tt.chin {{ color:#9A5A00; background:linear-gradient(135deg,#FFF3C4,#FFD970); animation:nt-nhip 1.6s ease-in-out infinite; }}
.luong .chip-tt.khoa {{ color:#7A4B00; background:linear-gradient(135deg,#FFF6DD,#FBE3A6); }}
.luong .cay-o {{ position:relative; z-index:3; width:100%; height:180px; display:flex; justify-content:center; align-items:flex-end;
    margin-bottom:-30px; }}
.luong .hinh-cay {{ width:190px; height:176px; transform-origin:50% 92%; animation:nt-dua 3.6s ease-in-out infinite; }}
.luong.chin .hinh-cay {{ animation:nt-dua 3.6s ease-in-out infinite, nt-sang 2s ease-in-out infinite; }}
.luong img.hinh-cay.anh-that {{ width:auto; height:200px; max-width:96%; object-fit:contain; object-position:50% 100%;
    margin-bottom:6px; filter:drop-shadow(0 6px 6px rgba(40,25,10,.35)); }}
.luong img.hinh-cay.anh-that.cay-ho_tieu {{ height:236px; }}
.luong img.hinh-cay.anh-that.cay-lua {{ height:190px; }}
.luong.chin img.hinh-cay.anh-that {{ animation:nt-dua 3.6s ease-in-out infinite, nt-sang 2s ease-in-out infinite; }}
.luong .dat {{ position:relative; z-index:2; width:88%; height:70px; border-radius:50% / 46%;
    background:radial-gradient(ellipse at 50% 35%, #A97A4C 0%, #845630 60%, #5F3B1D 100%);
    box-shadow:0 14px 18px -10px rgba(40,20,5,.6), inset 0 -6px 10px rgba(0,0,0,.25); overflow:hidden; }}
.luong .dat:before {{ content:""; position:absolute; inset:16px 26px; border-radius:50%;
    background:repeating-linear-gradient(0deg, transparent 0 9px, rgba(255,255,255,.12) 9px 11px); }}
.luong.am .dat {{ background:radial-gradient(ellipse at 50% 35%, #8C5F38 0%, #6A4223 60%, #4A2C14 100%); }}
.giot-tuoi {{ position:absolute; top:18px; width:6px; height:9px; border-radius:50% 50% 50% 50% / 65% 65% 35% 35%;
    background:#8FD0FF; animation:nt-giot 2.2s ease-in infinite; }}
.giot-tuoi:nth-child(2) {{ animation-delay:.7s; }} .giot-tuoi:nth-child(3) {{ animation-delay:1.4s; }}
.luong .nhan-luong {{ position:relative; z-index:3; margin-top:10px; width:84%; text-align:center; padding:8px 12px 9px;
    border-radius:16px; background:rgba(255,255,255,.92); box-shadow:0 10px 20px -14px rgba(30,60,30,.6); }}
.luong .nhan-luong b {{ display:block; color:{CHU}; font-size:.95rem; }}
.luong .nhan-luong > span {{ font-size:.78rem; color:{CHU_PHU}; }}
.thanh-luong {{ height:8px; margin-top:6px; border-radius:999px; background:#EDF2E6; overflow:hidden; }}
.thanh-luong i {{ display:block; height:100%; border-radius:999px; background:linear-gradient(90deg,#9BE07F,#2F7A24); }}
.luong.chin .thanh-luong i {{ background:linear-gradient(90deg,#FFD65A,#E39B12); }}
.so-lan-tuoi {{ font-size:.72rem; color:#1D6FB8; font-weight:700; margin-top:4px; }}
.luong .lap {{ position:absolute; color:#FFC93C; font-size:20px; animation:nt-lap 2s ease-in-out infinite; }}
.luong .lap.l1 {{ left:22%; top:30px; }} .luong .lap.l2 {{ right:20%; top:60px; animation-delay:.6s; }}
.luong .lap.l3 {{ left:60%; top:14px; animation-delay:1.2s; font-size:14px; }}
.mam-cho {{ width:58px; height:58px; margin-bottom:46px; border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-size:2rem; font-weight:300; color:#fff; border:3px dashed rgba(255,255,255,.85); animation:nt-nhip 2s ease-in-out infinite; }}
.luong.khoa .dat {{ filter:grayscale(.8) brightness(1.05); opacity:.75; }}
.luong.khoa .hang-rao {{ position:absolute; bottom:56px; left:6%; width:88%; height:74px; z-index:4; }}
.luong.khoa .nhan-luong {{ opacity:.85; }}

/* bình tưới (chạy 1 lần sau khi bấm Tưới) */
.binh-tuoi {{ position:absolute; z-index:6; top:-6px; left:56%; width:96px; height:120px; pointer-events:none;
    transform-origin:20% 60%; animation:nt-binh 2.6s ease forwards; }}
.binh-tuoi svg {{ width:90px; height:60px; }}
.binh-tuoi i {{ position:absolute; top:30px; width:5px; height:9px; border-radius:50%; background:#6CC2FF;
    animation:nt-mua .9s linear 3; }}

/* ---- trang trí thêm ---- */
@keyframes nt-di {{ 0% {{ transform:translateX(0) scaleX(1); }} 45% {{ transform:translateX(240px) scaleX(1); }}
    50% {{ transform:translateX(240px) scaleX(-1); }} 95% {{ transform:translateX(0) scaleX(-1); }} 100% {{ transform:translateX(0) scaleX(1); }} }}
@keyframes nt-mo {{ 0%,100% {{ transform:translateY(0) rotate(0); }} 30% {{ transform:translateY(-2px) rotate(-14deg); }}
    60% {{ transform:translateY(0) rotate(4deg); }} }}
@keyframes nt-bay-len {{ 0% {{ transform:translate(0,0); opacity:0; }} 15% {{ opacity:.9; }}
    50% {{ transform:translate(18px,-130px); }} 100% {{ transform:translate(-10px,-280px); opacity:0; }} }}
@keyframes nt-lac {{ 0%,100% {{ transform:rotate(-7deg); }} 50% {{ transform:rotate(7deg); }} }}
@keyframes nt-ong {{ 0% {{ transform:rotate(0) translateX(46px) rotate(0); }} 100% {{ transform:rotate(360deg) translateX(46px) rotate(-360deg); }} }}
@keyframes nt-lap-dat {{ 0%,100% {{ opacity:0; transform:translateY(0) scale(.4); }} 50% {{ opacity:1; transform:translateY(-10px) scale(1); }} }}
@keyframes nt-loe {{ 0% {{ left:-40%; }} 60%,100% {{ left:130%; }} }}
@keyframes nt-noi {{ 0%,100% {{ transform:translate(-50%,0); }} 50% {{ transform:translate(-50%,-5px); }} }}
@keyframes nt-soc {{ from {{ background-position:0 0; }} to {{ background-position:28px 0; }} }}
@keyframes nt-hien {{ 0%,100% {{ opacity:.18; }} 50% {{ opacity:.42; }} }}
@keyframes nt-song {{ 0% {{ box-shadow:0 0 0 0 rgba(255,255,255,.85), 0 12px 26px -10px rgba(31,90,22,.8); }}
    70% {{ box-shadow:0 0 0 22px rgba(255,255,255,0), 0 12px 26px -10px rgba(31,90,22,.8); }}
    100% {{ box-shadow:0 0 0 0 rgba(255,255,255,0), 0 12px 26px -10px rgba(31,90,22,.8); }} }}
@keyframes nt-bat {{ 0% {{ opacity:0; transform:translateY(24px) scale(.85); }} 70% {{ opacity:1; transform:translateY(-4px) scale(1.02); }}
    100% {{ transform:translateY(0) scale(1); }} }}
@keyframes nt-nhun {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-1.5px); }} }}
@keyframes nt-buoc {{ 0%,100% {{ transform:rotate(14deg); }} 50% {{ transform:rotate(-14deg); }} }}
@keyframes nt-mo-ga {{ 0%,55%,100% {{ transform:rotate(0); }} 65% {{ transform:rotate(38deg); }} 72% {{ transform:rotate(18deg); }}
    80% {{ transform:rotate(38deg); }} 88% {{ transform:rotate(0); }} }}
@keyframes nt-vo-canh {{ 0%,80%,100% {{ transform:rotate(0); }} 85% {{ transform:rotate(-22deg); }} 90% {{ transform:rotate(0); }}
    95% {{ transform:rotate(-22deg); }} }}
@keyframes nt-dap {{ from {{ transform:scaleX(1); }} to {{ transform:scaleX(.35); }} }}
@keyframes nt-bong {{ from {{ transform:translateX(0); }} to {{ transform:translateX(1700px); }} }}
@keyframes nt-la {{ 0% {{ opacity:0; transform:translate(0,0) rotate(0); }} 10% {{ opacity:1; }}
    50% {{ transform:translate(26px,70px) rotate(200deg); }} 90% {{ opacity:1; }} 100% {{ opacity:0; transform:translate(-8px,150px) rotate(420deg); }} }}
@keyframes nt-nhay {{ 0%,100% {{ opacity:.25; transform:scale(.7); }} 50% {{ opacity:1; transform:scale(1.2); }} }}
@keyframes nt-hat-lac {{ 0%,100% {{ transform:rotate(0); }} 25% {{ transform:rotate(-12deg); }} 75% {{ transform:rotate(12deg); }} }}

.nt-canh .cau-vong {{ position:absolute; left:28%; top:96px; width:460px; height:230px; border-radius:460px 460px 0 0;
    background:radial-gradient(circle at 50% 100%, transparent 54%, rgba(255,90,90,.5) 55%, rgba(255,170,60,.5) 58%,
    rgba(255,230,90,.5) 61%, rgba(110,210,110,.5) 64%, rgba(90,170,255,.5) 67%, rgba(160,110,230,.5) 70%, transparent 71%);
    animation:nt-hien 9s ease-in-out infinite; pointer-events:none; }}
.nt-canh .doi.xa {{ top:118px; height:190px; }}
.nt-canh .nha-kho {{ position:absolute; right:1.2%; top:182px; width:84px; height:68px; z-index:1;
    filter:drop-shadow(0 8px 8px rgba(40,70,20,.35)); }}
.nt-canh .cay-to {{ position:absolute; left:13%; top:150px; width:78px; height:96px; z-index:1; }}
.nt-canh .cay-to .tan {{ transform-origin:50% 100%; animation:nt-dua 5s ease-in-out infinite; }}
.nt-canh .buom.b3 {{ left:84%; top:330px; animation-delay:-8s; font-size:15px; }}
.nt-canh .dan-ga {{ position:absolute; left:30%; top:252px; width:150px; height:60px; z-index:1; animation:nt-di 26s linear infinite; }}
.nt-canh .ga {{ position:absolute; left:0; top:0; }}
.nt-canh .svg-ga {{ width:78px; height:72px; display:block; filter:drop-shadow(0 4px 3px rgba(40,70,20,.3)); }}
.nt-canh .ga.con {{ top:40px; }} .nt-canh .ga.c1 {{ left:-34px; }} .nt-canh .ga.c2 {{ left:-66px; top:44px; }}
.nt-canh .svg-ga-con {{ width:34px; height:32px; display:block; }}
.nt-canh .ga .than {{ animation:nt-nhun .5s ease-in-out infinite; }}
.nt-canh .ga .c-trai {{ transform-origin:50% 0; transform-box:fill-box; animation:nt-buoc .5s ease-in-out infinite; }}
.nt-canh .ga .c-phai {{ transform-origin:50% 0; transform-box:fill-box; animation:nt-buoc .5s ease-in-out infinite reverse; }}
.nt-canh .svg-ga .dau {{ transform-origin:84px 42px; animation:nt-mo-ga 4s ease-in-out infinite; }}
.nt-canh .svg-ga-con .dau {{ transform-origin:40px 24px; animation:nt-mo-ga 3s ease-in-out infinite; }}
.nt-canh .ga.c2 .dau {{ animation-delay:-1.4s; }}
.nt-canh .svg-ga .canh {{ transform-origin:44px 60px; animation:nt-vo-canh 6s ease-in-out infinite; }}
.nt-canh .buom {{ animation:nt-buom 12s ease-in-out infinite; }}
.nt-canh .svg-buom {{ width:42px; height:34px; display:block; }}
.nt-canh .buom.b2 .svg-buom {{ width:34px; height:28px; filter:hue-rotate(160deg); }}
.nt-canh .buom.b3 .svg-buom {{ width:30px; height:24px; filter:hue-rotate(260deg); }}
.nt-canh .canh-t {{ transform-origin:32px 24px; animation:nt-dap .28s ease-in-out infinite alternate; }}
.nt-canh .canh-p {{ transform-origin:32px 24px; animation:nt-dap .28s ease-in-out infinite alternate; }}
.nt-canh .bong-may {{ position:absolute; left:-30%; top:360px; width:420px; height:110px; border-radius:50%; z-index:1;
    background:radial-gradient(ellipse, rgba(30,70,20,.16), transparent 70%); animation:nt-bong 40s linear infinite; pointer-events:none; }}
.nt-canh .bong-may.b2 {{ top:430px; width:300px; animation-duration:55s; animation-delay:-25s; }}
.nt-canh .la-roi {{ position:absolute; left:15%; top:190px; width:9px; height:6px; border-radius:0 80% 0 80%; z-index:2;
    background:#5DBB46; animation:nt-la 7s ease-in infinite; opacity:0; }}
.nt-canh .la-roi.l2 {{ left:17%; animation-delay:2.4s; background:#8CC24A; }}
.nt-canh .la-roi.l3 {{ left:14%; animation-delay:4.8s; background:#E3B23C; }}
/* buổi trong ngày theo giờ Việt Nam */
.nt-canh .sao, .nt-canh .mat-trang {{ display:none; }}
.nt-canh.sang {{ background:linear-gradient(180deg,#FFC8A8 0%,#FFE3C2 35%,#E8F6FF 58%); }}
.nt-canh.sang .mat-troi {{ right:auto; left:46%; top:118px; transform:scale(.85); }}
.nt-canh.chieu {{ background:linear-gradient(180deg,#5A6FC0 0%,#F4877A 34%,#FFC37A 56%); }}
.nt-canh.chieu .mat-troi {{ top:150px; right:22%; background:radial-gradient(circle,#FFE7B0 0%,#FF9A4A 70%); }}
.nt-canh.chieu .doi, .nt-canh.chieu .co, .nt-canh.chieu .cay-to, .nt-canh.chieu .nha-kho {{ filter:sepia(.25) saturate(1.15) brightness(.95); }}
.nt-canh.dem {{ background:linear-gradient(180deg,#0B1636 0%,#1D2E63 40%,#33497F 58%); }}
.nt-canh.dem .mat-troi, .nt-canh.dem .cau-vong, .nt-canh.dem .chim, .nt-canh.dem .buom {{ display:none; }}
.nt-canh.dem .may {{ opacity:.25; }}
.nt-canh.dem .doi, .nt-canh.dem .co, .nt-canh.dem .cay-to, .nt-canh.dem .nha-kho, .nt-canh.dem .coi-xay, .nt-canh.dem .dan-ga {{
    filter:brightness(.55) saturate(.8) hue-rotate(10deg); }}
.nt-canh.dem .sao {{ display:block; position:absolute; inset:0 0 auto 0; height:200px; }}
.nt-canh.dem .sao i {{ position:absolute; width:3px; height:3px; border-radius:50%; background:#fff;
    box-shadow:0 0 6px 1px rgba(255,255,255,.8); animation:nt-nhay 2.6s ease-in-out infinite; }}
.nt-canh.dem .mat-trang {{ display:block; position:absolute; right:80px; top:36px; width:64px; height:64px; border-radius:50%;
    background:radial-gradient(circle at 40% 40%, #FFFBE6, #F3E6B5); box-shadow:0 0 40px 12px rgba(255,248,210,.45); }}
.nt-canh.dem .mat-trang:after {{ content:""; position:absolute; left:16px; top:20px; width:10px; height:10px; border-radius:50%;
    background:rgba(200,180,120,.35); box-shadow:18px 12px 0 -2px rgba(200,180,120,.3); }}
.nt-canh.dem .phan-hoa i {{ background:radial-gradient(circle,#F7FFB0,#C8FF5A 60%,transparent 70%);
    box-shadow:0 0 12px 4px rgba(210,255,110,.85); }}
.nt-canh.dem .bong-so div {{ background:rgba(255,255,255,.82); }}
.nt-canh .phan-hoa {{ position:absolute; inset:auto 0 0 0; height:100%; pointer-events:none; z-index:5; }}
.nt-canh .phan-hoa i {{ position:absolute; bottom:40px; width:6px; height:6px; border-radius:50%;
    background:radial-gradient(circle,#FFFBD6,#FFE27A 60%,transparent 70%); box-shadow:0 0 8px 2px rgba(255,236,140,.7);
    animation:nt-bay-len 10s ease-in-out infinite; }}
.nt-canh .hoa-co {{ position:absolute; left:0; right:0; bottom:0; height:40px; z-index:3; pointer-events:none; }}
.nt-canh .hoa-co span {{ position:absolute; bottom:2px; font-size:20px; transform-origin:50% 100%; animation:nt-lac 3s ease-in-out infinite; }}
.nt-canh .hoa-co .nhanh-co {{ width:22px; height:26px;
    background:radial-gradient(ellipse at 50% 100%, #3E9B2F 0 45%, transparent 46%) 0 0/8px 26px repeat-x; }}
.luong .ong {{ position:absolute; left:50%; top:70px; font-size:15px; z-index:5; animation:nt-ong 4s linear infinite; }}
.luong .ong.o2 {{ top:100px; animation-duration:5.5s; animation-direction:reverse; font-size:12px; }}
.lap-dat {{ position:absolute; top:20px; width:5px; height:5px; border-radius:50%; background:#FFE9A8;
    box-shadow:0 0 8px 3px rgba(255,226,140,.8); animation:nt-lap-dat 3.5s ease-in-out infinite; }}
.luong.dang-chon .dat {{ box-shadow:0 0 0 4px rgba(255,255,255,.9), 0 0 32px 8px rgba(255,236,150,.9),
    inset 0 -6px 10px rgba(0,0,0,.25); }}
.luong:not(.khoa) .dat {{ transition:transform .3s ease, box-shadow .3s ease; }}
.luong:not(.khoa):hover .dat {{ transform:translateY(-3px); }}
.luong .chip-tt {{ animation:nt-noi 3.2s ease-in-out infinite; }}
.luong .chip-tt.chin {{ animation:nt-noi 3.2s ease-in-out infinite, nt-nhip 1.6s ease-in-out infinite; }}
.thanh-luong i {{ background-image:repeating-linear-gradient(45deg, rgba(255,255,255,.28) 0 7px, transparent 7px 14px),
    linear-gradient(90deg,#9BE07F,#2F7A24) !important; animation:nt-soc 1.2s linear infinite; }}
.luong.chin .thanh-luong i {{ background-image:repeating-linear-gradient(45deg, rgba(255,255,255,.35) 0 7px, transparent 7px 14px),
    linear-gradient(90deg,#FFD65A,#E39B12) !important; }}
.nt-canh .loe {{ position:absolute; inset:0; border-radius:13px; overflow:hidden; pointer-events:none; }}
.nt-canh .loe i {{ position:absolute; top:0; bottom:0; width:30%; left:-40%;
    background:linear-gradient(100deg, transparent, rgba(255,255,255,.45), transparent); animation:nt-loe 5s ease-in-out infinite; }}

/* nút dưới mỗi luống */
.st-key-trang_nong_trai [class*="st-key-nt_"] button {{ border-radius:14px !important; min-height:44px;
    transition:transform .2s ease, box-shadow .2s ease !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_tuoi_"] button {{ border:none !important;
    background:linear-gradient(135deg,#6EC1FF,#1D6FB8) !important; box-shadow:0 10px 20px -10px rgba(29,111,184,.85) !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_tuoi_"] button:disabled {{ background:#EAF3FB !important; box-shadow:none !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_tuoi_"] button:disabled p {{ color:#6A8BA8 !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_thu_"] button {{ border:none !important;
    background:linear-gradient(135deg,#FFD65A,#E8743B) !important; box-shadow:0 10px 22px -10px rgba(232,116,59,.9) !important;
    animation:nt-nhip 1.8s ease-in-out infinite; }}
.st-key-trang_nong_trai [class*="st-key-nt_tuoi_"] button p, .st-key-trang_nong_trai [class*="st-key-nt_thu_"] button p {{
    color:#fff !important; font-weight:800 !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_"] button:not(:disabled):hover {{ transform:translateY(-2px); }}
/* dấu + đúng giữa luống trống (nút thật, kéo lên nằm trên mặt đất) */
.st-key-trang_nong_trai [class*="st-key-nt_cong_"] {{ position:relative; z-index:6; width:100% !important; max-width:none !important;
    height:76px; margin-top:-165px; }}
.st-key-trang_nong_trai [class*="st-key-nt_cong_"] button {{ position:absolute !important; left:50%; top:0;
    transform:translateX(-50%); width:76px !important; height:76px !important; min-height:76px !important;
    border-radius:50% !important; border:none !important; padding:0 !important;
    background:radial-gradient(circle at 35% 30%, #FFFFFF, #EAF8E2 60%, #C9EDB8) !important;
    animation:nt-song 2s ease-out infinite; transition:transform .25s cubic-bezier(.3,1.6,.5,1), background .25s ease !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_cong_"] button:before {{ content:""; position:absolute; inset:-9px; border-radius:50%;
    border:3px dashed rgba(255,255,255,.95); animation:nt-xoay 9s linear infinite; pointer-events:none; }}
.st-key-trang_nong_trai [class*="st-key-nt_cong_"] button p {{ font-size:2.4rem !important; font-weight:300 !important;
    color:#2F7A24 !important; line-height:1 !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_cong_"] button:hover {{ transform:translateX(-50%) scale(1.12) !important;
    background:radial-gradient(circle at 35% 30%, #9BE07F, #46A033) !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_cong_"] button:hover p {{ color:#fff !important; }}

/* bảng chọn hạt giống: gọn, nằm ngay trên luống */
.st-key-trang_nong_trai [class*="st-key-nt_chon_"] {{ position:relative; z-index:7; width:100% !important; max-width:300px !important;
    margin:-324px auto 0 !important; height:150px !important; min-height:0 !important; overflow:hidden; flex:none !important;
    gap:6px !important; justify-content:center !important; padding:10px !important; border-radius:22px; background:rgba(255,255,255,.97);
    box-shadow:0 18px 36px -14px rgba(25,70,20,.6), 0 0 0 5px rgba(255,255,255,.45);
    animation:nt-bat .4s cubic-bezier(.2,.9,.3,1.2) both; }}
.chon-hat-td {{ text-align:center; font-weight:800; color:#2F6B22; font-size:.9rem; line-height:22px; height:22px; }}
.st-key-trang_nong_trai [class*="st-key-nt_chon_"] .stHorizontalBlock {{ gap:8px !important; flex-wrap:nowrap !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_chon_"] [data-testid="stColumn"] {{ min-width:0 !important; width:auto !important;
    flex:1 1 0 !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_dong_"] {{ position:absolute !important; top:8px; right:10px; z-index:2;
    width:26px !important; height:26px; }}
.st-key-trang_nong_trai [class*="st-key-nt_dong_"] button {{ width:26px !important; height:26px !important; min-height:26px !important;
    padding:0 !important; border-radius:50% !important; border:none !important; background:#F1F5EE !important;
    transition:transform .2s ease, background .2s ease !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_dong_"] button p {{ font-size:.75rem !important; color:#5B6B55 !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_dong_"] button:hover {{ background:#FDE3E1 !important; transform:rotate(90deg) !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_gieo_"] button {{ height:92px !important; min-height:92px !important;
    border-radius:16px !important; padding:44px 2px 6px !important; border:1.5px solid #EEF1EA !important;
    background-repeat:no-repeat !important; background-position:50% 8px !important; background-size:34px 34px !important;
    box-shadow:0 6px 14px -10px rgba(40,70,30,.6) !important;
    transition:transform .22s cubic-bezier(.3,1.6,.5,1), box-shadow .22s ease, border-color .22s ease !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_gieo_"][class*="_lua"] button {{
    background-image:{_uri_icon('lua')}, linear-gradient(180deg,#FFFDF3,#FFF1C7) !important;
    background-position:50% 8px, 0 0 !important; background-size:34px 34px, 100% 100% !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_gieo_"][class*="_ho_tieu"] button {{
    background-image:{_uri_icon('ho_tieu')}, linear-gradient(180deg,#F8FDF3,#DDF1CF) !important;
    background-position:50% 8px, 0 0 !important; background-size:34px 34px, 100% 100% !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_gieo_"][class*="_ca_phe"] button {{
    background-image:{_uri_icon('ca_phe')}, linear-gradient(180deg,#FFFAF5,#F1DFCC) !important;
    background-position:50% 8px, 0 0 !important; background-size:34px 34px, 100% 100% !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_gieo_"] button p {{ white-space:pre-line; line-height:1.25 !important;
    font-size:.7rem !important; font-weight:600 !important; color:#7A6E5A !important; }}
.st-key-trang_nong_trai [class*="st-key-nt_gieo_"] button p:first-line {{ font-size:.86rem; font-weight:800; color:#3B2F18; }}
.st-key-trang_nong_trai [class*="st-key-nt_gieo_"] button:hover {{ transform:translateY(-4px) !important;
    border-color:#7BC862 !important; box-shadow:0 12px 20px -10px rgba(47,122,36,.7) !important; }}
.icon-cay {{ width:1.15em; height:1.15em; vertical-align:-.2em; }}
.kho-bt .icon-cay {{ width:30px; height:30px; }}
@media (max-width: 640px) {{
    .st-key-trang_nong_trai [class*="st-key-nt_cong_"], .st-key-trang_nong_trai [class*="st-key-nt_chon_"] {{ margin-top:0 !important; }}
    .nt-canh .nha-kho, .nt-canh .cay-to, .nt-canh .cau-vong {{ display:none; }} }}

@media (max-width: 760px) {{ .nt-canh .bong-so {{ display:none; }} .nt-canh .bien-go {{ min-width:0; }}
    .luong .hinh-cay {{ width:120px; height:112px; }} }}
@media (prefers-reduced-motion: reduce) {{ .nt-canh * {{ animation:none !important; }} }}
</style>""")



# ================================================================ DIỄN ĐÀN
_MAU_AVATAR = ["#E8743B", "#D48A06", "#047857", "#2563EB", "#7C3AED", "#DB2777", "#0E7490", "#65A30D"]
_HUY_HIEU = {-1: ("Quản trị", "qt"), 1: ("Mùa Vàng", "h1"), 2: ("Bội Thu", "h2"), 3: ("Đại Điền", "h3")}


def chu_nguoi_dung(chu: str) -> str:
    """Chữ người dùng nhập: thoát HTML, giữ xuống dòng, không để Streamlit hiểu $ là công thức."""
    return e(chu).replace("$", "&#36;").replace("\n", "<br>")


def avatar_dd(ho_ten: str, nd_id: int, anh_b64: str = "", co: int = 40) -> str:
    if anh_b64:
        return (f'<span class="dd-av" style="width:{co}px;height:{co}px"><img src="data:image/jpeg;base64,{anh_b64}" '
                f'alt=""></span>')
    chu = (ho_ten.strip().split()[-1][:1] if ho_ten.strip() else "?").upper()
    return (f'<span class="dd-av" style="width:{co}px;height:{co}px;font-size:{co * .42:.0f}px;'
            f'background:{_MAU_AVATAR[nd_id % len(_MAU_AVATAR)]}">{e(chu)}</span>')


def huy_hieu_dd(hang: int) -> str:
    if hang not in _HUY_HIEU:
        return ""
    ten, lop = _HUY_HIEU[hang]
    return f'<span class="dd-hh {lop}">{"🛡️" if hang == -1 else "👑"} {ten}</span>'


def dau_dien_dan(tk: dict) -> str:
    return gon(f"""<div class="dd-dau"><div class="dd-bong b1"></div><div class="dd-bong b2"></div>
      <div class="dd-dau-trai"><div class="dd-td">Diễn đàn Bồ Nông</div>
        <div class="dd-phu">Trò chuyện cùng bà con · chia sẻ kinh nghiệm mùa vụ · mua vật tư nông nghiệp</div></div>
      <div class="dd-so"><div><i>👥</i><b>{so(tk['thanh_vien'])}</b><span>thành viên</span></div>
        <div><i>📰</i><b>{so(tk['bai'])}</b><span>bài viết</span></div>
        <div><i>💬</i><b>{so(tk['tin_hom_nay'])}</b><span>tin hôm nay</span></div>
        <div><i>🛒</i><b>{so(tk['san_pham'])}</b><span>sản phẩm</span></div></div></div>""")


def bong_bong_tin(t: dict, la_minh: bool, hang: int, anh_b64: str, thoi_gian: str) -> str:
    an = '<span class="dd-an">Đang ẩn do bị báo cáo</span>' if t.get("an") else ""
    return gon(f'<div class="dd-tin {"minh" if la_minh else ""}">'
               + ("" if la_minh else avatar_dd(t["ho_ten"], t["nguoi_dung_id"], anh_b64, 34))
               + f'<div class="dd-bb"><div class="dd-ten">{"Bạn" if la_minh else e(t["ho_ten"])}{huy_hieu_dd(hang)}'
               f'<span class="dd-gio">{e(thoi_gian)}</span></div>'
               f'<div class="dd-noi">{chu_nguoi_dung(t["noi_dung"])}</div>{an}</div></div>')


def chat_trong() -> str:
    return gon('<div class="dd-trong"><div class="dd-trong-icon">💬</div><b>Chưa có tin nhắn nào</b>'
               '<span>Hãy là người đầu tiên chào bà con!</span></div>')


def dau_bai(b: dict, hang: int, anh_b64: str, thoi_gian: str) -> str:
    an = '<div class="dd-an">Bài đang ẩn do bị báo cáo · chỉ quản trị thấy</div>' if b.get("an") else ""
    return gon(f'<div class="dd-bai-dau">{avatar_dd(b["ho_ten"], b["nguoi_dung_id"], anh_b64, 44)}'
               f'<div class="dd-bai-ten"><b>{e(b["ho_ten"])}</b>{huy_hieu_dd(hang)}'
               f'<span class="dd-tg">{e(thoi_gian)} · <i class="dd-cd cd-{["Chung", "Lúa", "Cà phê", "Hồ tiêu"].index(b["chu_de"]) if b["chu_de"] in ["Chung", "Lúa", "Cà phê", "Hồ tiêu"] else 0}">'
               f'{ {"Chung": "🌐", "Lúa": "🌾", "Cà phê": "☕", "Hồ tiêu": "🌿"}.get(b["chu_de"], "")} {e(b["chu_de"])}</i></span></div></div>{an}'
               f'<div class="dd-bai-noi">{chu_nguoi_dung(b["noi_dung"])}</div>')


def dong_binh_luan(c: dict, hang: int, anh_b64: str, thoi_gian: str) -> str:
    an = ' <span class="dd-an">ẩn</span>' if c.get("an") else ""
    return gon(f'<div class="dd-bl">{avatar_dd(c["ho_ten"], c["nguoi_dung_id"], anh_b64, 30)}'
               f'<div class="dd-bl-bb"><b>{e(c["ho_ten"])}</b>{huy_hieu_dd(hang)}{an}'
               f'<div>{chu_nguoi_dung(c["noi_dung"])}</div><span class="dd-gio">{e(thoi_gian)}</span></div></div>')


_TRANH_SP = {
    "Phân bón": ('<svg viewBox="0 0 120 90"><path d="M30 20 h60 l6 60 h-72z" fill="#E9D7B5" stroke="#B8935A" stroke-width="3"/>'
                 '<path d="M30 20 q30 -10 60 0" fill="none" stroke="#B8935A" stroke-width="3"/>'
                 '<rect x="38" y="38" width="44" height="24" rx="5" fill="#46A033"/>'
                 '<text x="60" y="55" text-anchor="middle" font-size="12" font-weight="800" fill="#fff" '
                 'font-family="sans-serif">NPK</text><circle cx="98" cy="74" r="5" fill="#8B5A2B"/>'
                 '<circle cx="106" cy="80" r="4" fill="#A0703F"/><circle cx="92" cy="82" r="3.5" fill="#7A4A26"/></svg>'),
    "Thuốc trừ sâu": ('<svg viewBox="0 0 120 90"><rect x="44" y="10" width="20" height="12" rx="3" fill="#2F7A24"/>'
                      '<path d="M40 22 h28 v8 q10 6 10 18 v32 a6 6 0 0 1 -6 6 h-36 a6 6 0 0 1 -6 -6 v-32 q0 -12 10 -18z" '
                      'fill="#E8F5FF" stroke="#2F7FD6" stroke-width="3"/><rect x="36" y="48" width="36" height="22" rx="4" '
                      'fill="#2F7FD6"/><path d="M48 58 l6 6 l10 -12" stroke="#fff" stroke-width="3" fill="none"/>'
                      '<path d="M84 40 q10 -6 20 0 q-10 10 -20 0z" fill="#4FA83A"/><path d="M86 52 l14 4 M88 60 l12 8" '
                      'stroke="#8FD0FF" stroke-width="3" stroke-linecap="round"/></svg>'),
    "Hạt giống": ('<svg viewBox="0 0 120 90"><path d="M28 30 h50 v52 h-50z" fill="#F7E3B5" stroke="#C99A3E" stroke-width="3"/>'
                  '<path d="M28 30 l8 -12 h34 l8 12" fill="#EED39A" stroke="#C99A3E" stroke-width="3"/>'
                  '<path d="M53 72 V52" stroke="#3E9B2F" stroke-width="3"/><path d="M53 58 q-12 -2 -12 -12 q10 0 12 12z" '
                  'fill="#6CCB52"/><path d="M53 54 q12 -4 12 -14 q-10 2 -12 14z" fill="#4FB43A"/>'
                  '<ellipse cx="92" cy="70" rx="6" ry="4" fill="#C98A12"/><ellipse cx="102" cy="78" rx="6" ry="4" fill="#E0A82E"/>'
                  '<ellipse cx="90" cy="82" rx="5" ry="3.5" fill="#B47A10"/></svg>'),
    "Dụng cụ": ('<svg viewBox="0 0 120 90"><rect x="30" y="26" width="34" height="50" rx="10" fill="#FFB52E" stroke="#C9821A" '
                'stroke-width="3"/><rect x="38" y="16" width="18" height="12" rx="3" fill="#C9821A"/>'
                '<path d="M64 40 q20 0 26 -14 l10 4" stroke="#4A4A4A" stroke-width="4" fill="none" stroke-linecap="round"/>'
                '<rect x="36" y="42" width="22" height="10" rx="3" fill="#fff" opacity=".7"/>'
                '<path d="M100 30 l8 -6 M102 36 l10 0 M100 42 l8 6" stroke="#8FD0FF" stroke-width="3" stroke-linecap="round"/></svg>'),
}


def the_san_pham(sp: dict, anh_b64: str = "") -> str:
    hinh = (f'<img src="data:image/jpeg;base64,{anh_b64}" alt="">' if anh_b64
            else _TRANH_SP.get(sp["danh_muc"], _TRANH_SP["Phân bón"]))
    nhan = ""
    if sp.get("an"):
        nhan = '<span class="dd-sp-nhan an">Đang ẩn</span>'
    elif not sp["con_hang"]:
        nhan = '<span class="dd-sp-nhan het">Tạm hết hàng</span>'
    phu = f'<div class="dd-sp-phu">🌱 Hợp với: {e(sp["phu_hop"])}</div>' if sp["phu_hop"] else ""
    if sp.get("so_anh", 0) > 1:
        nhan += f'<span class="dd-sp-so-anh">📷 {sp["so_anh"]} ảnh</span>'
    return gon(f'<div class="dd-sp {"mo" if (sp.get("an") or not sp["con_hang"]) else ""}">'
               f'<div class="dd-sp-hinh dm-{list(_TRANH_SP).index(sp["danh_muc"]) if sp["danh_muc"] in _TRANH_SP else 0}">'
               f'{hinh}{nhan}<span class="dd-sp-dm">{e(sp["danh_muc"])}</span></div>'
               f'<div class="dd-sp-ten">{e(sp["ten"])}</div><div class="dd-sp-mt">{chu_nguoi_dung(sp["mo_ta"])}</div>{phu}'
               f'<div class="dd-sp-gia">{so(sp["gia"])}<small> đ / {e(sp["don_vi"])}</small></div>'
               f'<div class="dd-sp-mau">Giá mẫu · chế độ thử</div></div>')


def the_don_cho(d: dict, ten_tt: str) -> str:
    return gon(f'<div class="dd-don tt-{d["trang_thai"]}"><div><b>{e(d["ten_sp"])}</b> × {d["so_luong"]} '
               f'<span class="dd-gio">· mã {e(d["ma_don"])} · {d["tao_luc"]:%H:%M %d/%m/%Y}</span>'
               f'<div class="dd-don-dc">{e(d["ho_ten"])} · {e(d["so_dien_thoai"])} · {e(d["dia_chi"])}</div></div>'
               f'<div class="dd-don-phai"><b>{so(d["so_tien"])} đ</b><span class="dd-tt">{e(ten_tt)}</span></div></div>')


def css_dien_dan() -> str:
    return css_khung_anh() + css_dien_dan_dep() + gon(f"""
<style>
@keyframes dd-troi {{ 0%,100% {{ transform:translate(0,0) scale(1); }} 50% {{ transform:translate(30px,-20px) scale(1.15); }} }}
@keyframes dd-hien {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
.thanh-tai-khoan a.chip-dd {{ color:#1D4ED8 !important; background:#EEF4FF; border-color:#C9DAFB; }}
.thanh-tai-khoan a.chip-dd:hover {{ background:#E0EAFF; box-shadow:0 8px 18px -8px rgba(37,99,235,.45); }}
.dd-dau {{ position:relative; overflow:hidden; display:flex; align-items:center; justify-content:space-between; gap:20px;
    flex-wrap:wrap; padding:26px 30px; border-radius:26px; margin:.4rem 0 1rem; color:#fff;
    background:linear-gradient(120deg,#1E5631 0%,#2F7A24 45%,#4A9B3A 100%); box-shadow:0 22px 40px -26px rgba(20,60,20,.9); }}
.dd-bong {{ position:absolute; border-radius:50%; background:radial-gradient(circle,rgba(255,255,255,.22),transparent 70%);
    animation:dd-troi 9s ease-in-out infinite; }}
.dd-bong.b1 {{ width:260px; height:260px; right:12%; top:-120px; }}
.dd-bong.b2 {{ width:200px; height:200px; left:-60px; bottom:-110px; animation-delay:-4s; }}
.dd-td {{ font-family:'Noto Serif', Georgia, serif; font-size:2rem; font-weight:800; line-height:1.1; }}
.dd-phu {{ opacity:.9; margin-top:6px; font-size:.98rem; }}
.dd-so {{ display:flex; gap:10px; position:relative; }}
.dd-so div {{ background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.25); border-radius:16px;
    padding:10px 16px; text-align:center; backdrop-filter:blur(4px); min-width:92px; }}
.dd-so i {{ display:block; font-style:normal; font-size:1.1rem; }} .dd-so b {{ display:block; font-size:1.35rem; }} .dd-so span {{ font-size:.75rem; opacity:.9; }}

.dd-av {{ flex:none; display:inline-flex; align-items:center; justify-content:center; border-radius:50%; overflow:hidden;
    color:#fff; font-weight:800; box-shadow:0 0 0 2px #fff, 0 4px 10px -4px rgba(0,0,0,.35); }}
.dd-av img {{ width:100%; height:100%; object-fit:cover; }}
.dd-hh {{ display:inline-flex; align-items:center; gap:3px; margin-left:6px; padding:1px 8px; border-radius:999px;
    font-size:.68rem; font-weight:800; vertical-align:middle; }}
.dd-hh.h1 {{ background:#FFF3C4; color:#9A6A00; }} .dd-hh.h2 {{ background:#E3F4DC; color:#2F6B22; }}
.dd-hh.h3 {{ background:linear-gradient(135deg,#FFE7A3,#F2B33D); color:#6B4300; }}
.dd-hh.qt {{ background:#FDE3E1; color:#B42318; }}
.dd-gio {{ font-size:.72rem; color:{CHU_PHU}; font-weight:500; }}
.dd-an {{ display:inline-block; margin-top:4px; padding:2px 8px; border-radius:8px; font-size:.72rem; font-weight:700;
    background:#FEF3C7; color:#92400E; }}

/* phòng chat */
.st-key-khung_chat {{ background:linear-gradient(180deg,#F6FBF3,#FFFFFF); border-radius:20px; }}
.dd-tin {{ display:flex; gap:10px; align-items:flex-end; margin:4px 0; animation:dd-hien .3s ease both; }}
.dd-tin.minh {{ justify-content:flex-end; }}
.dd-bb {{ max-width:min(560px,82%); padding:8px 14px 9px; border-radius:18px 18px 18px 6px; background:#fff;
    border:1px solid #E6EEE1; box-shadow:0 6px 14px -12px rgba(30,60,30,.6); }}
.dd-tin.minh .dd-bb {{ border-radius:18px 18px 6px 18px; border:none; color:#fff;
    background:linear-gradient(135deg,#46A033,#2F7A24); box-shadow:0 10px 18px -12px rgba(47,122,36,.9); }}
.dd-ten {{ font-size:.78rem; font-weight:800; color:#2F6B22; margin-bottom:2px; }}
.dd-tin.minh .dd-ten {{ color:rgba(255,255,255,.92); text-align:right; }}
.dd-ten .dd-gio {{ margin-left:8px; }} .dd-tin.minh .dd-gio {{ color:rgba(255,255,255,.75); }}
.dd-noi {{ font-size:.95rem; line-height:1.45; word-wrap:break-word; }}
.dd-trong {{ display:flex; flex-direction:column; align-items:center; gap:4px; padding:70px 0; color:{CHU_PHU}; }}
.dd-trong-icon {{ font-size:2.6rem; animation:dd-troi 4s ease-in-out infinite; }}
.st-key-khung_chat [data-testid="stPopover"] button, .st-key-dd_bang_tin [data-testid="stPopover"] button {{
    border:none !important; background:transparent !important; min-height:28px !important; padding:0 6px !important;
    color:{CHU_PHU} !important; }}
.st-key-khung_chat [data-testid="stPopover"] button:hover {{ background:#EEF5EA !important; }}
.st-key-dd_o_chat textarea {{ font-size:1rem !important; }}

/* bảng tin */
.st-key-dd_soan {{ background:#fff; border:1px solid #E6EEE1 !important; border-radius:22px !important;
    box-shadow:0 14px 28px -24px rgba(30,60,30,.7); }}
[class*="st-key-dd_bai_"] {{ background:#fff; border:1px solid #ECEFE8; border-radius:22px; padding:16px 18px 10px;
    box-shadow:0 14px 30px -26px rgba(30,60,30,.75); animation:dd-hien .35s ease both; gap:.6rem !important; }}
.dd-bai-dau {{ display:flex; gap:12px; align-items:center; }}
.dd-bai-ten b {{ color:{CHU}; font-size:1rem; }} .dd-bai-ten .dd-tg {{ display:block; font-size:.78rem; color:{CHU_PHU}; margin-top:2px; }}
.dd-cd {{ font-style:normal; font-weight:800; padding:1px 8px; border-radius:999px; }}
.dd-cd.cd-0 {{ background:#EEF4FF; color:#1D4ED8; }} .dd-cd.cd-1 {{ background:#FFF6D6; color:#9A6A00; }}
.dd-cd.cd-2 {{ background:#F3E6DA; color:#7A4A26; }} .dd-cd.cd-3 {{ background:#E3F4DC; color:#2F6B22; }}
.dd-bai-noi {{ margin-top:10px; font-size:1rem; line-height:1.6; color:{CHU}; word-wrap:break-word; }}
[class*="st-key-dd_bai_"] [data-testid="stImage"] img {{ border-radius:16px; max-height:520px; object-fit:cover; }}
.dd-bl {{ display:flex; gap:8px; margin:6px 0; animation:dd-hien .3s ease both; }}
.dd-bl-bb {{ background:#F4F7F1; border-radius:4px 16px 16px 16px; padding:7px 12px; font-size:.9rem; line-height:1.45; }}
.dd-bl-bb b {{ font-size:.8rem; color:#2F6B22; }} .dd-bl-bb .dd-gio {{ display:block; margin-top:2px; }}

/* chợ */
.dd-sp {{ position:relative; background:#fff; border:1px solid #ECEFE8; border-radius:22px; padding:12px 14px 12px;
    box-shadow:0 14px 30px -26px rgba(30,60,30,.75); transition:transform .25s ease, box-shadow .25s ease; height:100%; }}
.dd-sp:hover {{ transform:translateY(-4px); box-shadow:0 22px 34px -24px rgba(30,60,30,.8); }}
.dd-sp.mo {{ opacity:.7; }}
.dd-sp-hinh {{ position:relative; aspect-ratio:4 / 3; border-radius:16px; display:flex; align-items:center; justify-content:center;
    overflow:hidden; }}
.dd-sp-hinh.dm-0 {{ background:radial-gradient(circle at 30% 30%,#FFF8E6,#F4E2BC); }}
.dd-sp-hinh.dm-1 {{ background:radial-gradient(circle at 30% 30%,#F1F8FF,#D6E8FB); }}
.dd-sp-hinh.dm-2 {{ background:radial-gradient(circle at 30% 30%,#F5FBEF,#D8EFC9); }}
.dd-sp-hinh.dm-3 {{ background:radial-gradient(circle at 30% 30%,#FFF4E8,#FBDDBE); }}
.dd-sp-hinh svg {{ width:62%; height:auto; transition:transform .35s cubic-bezier(.3,1.6,.5,1); }}
.dd-sp:hover .dd-sp-hinh svg {{ transform:scale(1.08) rotate(-3deg); }}
.dd-sp-hinh img {{ width:100%; height:100%; object-fit:cover; }}
.dd-sp-dm {{ position:absolute; left:10px; top:10px; padding:2px 10px; border-radius:999px; background:rgba(255,255,255,.9);
    font-size:.72rem; font-weight:800; color:#2F6B22; }}
.dd-sp-nhan {{ position:absolute; right:10px; top:10px; padding:2px 10px; border-radius:999px; font-size:.72rem; font-weight:800; }}
.ct-sp {{ padding:4px 0 8px; }} .ct-dm {{ position:static; display:inline-block; background:#E7F5DF; }}
.ct-ten {{ font-family:'Noto Serif', Georgia, serif; font-size:1.6rem; font-weight:800; color:{CHU}; margin:8px 0 4px; line-height:1.25; }}
.ct-mt {{ color:{CHU_PHU}; font-size:.95rem; line-height:1.5; }}
.ct-gia {{ margin:12px 0 8px; font-size:1.9rem; font-weight:900; color:#C2410C; }}
.ct-gia small {{ font-size:.9rem; color:{CHU_PHU}; font-weight:600; }}
.ct-dong {{ display:flex; flex-wrap:wrap; gap:14px; font-size:.88rem; color:#4E5E48; margin-bottom:10px; }}
.ct-con {{ color:#15803D; font-weight:800; }} .ct-het {{ color:#B42318; font-weight:800; }}
.ct-cam {{ font-size:.8rem; color:#6B7A64; background:#F4F8F1; border-radius:12px; padding:8px 12px; margin-bottom:10px; }}
[class*="st-key-dd_xem_"] button {{ border-radius:14px !important; border:1.5px solid #CFE6C4 !important; background:#fff !important; }}
[class*="st-key-dd_xem_"] button p {{ color:#2F6B22 !important; font-weight:800 !important; }}
[class*="st-key-dd_xem_"] button:hover {{ background:#F1F8EC !important; }}
.dd-sp-so-anh {{ position:absolute; right:10px; bottom:10px; padding:2px 9px; border-radius:999px; font-size:.72rem;
    font-weight:800; color:#fff; background:rgba(20,30,20,.55); backdrop-filter:blur(3px); }}
[class*="st-key-dd_luoi_anh_"] [data-testid="stImage"] img {{ aspect-ratio:1 / 1; object-fit:cover; border-radius:12px !important;
    max-height:none !important; transition:transform .25s ease; }}
[class*="st-key-dd_luoi_anh_"] [data-testid="stImage"] img:hover {{ transform:scale(1.03); }}
[class*="st-key-dd_luoi_anh_"] {{ gap:.4rem !important; }}
[class*="st-key-dd_luoi_anh_"] .stHorizontalBlock {{ gap:.4rem !important; }}
.dd-sp-nhan.het {{ background:#FDE3E1; color:#B42318; }} .dd-sp-nhan.an {{ background:#E5E7EB; color:#374151; }}
.dd-sp-ten {{ margin-top:10px; font-weight:800; font-size:1.02rem; color:{CHU}; }}
.dd-sp-mt {{ font-size:.84rem; color:{CHU_PHU}; line-height:1.45; margin-top:3px; min-height:2.9em; }}
.dd-sp-phu {{ font-size:.78rem; color:#2F6B22; margin-top:6px; font-weight:600; }}
.dd-sp-gia {{ margin-top:8px; font-size:1.25rem; font-weight:900; color:#C2410C; }}
.dd-sp-gia small {{ font-size:.78rem; color:{CHU_PHU}; font-weight:600; }}
.dd-sp-mau {{ font-size:.68rem; color:#9CA3AF; }}
[class*="st-key-dd_mua_"] button {{ border:none !important; border-radius:14px !important; color:#fff !important;
    background:linear-gradient(135deg,#F59E0B,#EA580C) !important; box-shadow:0 10px 20px -12px rgba(234,88,12,.9) !important;
    transition:transform .2s ease !important; }}
[class*="st-key-dd_mua_"] button p {{ color:#fff !important; font-weight:800 !important; }}
[class*="st-key-dd_mua_"] button:hover {{ transform:translateY(-2px); }}
[class*="st-key-dd_mua_"] button:disabled {{ background:#E5E7EB !important; box-shadow:none !important; }}
[class*="st-key-dd_mua_"] button:disabled p {{ color:#6B7280 !important; }}
.dd-don {{ display:flex; justify-content:space-between; gap:12px; padding:10px 14px; border-radius:14px; margin:6px 0;
    background:#FAFBF8; border:1px solid #ECEFE8; font-size:.9rem; }}
.dd-don-dc {{ font-size:.78rem; color:{CHU_PHU}; margin-top:2px; }}
.dd-don-phai {{ text-align:right; white-space:nowrap; }} .dd-don-phai b {{ display:block; color:#C2410C; }}
.dd-tt {{ font-size:.72rem; font-weight:800; padding:2px 8px; border-radius:999px; background:#E5E7EB; }}
.dd-don.tt-cho .dd-tt {{ background:#FEF3C7; color:#92400E; }} .dd-don.tt-da_tt .dd-tt {{ background:#DBEAFE; color:#1D4ED8; }}
.dd-don.tt-da_giao .dd-tt {{ background:#DCFCE7; color:#15803D; }}
@media (prefers-reduced-motion: reduce) {{ .dd-dau *, .dd-tin, .dd-bl, [class*="st-key-dd_bai_"] {{ animation:none !important; }} }}
</style>""")



def khung_anh(ds_b64: list, khoa: str) -> str:
    """Khung nhiều ảnh gọn gàng + xem ảnh to khi bấm (không cần JavaScript)."""
    n = len(ds_b64)
    hien = ds_b64[:5]
    kieu = {1: "k1", 2: "k2", 3: "k3", 4: "k4"}.get(n, "k5")
    o = []
    for i, b in enumerate(hien):
        ma = f"bnxa-{khoa}-{i}"
        them = (f'<span class="ka-them">+{n - 5}</span>' if i == 4 and n > 5 else "")
        o.append(f'<div class="ka-o o{i}"><a href="#{ma}"><img src="data:image/jpeg;base64,{b}" alt="" loading="lazy">'
                 f'{them}</a></div>')
    # lớp xem ảnh to: mỗi ảnh một lớp, hiện khi được bấm (CSS :target)
    xem = "".join(
        f'<div class="ka-xem" id="bnxa-{khoa}-{i}"><a class="ka-nen" href="#bn-dong-anh"></a>'
        f'<img src="data:image/jpeg;base64,{b}" alt="">'
        f'<a class="ka-dong" href="#bn-dong-anh">✕</a>'
        + (f'<a class="ka-truoc" href="#bnxa-{khoa}-{i - 1}">‹</a>' if i > 0 else "")
        + (f'<a class="ka-sau" href="#bnxa-{khoa}-{i + 1}">›</a>' if i < n - 1 else "")
        + f'<span class="ka-dem">{i + 1} / {n}</span></div>' for i, b in enumerate(ds_b64))
    return gon(f'<div class="khung-anh {kieu}">{"".join(o)}</div>{xem}')


def css_khung_anh() -> str:
    return gon("""
<style>
.khung-anh { display:grid; gap:6px; border-radius:18px; overflow:hidden; margin:4px auto 6px; width:100%; max-width:820px; }
.khung-anh .ka-o { position:relative; overflow:hidden; background:#EEF1EA; min-height:0; }
.khung-anh .ka-o a { display:block; width:100%; height:100%; cursor:zoom-in; }
.khung-anh img { width:100%; height:100%; object-fit:cover; display:block; transition:transform .35s ease, filter .35s ease; }
.khung-anh .ka-o:hover img { transform:scale(1.05); filter:brightness(1.05); }
.khung-anh.k1 { grid-template-columns:1fr; max-width:640px; }
.khung-anh.k1 .ka-o, .khung-anh.k1 img { max-height:460px; }
.khung-anh.k2 { grid-template-columns:1fr 1fr; height:340px; }
.khung-anh.k3 { grid-template-columns:repeat(3,1fr); gap:14px; align-items:start; overflow:visible; border-radius:0;
    padding:0 2px; }
.khung-anh.k3 .ka-o { aspect-ratio:3 / 4; border-radius:22px; box-shadow:0 0 0 1px rgba(0,0,0,.06), 0 12px 24px -16px rgba(0,0,0,.55); }
.khung-anh.k3 .o0, .khung-anh.k3 .o2 { margin-bottom:40px; }
.khung-anh.k3 .o1 { margin-top:40px; }
.khung-anh.k4 { grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; height:440px; }
.khung-anh.k5 { grid-template-columns:repeat(6,1fr); grid-template-rows:1.25fr 1fr; height:460px; }
.khung-anh.k5 .o0 { grid-column:1 / 4; } .khung-anh.k5 .o1 { grid-column:4 / 7; }
.khung-anh.k5 .o2 { grid-column:1 / 3; } .khung-anh.k5 .o3 { grid-column:3 / 5; } .khung-anh.k5 .o4 { grid-column:5 / 7; }
.ka-them { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; color:#fff;
    font-size:1.8rem; font-weight:800; background:rgba(0,0,0,.45); }
.ka-xem { display:none; }
.ka-xem:target { display:flex; position:fixed; inset:0; z-index:1000000; align-items:center; justify-content:center;
    background:rgba(10,14,10,.88); animation:ka-mo .25s ease; }
@keyframes ka-mo { from { opacity:0; } to { opacity:1; } }
.ka-xem .ka-nen { position:absolute; inset:0; cursor:zoom-out; }
.ka-xem img { position:relative; max-width:92vw; max-height:86vh; border-radius:10px; box-shadow:0 20px 60px rgba(0,0,0,.6);
    pointer-events:none; }
.ka-xem .ka-dong, .ka-xem .ka-truoc, .ka-xem .ka-sau { position:absolute; display:flex; align-items:center; justify-content:center;
    color:#fff !important; text-decoration:none !important; background:rgba(255,255,255,.14); border-radius:50%;
    transition:background .2s ease; }
.ka-xem .ka-dong { top:18px; right:22px; width:44px; height:44px; font-size:1.3rem; }
.ka-xem .ka-truoc, .ka-xem .ka-sau { top:50%; width:52px; height:52px; margin-top:-26px; font-size:2.2rem; line-height:1; }
.ka-xem .ka-truoc { left:22px; } .ka-xem .ka-sau { right:22px; }
.ka-xem a:hover { background:rgba(255,255,255,.3); }
.ka-xem .ka-dem { position:absolute; bottom:18px; color:#fff; font-size:.9rem; opacity:.85; }
@media (max-width: 640px) { .khung-anh.k2 { height:200px; } .khung-anh.k3 { gap:8px; } .khung-anh.k3 .o1 { margin-top:22px; } .khung-anh.k3 .o0, .khung-anh.k3 .o2 { margin-bottom:22px; } .khung-anh.k4, .khung-anh.k5 { height:280px; } }
</style>""")



def dau_o_soan(ho_ten: str, nd_id: int, anh_b64: str) -> str:
    return gon(f'<div class="soan-dau">{avatar_dd(ho_ten, nd_id, anh_b64, 42)}<div><b>Tạo bài viết</b>'
               f'<span>Chia sẻ với {e("bà con")} trên Diễn đàn Bồ Nông</span></div></div>')


def dong_dem_bai(so_tim: int, so_bl: int, da_tim: bool) -> str:
    tim = (f'<span class="dem-tim"><i>❤</i>{"Bạn" + (f" và {so_tim - 1} người khác" if so_tim > 1 else "") if da_tim else f"{so_tim} lượt thích"}</span>'
           if so_tim else '<span class="dem-tim mo">Hãy là người thích đầu tiên</span>')
    return gon(f'<div class="dem-bai">{tim}<span>{so_bl} bình luận</span></div>')


def cot_phai_dien_dan(noi_bat: list, tv_moi: list, anh_tv: dict) -> str:
    nb = "".join(f'<div class="cp-nb"><b>{e(b["noi_dung"][:70])}{"…" if len(b["noi_dung"]) > 70 else ""}</b>'
                 f'<span>{e(b["ho_ten"])} · ❤ {b["so_tim"]} · 💬 {b["so_bl"]}</span></div>' for b in noi_bat) \
        or '<div class="cp-trong">Chưa có bài nổi bật.</div>'
    tv = "".join(f'<div class="cp-tv">{avatar_dd(t["ho_ten"], t["id"], anh_tv.get(t["id"], ""), 30)}'
                 f'<span>{e(t["ho_ten"])}</span></div>' for t in tv_moi) or '<div class="cp-trong">Chưa có thành viên.</div>'
    return gon(f"""<div class="cot-phai">
      <div class="cp-the"><div class="cp-td">🔥 Bài nổi bật</div>{nb}</div>
      <div class="cp-the"><div class="cp-td">👋 Thành viên mới</div>{tv}</div>
      <div class="cp-the noi-quy"><div class="cp-td">📌 Nội quy diễn đàn</div>
        <ol><li>Tôn trọng nhau, không chửi bới, công kích.</li><li>Không quảng cáo, không đăng tin lừa đảo.</li>
        <li>Thông tin giá cả nên ghi rõ nơi, ngày.</li><li>Thấy nội dung xấu, bấm <b>⋯ → Báo cáo</b>.</li></ol></div>
    </div>""")


def css_dien_dan_dep() -> str:
    """Lớp trang trí thêm cho diễn đàn (thẻ, ô đăng bài, nút hành động, cột phải)."""
    return gon(f"""
<style>
/* thanh chuyển mục của diễn đàn */
@keyframes dd-nav-sang {{ 0% {{ left:-60%; }} 60%,100% {{ left:130%; }} }}
.st-key-dd_nav {{ background:#fff; border:1px solid #E6EEE1; border-radius:22px; padding:8px 10px;
    box-shadow:0 14px 30px -24px rgba(30,60,30,.75); margin:2px 0 10px; }}
.st-key-dd_nav .stHorizontalBlock {{ gap:8px !important; flex-wrap:nowrap; }}
.st-key-dd_nav [class*="st-key-dd_tab_"] button {{ position:relative; overflow:hidden; min-height:48px; border-radius:16px !important;
    border:1.5px solid transparent !important; background:#F4F7F1 !important;
    transition:transform .2s cubic-bezier(.3,1.6,.5,1), background .2s ease, box-shadow .2s ease !important; }}
.st-key-dd_nav [class*="st-key-dd_tab_"] button p {{ font-size:1rem !important; font-weight:800 !important; color:#4E5E48 !important;
    white-space:nowrap; }}
.st-key-dd_nav [class*="st-key-dd_tab_"] button:hover {{ background:#E7F3E0 !important; border-color:#B9DFA8 !important;
    transform:translateY(-2px); }}
.st-key-dd_nav [class*="st-key-dd_tab_on_"] button {{ background:linear-gradient(135deg,#5BB846,#2F7A24) !important;
    box-shadow:0 12px 22px -12px rgba(47,122,36,.95), inset 0 1px 0 rgba(255,255,255,.35) !important; }}
.st-key-dd_nav [class*="st-key-dd_tab_on_"] button p {{ color:#fff !important; }}
.st-key-dd_nav [class*="st-key-dd_tab_on_"] button:after {{ content:""; position:absolute; top:0; bottom:0; width:40%; left:-60%;
    background:linear-gradient(100deg, transparent, rgba(255,255,255,.35), transparent); animation:dd-nav-sang 3.5s ease-in-out infinite; }}
.st-key-dd_nav [class*="st-key-dd_tab_on_"] button:hover {{ background:linear-gradient(135deg,#66C450,#2F7A24) !important; }}
.st-key-dd_nav [class*="st-key-dd_tab_"][class*="quan_tri"] button p {{ color:#B42318 !important; }}
.st-key-dd_nav [class*="st-key-dd_tab_on_quan_tri"] button {{ background:linear-gradient(135deg,#F97066,#B42318) !important;
    box-shadow:0 12px 22px -12px rgba(180,35,24,.9) !important; }}
.st-key-dd_nav [class*="st-key-dd_tab_on_quan_tri"] button p {{ color:#fff !important; }}
@media (max-width: 640px) {{ .st-key-dd_nav .stHorizontalBlock {{ flex-wrap:wrap; }} }}

/* ô đăng bài */
.st-key-dd_soan {{ background:#fff; border:1px solid #E6EEE1; border-radius:24px; padding:16px 18px 10px;
    box-shadow:0 18px 36px -28px rgba(30,60,30,.8); gap:.5rem !important; }}
.soan-dau {{ display:flex; align-items:center; gap:12px; }}
.soan-dau b {{ display:block; font-size:1.05rem; color:{CHU}; }} .soan-dau span {{ font-size:.8rem; color:{CHU_PHU}; }}
.st-key-dd_soan textarea {{ background:#F6F8F3 !important; border-radius:16px !important; font-size:1rem !important;
    line-height:1.5 !important; }}
.st-key-dd_soan [data-baseweb="textarea"] {{ border:1.5px solid transparent !important; border-radius:16px !important;
    background:#F6F8F3 !important; transition:border-color .2s ease, box-shadow .2s ease; }}
.st-key-dd_soan [data-baseweb="textarea"]:focus-within {{ border-color:#7BC862 !important; box-shadow:0 0 0 4px rgba(123,200,98,.18); }}
.soan-nhan {{ font-size:.78rem; font-weight:800; color:{CHU_PHU}; text-transform:uppercase; letter-spacing:.04em; margin-top:2px; }}
.st-key-dd_soan [data-testid="stFileUploaderDropzone"] {{ padding:6px 8px !important; border-radius:14px !important;
    background:#F1F8EC !important; border:1.5px dashed #A9D995 !important; min-height:0 !important; }}
.st-key-dd_soan [data-testid="stFileUploaderDropzoneInstructions"] {{ display:none !important; }}
.st-key-dd_soan [data-testid="stFileUploaderDropzone"] button {{ font-size:0 !important; width:100%; border:none !important;
    background:transparent !important; min-height:34px; }}
.st-key-dd_soan [data-testid="stFileUploaderDropzone"] button:after {{ content:"📷  Thêm ảnh (chọn nhiều ảnh)";
    font-size:.92rem; font-weight:800; color:#2F6B22; }}
.st-key-dd_soan [data-testid="stFileUploaderDropzone"] button svg {{ display:none; }}
.st-key-dd_soan [data-testid="stFormSubmitButton"] button {{ min-height:46px; border-radius:14px !important; border:none !important;
    background:linear-gradient(135deg,#46A033,#2F7A24) !important; box-shadow:0 12px 22px -12px rgba(47,122,36,.95) !important;
    transition:transform .2s ease !important; }}
.st-key-dd_soan [data-testid="stFormSubmitButton"] button:hover {{ transform:translateY(-2px); }}
.st-key-dd_soan [data-testid="stFormSubmitButton"] button p {{ color:#fff !important; font-weight:800 !important; font-size:1rem !important; }}
.soan-goi-y {{ font-size:.74rem; color:#8A9384; padding:0 2px 4px; }}

/* nút chọn dạng viên (chủ đề, lọc, sắp xếp) */
.st-key-trang_dien_dan [data-testid="stButtonGroup"] button, .st-key-dd_trang [data-testid="stButtonGroup"] button {{
    border-radius:999px !important; margin-right:6px !important; border:1.5px solid #E1E8DC !important; background:#fff !important;
    padding:4px 14px !important; min-height:36px !important; transition:all .2s ease !important; }}
.st-key-dd_trang [data-testid="stButtonGroup"] button p {{ font-weight:700 !important; font-size:.88rem !important; color:#4E5E48 !important; }}
.st-key-dd_trang [data-testid="stButtonGroup"] button:hover {{ border-color:#9BD17F !important; background:#F5FBF1 !important; }}
.st-key-dd_trang [data-testid="stButtonGroup"] button[kind="segmented_controlActive"],
.st-key-dd_trang [data-testid="stButtonGroup"] button[aria-checked="true"] {{ background:#E7F5DF !important; border-color:#46A033 !important; }}
.st-key-dd_trang [data-testid="stButtonGroup"] button[kind="segmented_controlActive"] p,
.st-key-dd_trang [data-testid="stButtonGroup"] button[aria-checked="true"] p {{ color:#1F5A17 !important; }}

/* thẻ bài viết */
[class*="st-key-dd_bai_"] {{ padding:18px 20px 12px !important; border-radius:24px !important; }}
[class*="st-key-dd_bai_"]:hover {{ box-shadow:0 20px 40px -28px rgba(30,60,30,.85); }}
.dd-bai-noi {{ font-size:1.02rem !important; }}
.dem-bai {{ display:flex; justify-content:space-between; font-size:.84rem; color:{CHU_PHU}; padding:2px 2px 8px;
    border-bottom:1px solid #EEF1EA; }}
.dem-tim i {{ display:inline-flex; align-items:center; justify-content:center; width:20px; height:20px; margin-right:6px;
    border-radius:50%; font-style:normal; font-size:.7rem; color:#fff; background:linear-gradient(135deg,#FF6B81,#E11D48); }}
.dem-tim.mo {{ font-style:italic; opacity:.8; }}
[class*="st-key-dd_hd_"] button {{ border:none !important; background:transparent !important; border-radius:12px !important;
    min-height:40px !important; transition:background .2s ease !important; }}
[class*="st-key-dd_hd_"] button p {{ font-weight:700 !important; color:#4E5E48 !important; }}
[class*="st-key-dd_hd_"] button:hover {{ background:#F2F6EF !important; }}
[class*="st-key-dd_hd_"] [class*="st-key-dd_tim_"] button:active {{ transform:scale(.96); }}
[class*="st-key-dd_khung_bl_"] {{ background:#FAFBF8; border-radius:18px; padding:10px 12px 4px; gap:.3rem !important; }}
[class*="st-key-dd_khung_bl_"] input {{ border-radius:999px !important; }}
/* nút ⋯: bỏ mũi tên nhỏ */
[data-testid="stPopover"] button svg {{ display:none !important; }}

/* cột phải */
.cot-phai {{ display:flex; flex-direction:column; gap:14px; position:sticky; top:70px; }}
.cp-the {{ background:#fff; border:1px solid #ECEFE8; border-radius:22px; padding:16px 18px;
    box-shadow:0 14px 30px -26px rgba(30,60,30,.75); }}
.cp-td {{ font-weight:900; color:{CHU}; margin-bottom:10px; font-size:1rem; }}
.cp-nb {{ padding:8px 0; border-top:1px dashed #E6ECE1; }} .cp-nb:first-of-type {{ border-top:none; padding-top:0; }}
.cp-nb b {{ display:block; font-size:.88rem; color:{CHU}; font-weight:700; line-height:1.4; }}
.cp-nb span {{ font-size:.74rem; color:{CHU_PHU}; }}
.cp-tv {{ display:flex; align-items:center; gap:10px; padding:5px 0; font-size:.88rem; font-weight:600; color:{CHU}; }}
.cp-trong {{ font-size:.85rem; color:{CHU_PHU}; }}
.noi-quy ol {{ margin:0; padding-left:18px; font-size:.84rem; color:#4E5E48; line-height:1.6; }}
.noi-quy {{ background:linear-gradient(180deg,#FFFDF5,#fff); border-color:#F3E6BF; }}
@media (max-width: 900px) {{ .cot-phai {{ position:static; }} }}
</style>""")



def dau_chi_tiet_sp(sp: dict) -> str:
    tt = ('<span class="ct-con">● Còn hàng</span>' if sp["con_hang"] and not sp.get("an")
          else '<span class="ct-het">● Tạm hết hàng</span>')
    return gon(f'<div class="ct-sp"><span class="dd-sp-dm ct-dm">{e(sp["danh_muc"])}</span>'
               f'<div class="ct-ten">{e(sp["ten"])}</div><div class="ct-mt">{chu_nguoi_dung(sp["mo_ta"])}</div>'
               f'<div class="ct-gia">{so(sp["gia"])}<small> đ / {e(sp["don_vi"])}</small></div>'
               f'<div class="ct-dong">{tt}' + (f'<span>🌱 Hợp với: <b>{e(sp["phu_hop"])}</b></span>' if sp["phu_hop"] else "")
               + '</div><div class="ct-cam">✅ Giá mẫu · 🚚 Giao tận nơi (chế độ thử) · 💬 Hỏi đáp trên Diễn đàn</div></div>')
