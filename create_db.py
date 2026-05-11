"""
Jalankan sekali untuk membuat database dan data awal:
    python create_db.py
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'selapan.db')

def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            nama     TEXT    NOT NULL,
            kelas    TEXT,
            role     TEXT    NOT NULL DEFAULT 'siswa'
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS presensi (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            tanggal     TEXT    NOT NULL,
            status      TEXT    NOT NULL,
            keterangan  TEXT    DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS jurnal (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            tanggal  TEXT    NOT NULL,
            kegiatan TEXT    NOT NULL,
            hasil    TEXT,
            kendala  TEXT,
            solusi   TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()

    users = [
        ('admin',   generate_password_hash('admin123'),    'Administrator',   None,        'admin'),
        ('bu_sari', generate_password_hash('guru123'),     'Bu Sari Dewi',    None,        'guru'),
        ('pak_adi', generate_password_hash('guru123'),     'Pak Adi Santoso', None,        'guru'),
        ('pak_eko', generate_password_hash('ekoagus123'),  'Pak Eko',         None,        'guru'),
        ('budi',    generate_password_hash('siswa123'),    'Budi Prasetyo',   'XII RPL 1', 'siswa'),
        ('ani',     generate_password_hash('siswa123'),    'Ani Kurniawati',  'XII RPL 1', 'siswa'),
        ('dika',    generate_password_hash('siswa123'),    'Dika Ramadhan',   'XII TKJ 1', 'siswa'),
        ('siti',    generate_password_hash('siswa123'),    'Siti Rahayu',     'XII TKJ 1', 'siswa'),
        ('rizky',   generate_password_hash('siswa123'),    'Rizky Hidayat',   'XII MM 1',  'siswa'),
        ('javier',  generate_password_hash('Javier E.G.'),'Javier',          'XII RPL 1', 'siswa'),
    ]

    for u in users:
        try:
            conn.execute(
                'INSERT INTO users (username,password,nama,kelas,role) VALUES (?,?,?,?,?)', u
            )
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print("✅ Database berhasil dibuat: selapan.db")
    print("\n📋 Akun yang tersedia:")
    print("  ADMIN  → username: admin     | password: admin123")
    print("  GURU   → username: bu_sari   | password: guru123")
    print("  GURU   → username: pak_adi   | password: guru123")
    print("  GURU   → username: pak_eko   | password: ekoagus123")
    print("  SISWA  → username: budi      | password: siswa123")
    print("  SISWA  → username: ani       | password: siswa123")
    print("  SISWA  → username: dika      | password: siswa123")
    print("  SISWA  → username: siti      | password: siswa123")
    print("  SISWA  → username: rizky     | password: siswa123")
    print("  SISWA  → username: javier    | password: Javier E.G.")

if __name__ == '__main__':
    create_db()
