# -*- coding: utf-8 -*-
"""
Dự báo giá nông sản bằng 3 mô hình, tự chọn mô hình tốt nhất cho từng chuỗi giá.

BA MÔ HÌNH (cả lúa, cà phê, hồ tiêu đều dùng đúng 3 mô hình này)
------------------------------------------------------------------
1. Holt – san bằng mũ có giảm xu hướng
   Bám theo mức giá gần nhất (ngày gần được coi trọng hơn), có xu hướng tăng/giảm nhẹ và
   xu hướng yếu dần khi dự báo xa. Hợp với giá "bậc thang": đứng yên nhiều ngày rồi nhảy bậc.
2. ARIMA(p,1,0) – mô hình chuỗi thời gian kinh điển
   Học quy luật "mức thay đổi hôm nay phụ thuộc mức thay đổi p ngày trước" (vd. cà phê tăng thì
   hay tăng tiếp, lúa tăng thì hay quay đầu). p (1–7) được chọn tự động theo tiêu chí AIC.
   Tính trên log giá nên dùng được khi giá tăng gấp đôi.
3. Random Forest – học máy
   Nhiều "cây quyết định" học từ % thay đổi của 1–30 ngày trước, bắt được quy luật không thẳng
   (vd. sau cú nhảy lớn thì hay đứng yên). Dự báo nhiều ngày bằng cách đoán từng ngày nối tiếp.

CHỌN MÔ HÌNH TỐT NHẤT ("kiểm tra ngược")
-----------------------------------------
Giả vờ đang ở một ngày trong 6 tháng gần nhất, cho cả 3 mô hình dự báo 30 ngày tiếp theo rồi so
với giá thật. Lặp lại nhiều lần. Mô hình có sai số trung bình (1–30 ngày) nhỏ nhất được chọn.
Cách "giá giữ nguyên như hôm nay" được tính kèm để làm MỐC THAM KHẢO (không phải mô hình).

RIÊNG CÀ PHÊ – DỰ BÁO "NGÀY MAI" CÓ THÊM GIÁ LONDON
---------------------------------------------------
Giá Robusta sàn London phiên hôm trước ảnh hưởng mạnh tới giá trong nước hôm sau (tương quan ~0,7).
ARIMA và Random Forest được cho thêm thông tin này (Holt không nhận thêm thông tin ngoài).
Mô hình nào sai ít nhất khi dự báo 1 ngày (kiểm tra ngược) thì được dùng cho "ngày mai".
Chỉ dùng khi đã có giá London của phiên cần thiết; nếu chưa có thì dùng mô hình thường.
"""

import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

TEN_MO_HINH = ["Holt", "ARIMA", "Random Forest"]
SO_NGAY_DU_BAO = 30
SO_NGAY_KIEM_TRA = 180      # kiểm tra ngược trong 6 tháng gần nhất
BUOC_KIEM_TRA = 15          # cứ 15 ngày thử một lần
Z_90 = 1.645                # hệ số cho vùng 90%

# Random Forest: các độ trễ (ngày) dùng làm đầu vào
TRE = [1, 2, 3, 4, 5, 6, 7, 14, 21, 30]


# ================================================================ 1. HOLT
def _holt_chay(y, a, b, p):
    muc, xh, sai = y[0], 0.0, 0.0
    for v in y[1:]:
        doan = muc + p * xh
        sai += (v - doan) ** 2
        moi = a * v + (1 - a) * doan
        xh = b * (moi - muc) + (1 - b) * p * xh
        muc = moi
    return muc, xh, sai


def holt_hoc(y):
    """Thử nhiều bộ tham số, chọn bộ dự báo 'ngày mai' sát nhất trên 1 năm gần nhất."""
    y = y[-365:]
    tot, sai_min = (0.5, 0.0, 0.9), np.inf
    for a in np.arange(0.1, 1.01, 0.1):
        for b in (0.0, 0.02, 0.05, 0.1, 0.2):
            for p in (0.8, 0.9, 0.95, 0.98):
                sai = _holt_chay(y, a, b, p)[2]
                if sai < sai_min:
                    tot, sai_min = (round(float(a), 2), b, p), sai
    return tot


def holt_du_bao(y, so_ngay, tham_so, ngoai_tiep=None):
    a, b, p = tham_so
    muc, xh, _ = _holt_chay(y[-400:], a, b, p)
    return muc + np.cumsum(p ** np.arange(1, so_ngay + 1)) * xh


# ================================================================ 2. ARIMA(p,1,0) trên log giá
def arima_hoc(y, ngoai=None, p_max=7):
    """
    Hồi quy log-thay-đổi hôm nay theo log-thay-đổi p ngày trước (bình phương nhỏ nhất),
    chọn p theo AIC. ngoai (tuỳ chọn): mảng cùng độ dài với các log-thay-đổi, NaN = thiếu.
    """
    dl = np.diff(np.log(y[-731:]))
    nx = None if ngoai is None else np.asarray(ngoai, dtype=float)[-len(dl):]
    tot = None
    for p in range(1, p_max + 1):
        m = len(dl)
        X = np.column_stack([dl[p - k - 1:m - k - 1] for k in range(p)])
        if nx is not None:
            X = np.column_stack([X, nx[p:]])
        Y = dl[p:]
        ok = ~np.isnan(X).any(axis=1)
        X, Y = X[ok], Y[ok]
        if len(Y) < 60:
            continue
        he_so, *_ = np.linalg.lstsq(X, Y, rcond=None)
        du = Y - X @ he_so
        aic = len(Y) * np.log(du @ du / len(Y) + 1e-18) + 2 * X.shape[1]
        if tot is None or aic < tot[0]:
            tot = (aic, p, he_so)
    if tot is None:
        return 1, np.zeros(1 + (ngoai is not None))
    return tot[1], tot[2]


def arima_du_bao(y, so_ngay, tham_so, ngoai_tiep=None):
    """ngoai_tiep: giá trị bên ngoài cho ngày đầu tiên (chỉ khi mô hình có giá London)."""
    p, he_so = tham_so
    dl = list(np.diff(np.log(y[-(p + 1):])))
    muc, ra = np.log(y[-1]), []
    for k in range(so_ngay):
        x = [dl[-1 - i] for i in range(p)]
        if len(he_so) > p:
            x.append(ngoai_tiep if (k == 0 and ngoai_tiep is not None) else 0.0)
        buoc = float(np.dot(he_so, x))
        dl.append(buoc)
        muc += buoc
        ra.append(np.exp(muc))
    return np.array(ra)


# ================================================================ 3. RANDOM FOREST
def _dac_trung(dl, i):
    """Đầu vào để đoán log-thay-đổi ở vị trí i (chỉ dùng dữ liệu trước i)."""
    return [dl[i - l] for l in TRE] + [dl[i - 7:i].mean(), dl[i - 30:i].mean(), dl[i - 30:i].std()]


def rf_hoc(y, ngoai=None):
    from sklearn.ensemble import RandomForestRegressor
    dl = np.diff(np.log(y[-901:]))
    nx = None if ngoai is None else np.asarray(ngoai, dtype=float)[-len(dl):]
    X, Y = [], []
    for i in range(max(TRE), len(dl)):
        x = _dac_trung(dl, i)
        if nx is not None:
            if np.isnan(nx[i]):
                continue
            x.append(nx[i])
        X.append(x)
        Y.append(dl[i])
    mh = RandomForestRegressor(n_estimators=100, max_depth=6, min_samples_leaf=5,
                               n_jobs=-1, random_state=0)
    mh.fit(np.array(X), np.array(Y))
    mh.n_jobs = 1   # dự đoán từng dòng nhanh hơn khi không chia luồng
    return mh


def rf_du_bao(y, so_ngay, mh, ngoai_tiep=None):
    dl = list(np.diff(np.log(y[-(max(TRE) + 2):])))
    muc, ra = y[-1], []
    co_ngoai = mh.n_features_in_ > len(TRE) + 3
    for k in range(so_ngay):
        a = np.array(dl)
        x = _dac_trung(a, len(a))
        if co_ngoai:
            x.append(ngoai_tiep if (k == 0 and ngoai_tiep is not None) else 0.0)
        buoc = float(mh.predict(np.array([x]))[0])
        dl.append(buoc)
        muc *= np.exp(buoc)
        ra.append(muc)
    return np.array(ra)


MO_HINH = {
    "Holt": (holt_hoc, holt_du_bao),
    "ARIMA": (arima_hoc, arima_du_bao),
    "Random Forest": (rf_hoc, rf_du_bao),
}


# ================================================================ Giá London cho cà phê
def _gia_london(the_gioi):
    gia = the_gioi.dropna(subset=["robusta"]).set_index("ngay")["robusta"]
    return gia[~gia.index.duplicated()].sort_index()


def chuoi_london(ngay: pd.DatetimeIndex, the_gioi: pd.DataFrame) -> np.ndarray:
    """
    Phần tử thứ i ứng với log-thay-đổi giá trong nước từ ngày i đến ngày i+1 (ngày d = ngay[i+1]):
    = log-thay-đổi giá Robusta London giữa phiên ghi ngày d-1 và d-2. NaN nếu thiếu số liệu.
    (Phiên London ngày d-1 đóng cửa vào tối d-1 giờ VN, trước khi giá trong nước ngày d được chốt.)
    """
    if the_gioi is None or the_gioi.empty:
        return np.full(len(ngay) - 1, np.nan)
    gia = _gia_london(the_gioi)
    lon = np.log(gia)
    r = (lon - lon.shift(1)).where(gia.index.to_series().diff().dt.days == 1)  # 2 ngày liền nhau
    return r.reindex(ngay[1:] - pd.Timedelta(days=1)).to_numpy(dtype=float)


def london_cho_ngay_mai(ngay_cuoi: pd.Timestamp, the_gioi: pd.DataFrame):
    """Log-thay-đổi London phiên ghi ngày 'ngay_cuoi' so với hôm trước -> dùng cho ngày mai."""
    if the_gioi is None or the_gioi.empty:
        return None
    gia = _gia_london(the_gioi)
    truoc = ngay_cuoi - pd.Timedelta(days=1)
    if ngay_cuoi in gia.index and truoc in gia.index:
        return float(np.log(gia[ngay_cuoi] / gia[truoc]))
    return None


# ================================================================ Kết quả
@dataclass
class KetQuaDuBao:
    bang: pd.DataFrame                 # cột: ngay, du_bao, thap, cao (30 ngày)
    mo_hinh_chon: str                  # tên mô hình tốt nhất
    so_sanh: pd.DataFrame              # mỗi dòng 1 mô hình: sai số 1 / 7 / 30 ngày / trung bình (%)
    sai_so_theo_ngay: np.ndarray       # % sai trung bình của mô hình được chọn, theo từng ngày
    giu_nguyen_theo_ngay: np.ndarray   # như trên cho cách "giá giữ nguyên"
    so_lan_kiem_tra: int
    mo_ta_tham_so: str = ""
    ngay_mai: dict = field(default_factory=dict)   # (cà phê) dự báo ngày mai có giá London


def _mo_ta(ten, ts):
    if ten == "Holt":
        a, b, p = ts
        return f"α = {a}, β = {b}, φ = {p}"
    if ten == "ARIMA":
        p, he_so = ts
        return f"p = {p}, nhìn lại {p} ngày" + (", có giá London" if len(he_so) > p else "")
    return f"{ts.n_estimators} cây, độ sâu tối đa {ts.max_depth}"


# ================================================================ Hàm chính
def du_bao(chuoi: pd.DataFrame, so_ngay: int = SO_NGAY_DU_BAO,
           the_gioi: pd.DataFrame = None) -> KetQuaDuBao:
    """
    chuoi    : bảng có cột 'ngay' và 'gia', mỗi ngày một dòng (đã làm sạch).
    the_gioi : (chỉ cà phê) bảng giá thế giới từ du_lieu.doc_gia_the_gioi().
    """
    y = chuoi["gia"].to_numpy(dtype=float)
    ngay = pd.DatetimeIndex(chuoi["ngay"])
    n = len(y)
    if n < 120:
        raise ValueError("Cần ít nhất 120 ngày dữ liệu để chạy 3 mô hình.")

    H = SO_NGAY_DU_BAO
    bat_dau = max(60, n - SO_NGAY_KIEM_TRA - H)
    cac_goc = list(range(bat_dau, n - H + 1, BUOC_KIEM_TRA)) or [n - H]

    # ---- Kiểm tra ngược cho 3 mô hình + "giữ nguyên"
    sai = {ten: [] for ten in TEN_MO_HINH + ["Giữ nguyên"]}
    ts_holt = holt_hoc(y[:cac_goc[0]])          # Holt: học tham số 1 lần trước giai đoạn thử
    for g in cac_goc:
        qua_khu, that = y[:g], y[g:g + H]
        doan = {
            "Holt": holt_du_bao(qua_khu, H, ts_holt),
            "ARIMA": arima_du_bao(qua_khu, H, arima_hoc(qua_khu)),
            "Random Forest": rf_du_bao(qua_khu, H, rf_hoc(qua_khu)),
            "Giữ nguyên": np.full(H, qua_khu[-1]),
        }
        for ten, d in doan.items():
            sai[ten].append((that - d) / that)          # sai số tương đối có dấu
    sai = {ten: np.array(v) for ten, v in sai.items()}

    def tom_tat(ten):
        a = np.abs(sai[ten]) * 100
        return {"Mô hình": ten, "1 ngày": a[:, 0].mean(), "7 ngày": a[:, 6].mean(),
                "30 ngày": a[:, 29].mean(), "Trung bình": a.mean()}

    so_sanh = pd.DataFrame([tom_tat(t) for t in TEN_MO_HINH + ["Giữ nguyên"]])
    mo_hinh_chon = min(TEN_MO_HINH, key=lambda t: np.abs(sai[t]).mean())
    so_sanh["Được chọn"] = so_sanh["Mô hình"] == mo_hinh_chon

    # ---- Học lại mô hình được chọn trên toàn bộ dữ liệu và dự báo
    hoc, doan_ham = MO_HINH[mo_hinh_chon]
    ts_chon = hoc(y)
    gia_du_bao = doan_ham(y, so_ngay, ts_chon)

    # ---- Vùng sai số 90% từ chính các lần sai của mô hình được chọn
    do_lech = np.maximum.accumulate(sai[mo_hinh_chon].std(axis=0) * Z_90)[:so_ngay]
    thap, cao = gia_du_bao * (1 - do_lech), gia_du_bao * (1 + do_lech)

    # ---- Cà phê: dự báo ngày mai có giá London
    ngay_mai = {}
    if the_gioi is not None and not the_gioi.empty:
        ngay_mai = _ngay_mai_london(y, ngay, the_gioi, cac_goc[0], ts_holt)
        if ngay_mai.get("dung"):
            gia_du_bao[0] = ngay_mai["gia"]
            thap[0] = ngay_mai["gia"] * (1 - ngay_mai["do_lech"])
            cao[0] = ngay_mai["gia"] * (1 + ngay_mai["do_lech"])

    bang = pd.DataFrame({
        "ngay": pd.date_range(ngay[-1] + pd.Timedelta(days=1), periods=so_ngay, freq="D"),
        "du_bao": np.round(gia_du_bao, 0),
        "thap": np.round(thap, 0),
        "cao": np.round(cao, 0),
    })
    sai_so_theo_ngay = np.abs(sai[mo_hinh_chon]).mean(axis=0) * 100
    if ngay_mai.get("dung"):
        sai_so_theo_ngay[0] = ngay_mai["sai_so"][ngay_mai["mo_hinh"]]
    return KetQuaDuBao(
        bang=bang, mo_hinh_chon=mo_hinh_chon, so_sanh=so_sanh,
        sai_so_theo_ngay=sai_so_theo_ngay,
        giu_nguyen_theo_ngay=np.abs(sai["Giữ nguyên"]).mean(axis=0) * 100,
        so_lan_kiem_tra=len(cac_goc), mo_ta_tham_so=_mo_ta(mo_hinh_chon, ts_chon),
        ngay_mai=ngay_mai,
    )


def _ngay_mai_london(y, ngay, the_gioi, bat_dau, ts_holt):
    """
    Kiểm tra ngược riêng cho dự báo 1 ngày (có giá London), chọn mô hình tốt nhất cho ngày mai.
    Cứ 15 ngày học lại mô hình, rồi đoán từng ngày trong 15 ngày đó (biết giá thật đến hôm trước).
    Ngày nào thiếu giá London thì bỏ qua.
    """
    lon = chuoi_london(ngay, the_gioi)          # lon[i] ảnh hưởng tới log-thay-đổi thứ i
    n = len(y)
    loi = {"Holt": [], "ARIMA": [], "Random Forest": [],
           "ARIMA (không London)": [], "Random Forest (không London)": []}
    for g in range(bat_dau, n, BUOC_KIEM_TRA):
        can_doan = [d for d in range(g, min(g + BUOC_KIEM_TRA, n)) if not np.isnan(lon[d - 1])]
        if not can_doan:
            continue
        ts_a, ts_a0 = arima_hoc(y[:g], ngoai=lon[:g - 1]), arima_hoc(y[:g])
        mh_r, mh_r0 = rf_hoc(y[:g], ngoai=lon[:g - 1]), rf_hoc(y[:g])
        for d in can_doan:
            qua_khu, that, x = y[:d], y[d], lon[d - 1]
            loi["Holt"].append((that - holt_du_bao(qua_khu, 1, ts_holt)[0]) / that)
            loi["ARIMA"].append((that - arima_du_bao(qua_khu, 1, ts_a, x)[0]) / that)
            loi["Random Forest"].append((that - rf_du_bao(qua_khu, 1, mh_r, x)[0]) / that)
            loi["ARIMA (không London)"].append((that - arima_du_bao(qua_khu, 1, ts_a0)[0]) / that)
            loi["Random Forest (không London)"].append(
                (that - rf_du_bao(qua_khu, 1, mh_r0)[0]) / that)

    so_ngay_thu = len(loi["Holt"])
    if so_ngay_thu < 20:
        return {"dung": False, "so_ngay_thu": so_ngay_thu,
                "ly_do": "chưa đủ ngày có giá London để kiểm tra"}
    sai_so = {k: float(np.mean(np.abs(v)) * 100) for k, v in loi.items()}
    tot = min(TEN_MO_HINH, key=lambda t: sai_so[t])
    ket_qua = {"mo_hinh": tot, "sai_so": sai_so, "so_ngay_thu": so_ngay_thu,
               "do_lech": float(np.std(loi[tot]) * Z_90), "dung": False}

    x_moi = london_cho_ngay_mai(ngay[-1], the_gioi)
    if x_moi is None:
        ket_qua["ly_do"] = f"chưa có giá London phiên ghi ngày {ngay[-1]:%d/%m/%Y}"
        return ket_qua
    if tot == "Holt":
        gia = holt_du_bao(y, 1, holt_hoc(y))[0]
    elif tot == "ARIMA":
        gia = arima_du_bao(y, 1, arima_hoc(y, ngoai=lon), x_moi)[0]
    else:
        gia = rf_du_bao(y, 1, rf_hoc(y, ngoai=lon), x_moi)[0]
    ket_qua.update({"dung": True, "gia": float(gia), "london_thay_doi": float(np.expm1(x_moi) * 100)})
    return ket_qua


if __name__ == "__main__":
    # Chạy thử:  python du_bao.py
    import time
    from du_lieu import doc_du_lieu, doc_gia_the_gioi, lay_chuoi_gia

    df = doc_du_lieu()
    tg = doc_gia_the_gioi()
    for (ns, lo, kv), _ in df.groupby(["nong_san", "loai", "khu_vuc"]):
        t0 = time.time()
        kq = du_bao(lay_chuoi_gia(df, ns, lo, kv), 30, tg if ns == "Cà phê" else None)
        ss = kq.so_sanh.set_index("Mô hình")["Trung bình"].round(2).to_dict()
        print(f"{ns:8} {lo[:18]:18} {kv[:22]:22} | chọn: {kq.mo_hinh_chon:13} | {ss} "
              f"| {time.time() - t0:.1f}s", flush=True)
        if kq.ngay_mai:
            nm = kq.ngay_mai
            print("     ngày mai (London):", nm.get("mo_hinh"), nm.get("dung"), nm.get("ly_do", ""),
                  nm.get("so_ngay_thu"), {k: round(v, 3) for k, v in nm.get("sai_so", {}).items()},
                  flush=True)
