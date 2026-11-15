# -*- coding: utf-8 -*-
"""
CHUYỂN DỮ LIỆU LÊN TURSO (chạy 1 lần)

Chép toàn bộ data/nguoi_dung.db trên máy (tài khoản, xu, VIP, nông trại, diễn đàn, chợ...) lên Turso.

Cách chạy (trong VS Code, mở Terminal):
    .venv\\Scripts\\activate
    python chuyen_du_lieu_len_turso.py

Trước đó phải điền TURSO_DATABASE_URL và TURSO_AUTH_TOKEN vào .streamlit/secrets.toml.
Chạy lại nhiều lần cũng không sao: dòng nào đã có sẽ được ghi đè bằng bản trên máy, không bị nhân đôi.
"""

import sqlite3
import sys
from pathlib import Path

import csdl

FILE_CSDL = Path(__file__).parent / "data" / "nguoi_dung.db"


def main():
    ch = csdl.cau_hinh_turso()
    if not ch:
        print("❌ Chưa có TURSO_DATABASE_URL và TURSO_AUTH_TOKEN trong .streamlit/secrets.toml.")
        sys.exit(1)
    if not FILE_CSDL.exists():
        print(f"❌ Không thấy file {FILE_CSDL}.")
        sys.exit(1)
    goc = sqlite3.connect(FILE_CSDL)
    dich = csdl.KetNoiTurso(*ch)
    print(f"Đang kết nối Turso: {ch[0]}")
    dich.execute("SELECT 1")
    print("✅ Kết nối được Turso.\n")

    bang = goc.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                       "ORDER BY name").fetchall()
    chi_muc = goc.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL").fetchall()

    # 1) tạo bảng giống hệt trên máy
    for ten, sql in bang:
        sql_tao = sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1) if "IF NOT EXISTS" not in sql else sql
        dich.execute(sql_tao)
        # bảng đã có trên Turso từ trước nhưng thiếu cột -> thêm cột
        cot_dich = {r[1] for r in dich.execute(f"PRAGMA table_info({ten})")}
        for r in goc.execute(f"PRAGMA table_info({ten})"):
            if r[1] not in cot_dich:
                kieu = r[2] or ""
                mac_dinh = f" DEFAULT {r[4]}" if r[4] is not None else ""
                dich.execute(f"ALTER TABLE {ten} ADD COLUMN {r[1]} {kieu}{mac_dinh}")
    for ten, sql in chi_muc:
        dich.execute(sql.replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ", 1)
                     .replace("CREATE UNIQUE INDEX ", "CREATE UNIQUE INDEX IF NOT EXISTS ", 1))

    # 2) chép dữ liệu từng bảng
    tong = 0
    for ten, _ in bang:
        cot = [r[1] for r in goc.execute(f"PRAGMA table_info({ten})")]
        hang = goc.execute(f"SELECT {', '.join(cot)} FROM {ten}").fetchall()
        if not hang:
            print(f"  · {ten}: trống")
            continue
        dich.executemany(f"INSERT OR REPLACE INTO {ten} ({', '.join(cot)}) VALUES ({', '.join('?' * len(cot))})", hang)
        so_tren_turso = dich.execute(f"SELECT COUNT(*) FROM {ten}").fetchone()[0]
        print(f"  ✓ {ten}: chép {len(hang)} dòng (trên Turso hiện có {so_tren_turso})")
        tong += len(hang)
    print(f"\n🎉 Xong! Đã chép {tong} dòng lên Turso.")
    print("Từ giờ khi secrets.toml có thông tin Turso, app (trên máy và trên mạng) đều dùng chung dữ liệu Turso.")


if __name__ == "__main__":
    main()
