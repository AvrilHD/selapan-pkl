from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import database as db
from datetime import date

app = Flask(__name__)
app.secret_key = 'smkn8-malang-selapan-2025-secret'

# ─────────────────────────────────────────────
#  Helper / Decorators
# ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in roles:
                flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

def get_current_user():
    return {
        'id':       session.get('user_id'),
        'username': session.get('username'),
        'nama':     session.get('nama'),
        'role':     session.get('role'),
        'kelas':    session.get('kelas'),
    }

# ─────────────────────────────────────────────
#  Auth
# ─────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = db.verify_password(username, password)
        if user:
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['nama']     = user['nama']
            session['role']     = user['role']
            session['kelas']    = user['kelas']
            flash(f'Selamat datang, {user["nama"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('login'))

# ─────────────────────────────────────────────
#  Dashboard
# ─────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    user  = get_current_user()
    stats = db.get_stats_dashboard(user['id'], user['role'])
    return render_template('dashboard.html', user=user, stats=stats,
                           today=date.today().isoformat())

# ─────────────────────────────────────────────
#  Presensi
# ─────────────────────────────────────────────
@app.route('/presensi', methods=['GET', 'POST'])
@login_required
def presensi():
    user = get_current_user()
    today = date.today().isoformat()

    if request.method == 'POST':
        tanggal    = request.form.get('tanggal', today)
        status     = request.form.get('status')
        keterangan = request.form.get('keterangan', '')
        db.simpan_presensi(user['id'], tanggal, status, keterangan)
        flash('Presensi berhasil disimpan!', 'success')
        return redirect(url_for('presensi'))

    # Admin & guru lihat semua; siswa lihat milik sendiri
    if user['role'] in ('admin', 'guru'):
        data = db.get_all_presensi()
    else:
        data = db.get_presensi_user(user['id'])

    return render_template('presensi.html', user=user, data=data, today=today)

# ─────────────────────────────────────────────
#  Jurnal
# ─────────────────────────────────────────────
@app.route('/jurnal', methods=['GET', 'POST'])
@login_required
def jurnal():
    user  = get_current_user()
    today = date.today().isoformat()

    if request.method == 'POST':
        tanggal  = request.form.get('tanggal', today)
        kegiatan = request.form.get('kegiatan', '')
        hasil    = request.form.get('hasil', '')
        kendala  = request.form.get('kendala', '')
        solusi   = request.form.get('solusi', '')
        db.simpan_jurnal(user['id'], tanggal, kegiatan, hasil, kendala, solusi)
        flash('Jurnal berhasil disimpan!', 'success')
        return redirect(url_for('daftar_jurnal'))

    return render_template('jurnal.html', user=user, today=today)

# ─────────────────────────────────────────────
#  Daftar Jurnal
# ─────────────────────────────────────────────
@app.route('/daftar-jurnal')
@login_required
def daftar_jurnal():
    user = get_current_user()
    if user['role'] in ('admin', 'guru'):
        data = db.get_all_jurnal()
    else:
        data = db.get_jurnal_user(user['id'])
    return render_template('daftar_jurnal.html', user=user, data=data)

# ─────────────────────────────────────────────
#  Laporan  (admin & guru only)
# ─────────────────────────────────────────────
@app.route('/laporan')
@login_required
@role_required('admin', 'guru')
def laporan():
    user  = get_current_user()
    rekap = db.get_rekap_presensi()
    semua = db.get_all_presensi()
    return render_template('laporan.html', user=user, rekap=rekap, semua=semua)

# ─────────────────────────────────────────────
#  Run
# ─────────────────────────────────────────────
if __name__ == '__main__':
    import os
    # Buat DB otomatis kalau belum ada
    if not os.path.exists('selapan.db'):
        import create_db
        create_db.create_db()
    app.run(debug=True)
