import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'selapan.db')

# ─────────────────────────────────────────────
#  ROLE DEFINITIONS
#  'admin'  → bisa lihat semua data, kelola user, lihat laporan
#  'guru'   → bisa isi jurnal, lihat laporan kelas sendiri
#  'siswa'  → bisa presensi, isi jurnal harian sendiri
# ─────────────────────────────────────────────
ROLE_PERMISSIONS = {
    'admin': ['dashboard', 'presensi', 'jurnal', 'daftar_jurnal', 'laporan', 'kelola_user'],
    'guru':  ['dashboard', 'presensi', 'jurnal', 'daftar_jurnal', 'laporan'],
    'siswa': ['dashboard', 'presensi', 'jurnal', 'daftar_jurnal'],
}

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Auth ──────────────────────────────────────
def get_user_by_username(username):
    conn = get_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return user

def verify_password(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None

def has_permission(role, page):
    return page in ROLE_PERMISSIONS.get(role, [])

# ── Presensi ──────────────────────────────────
def simpan_presensi(user_id, tanggal, status, keterangan=''):
    conn = get_connection()
    existing = conn.execute(
        'SELECT id FROM presensi WHERE user_id=? AND tanggal=?', (user_id, tanggal)
    ).fetchone()
    if existing:
        conn.execute(
            'UPDATE presensi SET status=?, keterangan=? WHERE user_id=? AND tanggal=?',
            (status, keterangan, user_id, tanggal)
        )
    else:
        conn.execute(
            'INSERT INTO presensi (user_id, tanggal, status, keterangan) VALUES (?,?,?,?)',
            (user_id, tanggal, status, keterangan)
        )
    conn.commit()
    conn.close()

def get_presensi_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM presensi WHERE user_id=? ORDER BY tanggal DESC', (user_id,)
    ).fetchall()
    conn.close()
    return rows

def get_all_presensi():
    conn = get_connection()
    rows = conn.execute('''
        SELECT p.*, u.nama, u.kelas, u.role
        FROM presensi p JOIN users u ON p.user_id = u.id
        ORDER BY p.tanggal DESC
    ''').fetchall()
    conn.close()
    return rows

# ── Jurnal ────────────────────────────────────
def simpan_jurnal(user_id, tanggal, kegiatan, hasil, kendala, solusi):
    conn = get_connection()
    existing = conn.execute(
        'SELECT id FROM jurnal WHERE user_id=? AND tanggal=?', (user_id, tanggal)
    ).fetchone()
    if existing:
        conn.execute(
            '''UPDATE jurnal SET kegiatan=?, hasil=?, kendala=?, solusi=?
               WHERE user_id=? AND tanggal=?''',
            (kegiatan, hasil, kendala, solusi, user_id, tanggal)
        )
    else:
        conn.execute(
            '''INSERT INTO jurnal (user_id, tanggal, kegiatan, hasil, kendala, solusi)
               VALUES (?,?,?,?,?,?)''',
            (user_id, tanggal, kegiatan, hasil, kendala, solusi)
        )
    conn.commit()
    conn.close()

def get_jurnal_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM jurnal WHERE user_id=? ORDER BY tanggal DESC', (user_id,)
    ).fetchall()
    conn.close()
    return rows

def get_all_jurnal():
    conn = get_connection()
    rows = conn.execute('''
        SELECT j.*, u.nama, u.kelas, u.role
        FROM jurnal j JOIN users u ON j.user_id = u.id
        ORDER BY j.tanggal DESC
    ''').fetchall()
    conn.close()
    return rows

# ── Laporan ───────────────────────────────────
def get_rekap_presensi(user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute('''
            SELECT status, COUNT(*) as jumlah
            FROM presensi WHERE user_id=?
            GROUP BY status
        ''', (user_id,)).fetchall()
    else:
        rows = conn.execute('''
            SELECT u.nama, u.kelas,
                   SUM(CASE WHEN p.status='Hadir' THEN 1 ELSE 0 END) as hadir,
                   SUM(CASE WHEN p.status='Sakit' THEN 1 ELSE 0 END) as sakit,
                   SUM(CASE WHEN p.status='Izin'  THEN 1 ELSE 0 END) as izin,
                   SUM(CASE WHEN p.status='Alpha' THEN 1 ELSE 0 END) as alpha,
                   COUNT(*) as total
            FROM users u LEFT JOIN presensi p ON u.id=p.user_id
            WHERE u.role='siswa'
            GROUP BY u.id
            ORDER BY u.kelas, u.nama
        ''').fetchall()
    conn.close()
    return rows

def get_all_users():
    conn = get_connection()
    rows = conn.execute(
        'SELECT id, username, nama, kelas, role FROM users ORDER BY role, nama'
    ).fetchall()
    conn.close()
    return rows

def get_stats_dashboard(user_id, role):
    conn = get_connection()
    stats = {}
    if role == 'admin':
        stats['total_siswa']  = conn.execute("SELECT COUNT(*) FROM users WHERE role='siswa'").fetchone()[0]
        stats['total_guru']   = conn.execute("SELECT COUNT(*) FROM users WHERE role='guru'").fetchone()[0]
        stats['total_presensi'] = conn.execute("SELECT COUNT(*) FROM presensi").fetchone()[0]
        stats['total_jurnal'] = conn.execute("SELECT COUNT(*) FROM jurnal").fetchone()[0]
    else:
        stats['hadir'] = conn.execute(
            "SELECT COUNT(*) FROM presensi WHERE user_id=? AND status='Hadir'", (user_id,)
        ).fetchone()[0]
        stats['jurnal'] = conn.execute(
            "SELECT COUNT(*) FROM jurnal WHERE user_id=?", (user_id,)
        ).fetchone()[0]
        stats['total_presensi'] = conn.execute(
            "SELECT COUNT(*) FROM presensi WHERE user_id=?", (user_id,)
        ).fetchone()[0]
    conn.close()
    return stats
