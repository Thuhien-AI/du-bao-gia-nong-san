# -*- coding: utf-8 -*-
"""
Kết nối cơ sở dữ liệu cho cả app.

- Có TURSO_DATABASE_URL + TURSO_AUTH_TOKEN (trong .streamlit/secrets.toml hoặc phần Secrets của
  Streamlit Cloud) -> dữ liệu lưu trên Turso (trên mạng, không mất khi web khởi động lại).
- Không có -> dùng file data/nguoi_dung.db trên máy như trước.

Kết nối Turso đi qua giao thức HTTP của Turso ("Hrana over HTTP", POST /v2/pipeline) và được làm cho
giống hệt sqlite3 của Python (execute, executemany, executescript, fetchone, fetchall, lastrowid,
row["ten_cot"], dict(row), with kn:, BEGIN IMMEDIATE/COMMIT/ROLLBACK), nên các file khác gần như
không phải sửa.
"""

import base64
import os
import re
import sqlite3
import threading
from pathlib import Path

_DA_LAM = set()            # việc chỉ cần làm 1 lần mỗi lần chạy web (tạo bảng...)
_KHOA = threading.Lock()


# ================================================================ Cấu hình
def _doc_bi_mat(ten: str) -> str:
    gia_tri = os.environ.get(ten, "")
    if gia_tri:
        return gia_tri.strip()
    try:
        import streamlit as st
        return str(st.secrets.get(ten, "") or "").strip()
    except Exception:
        pass
    # chạy ngoài Streamlit (vd. công cụ chuyển dữ liệu): đọc thẳng file secrets.toml
    f = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if f.exists():
        try:
            import tomllib
            return str(tomllib.loads(f.read_text(encoding="utf-8")).get(ten, "") or "").strip()
        except Exception:
            pass
    return ""


def cau_hinh_turso():
    """(url https, token) hoặc None nếu chưa cấu hình Turso."""
    url, token = _doc_bi_mat("TURSO_DATABASE_URL"), _doc_bi_mat("TURSO_AUTH_TOKEN")
    if not url or not token:
        return None
    url = re.sub(r"^(libsql|wss?)://", "https://", url).rstrip("/")
    return url, token


def dang_dung_turso() -> bool:
    return cau_hinh_turso() is not None


def ket_noi(file_csdl):
    """Mở kết nối: Turso nếu đã cấu hình, không thì file SQLite."""
    ch = cau_hinh_turso()
    if ch:
        return KetNoiTurso(*ch)
    Path(file_csdl).parent.mkdir(exist_ok=True)
    kn = sqlite3.connect(file_csdl)
    kn.row_factory = sqlite3.Row
    return kn


def mot_lan(khoa: str) -> bool:
    """True nếu việc `khoa` chưa làm trong lần chạy web này (dùng để tạo bảng 1 lần)."""
    with _KHOA:
        return khoa not in _DA_LAM


def da_lam(khoa: str):
    with _KHOA:
        _DA_LAM.add(khoa)


# ================================================================ Dòng kết quả giống sqlite3.Row
class Hang(tuple):
    def __new__(cls, gia_tri, ten_cot):
        h = super().__new__(cls, gia_tri)
        h._cot = ten_cot
        return h

    def __getitem__(self, k):
        if isinstance(k, str):
            try:
                return tuple.__getitem__(self, self._cot.index(k))
            except ValueError:
                raise IndexError(f"Không có cột {k}")
        return tuple.__getitem__(self, k)

    def keys(self):
        return list(self._cot)


class _ConTro:
    def __init__(self, cot=None, dong=None, lastrowid=None, rowcount=-1):
        self._cot = cot or []
        self._dong = [Hang(d, self._cot) for d in (dong or [])]
        self._i = 0
        self.lastrowid = lastrowid
        self.rowcount = rowcount
        self.description = tuple((c, None, None, None, None, None, None) for c in self._cot) or None

    def fetchone(self):
        if self._i >= len(self._dong):
            return None
        self._i += 1
        return self._dong[self._i - 1]

    def fetchall(self):
        con = self._dong[self._i:]
        self._i = len(self._dong)
        return con

    def __iter__(self):
        return iter(self.fetchall())


# ================================================================ Mã hoá giá trị theo giao thức Hrana
def _ma_hoa(v):
    if v is None:
        return {"type": "null"}
    if isinstance(v, bool):
        return {"type": "integer", "value": str(int(v))}
    if isinstance(v, int):
        return {"type": "integer", "value": str(v)}
    if isinstance(v, float):
        return {"type": "float", "value": v}
    if isinstance(v, (bytes, bytearray, memoryview)):
        return {"type": "blob", "base64": base64.b64encode(bytes(v)).decode().rstrip("=")}
    return {"type": "text", "value": str(v)}


def _giai_ma(o):
    t = o.get("type")
    if t == "null":
        return None
    if t == "integer":
        return int(o["value"])
    if t == "float":
        return float(o["value"])
    if t == "blob":
        b = o.get("base64", "")
        return base64.b64decode(b + "=" * (-len(b) % 4))
    return o.get("value")


def _loi(e: dict):
    thong_bao = e.get("message", "Lỗi cơ sở dữ liệu")
    ma = str(e.get("code", ""))
    if "CONSTRAINT" in ma.upper() or "constraint failed" in thong_bao:
        return sqlite3.IntegrityError(thong_bao)
    return sqlite3.OperationalError(thong_bao)


_PHIEN = None


def _phien():
    global _PHIEN
    if _PHIEN is None:
        import requests
        _PHIEN = requests.Session()
    return _PHIEN


# ================================================================ Kết nối Turso giống sqlite3.Connection
class KetNoiTurso:
    _cache_pragma = {}          # PRAGMA table_info(...) -> kết quả (dùng chung, xoá khi ALTER TABLE)
    _da_tao = set()             # câu CREATE ... IF NOT EXISTS đã chạy

    def __init__(self, url: str, token: str):
        self.url, self.token = url, token
        self.baton = None
        self.base_url = None
        self.row_factory = None
        self.isolation_level = None
        self.total_changes = 0

    # ---------- gửi yêu cầu
    def _gui(self, cac_cau: list, dong: bool):
        yeu_cau = [{"type": "execute", "stmt": {"sql": sql, "args": [_ma_hoa(v) for v in ts]}}
                   for sql, ts in cac_cau]
        if dong:
            yeu_cau.append({"type": "close"})
        dia_chi = (self.base_url or self.url) + "/v2/pipeline"
        tl = _phien().post(dia_chi, json={"baton": self.baton, "requests": yeu_cau},
                           headers={"Authorization": f"Bearer {self.token}"}, timeout=30)
        if tl.status_code >= 400:
            raise sqlite3.OperationalError(f"Turso trả lỗi {tl.status_code}: {tl.text[:300]}")
        du = tl.json()
        self.baton = None if dong else du.get("baton")
        self.base_url = None if dong else (du.get("base_url") or self.base_url)
        kq = []
        for r in du.get("results", [])[:len(cac_cau)]:
            if r.get("type") == "error":
                if self.baton and not dong:
                    pass
                raise _loi(r.get("error", {}))
            res = r["response"]["result"]
            cot = [c.get("name") for c in res.get("cols", [])]
            hang = [tuple(_giai_ma(o) for o in d) for d in res.get("rows", [])]
            rid = res.get("last_insert_rowid")
            kq.append(_ConTro(cot, hang, int(rid) if rid not in (None, "") else None,
                              int(res.get("affected_row_count") or 0)))
        return kq

    @property
    def in_transaction(self):
        return self.baton is not None

    def _chay(self, cac_cau: list):
        """Chạy danh sách (sql, tham_số). Trong giao dịch thì giữ kết nối mở (baton)."""
        dau = cac_cau[0][0].strip().upper() if cac_cau else ""
        cuoi = cac_cau[-1][0].strip().upper() if cac_cau else ""
        mo_gd = dau.startswith("BEGIN")
        ket_gd = cuoi.startswith(("COMMIT", "ROLLBACK", "END"))
        giu_mo = (self.in_transaction or mo_gd) and not ket_gd
        try:
            return self._gui(cac_cau, dong=not giu_mo)
        except sqlite3.OperationalError as loi:
            # BEGIN IMMEDIATE không được hỗ trợ -> dùng BEGIN thường
            if mo_gd and "IMMEDIATE" in dau and not self.in_transaction:
                cac_cau = [("BEGIN", ())] + cac_cau[1:]
                return self._gui(cac_cau, dong=not giu_mo)
            if self.in_transaction:
                self._dong_luong()
            raise
        except sqlite3.IntegrityError:
            raise

    def _dong_luong(self):
        if self.baton:
            try:
                self._gui([], dong=True)
            except Exception:
                pass
        self.baton = self.base_url = None

    # ---------- giống sqlite3
    def execute(self, sql: str, tham_so=()):
        s = sql.strip()
        hoa = s.upper()
        if hoa.startswith("CREATE") and "IF NOT EXISTS" in hoa and s in KetNoiTurso._da_tao:
            return _ConTro()
        m = re.match(r"PRAGMA\s+table_info\((\w+)\)", s, re.I)
        if m and m.group(1).lower() in KetNoiTurso._cache_pragma:
            c = KetNoiTurso._cache_pragma[m.group(1).lower()]
            return _ConTro(c[0], c[1])
        con_tro = self._chay([(s, tuple(tham_so or ()))])[0]
        if hoa.startswith("CREATE") and "IF NOT EXISTS" in hoa:
            KetNoiTurso._da_tao.add(s)
        if m:
            KetNoiTurso._cache_pragma[m.group(1).lower()] = (con_tro._cot, [tuple(d) for d in con_tro._dong])
        m2 = re.match(r"ALTER\s+TABLE\s+(\w+)", s, re.I)
        if m2:
            KetNoiTurso._cache_pragma.pop(m2.group(1).lower(), None)
        return con_tro

    def executemany(self, sql: str, ds_tham_so):
        ds = [(sql, tuple(t)) for t in ds_tham_so]
        tong = 0
        # gửi theo từng gói nhỏ (ảnh lớn) để không quá dung lượng 1 yêu cầu
        goi, co = [], 0
        for cau in ds:
            co += sum(len(v) for v in cau[1] if isinstance(v, (bytes, bytearray)))
            goi.append(cau)
            if len(goi) >= 50 or co > 3_000_000:
                tong += sum(c.rowcount for c in self._chay(goi))
                goi, co = [], 0
        if goi:
            tong += sum(c.rowcount for c in self._chay(goi))
        return _ConTro(rowcount=tong)

    def executescript(self, script: str):
        cac = [c.strip() for c in _tach_cau(script) if c.strip()]
        can = [c for c in cac if c not in KetNoiTurso._da_tao]
        if can:
            self._chay([(c, ()) for c in can])
            for c in can:
                if c.upper().startswith("CREATE") and "IF NOT EXISTS" in c.upper():
                    KetNoiTurso._da_tao.add(c)
        return _ConTro()

    def commit(self):
        if self.in_transaction:
            self._chay([("COMMIT", ())])

    def rollback(self):
        if self.in_transaction:
            try:
                self._chay([("ROLLBACK", ())])
            finally:
                self.baton = self.base_url = None

    def close(self):
        self._dong_luong()

    def __enter__(self):
        return self

    def __exit__(self, loai_loi, *_):
        if self.in_transaction:
            (self.rollback if loai_loi else self.commit)()
        return False


def _tach_cau(script: str):
    """Tách script thành từng câu lệnh (bỏ chú thích --)."""
    dong = [re.sub(r"--.*$", "", d) for d in script.splitlines()]
    return " \n".join(dong).split(";")
