# 🏫 Selapan PKL — SMKN 8 Malang

Sistem Elektronik Laporan Praktek Kerja Lapangan

## 📁 Struktur Project
```
selapan_project/
├── app.py              ← Main Flask app + routing
├── database.py         ← Database + aturan role
├── create_db.py        ← Script buat DB & data awal
├── requirements.txt    ← Library Python
├── render.yaml         ← Config deploy ke Render.com
├── static/
│   └── logo.png        ← Logo sekolah (taruh di sini)
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── presensi.html
    ├── jurnal.html
    ├── daftar_jurnal.html
    └── laporan.html
```

## 🔐 Akun Default
| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| Guru  | bu_sari  | guru123   |
| Guru  | pak_adi  | guru123   |
| Siswa | budi     | siswa123  |
| Siswa | ani      | siswa123  |
| Siswa | dika     | siswa123  |

## 🚀 Cara Deploy ke Render.com (GRATIS)

### 1. Push ke GitHub
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/USERNAME/selapan-pkl.git
git push -u origin main
```

### 2. Deploy di Render.com
1. Buka https://render.com → Sign Up (gratis)
2. Klik **New** → **Web Service**
3. Connect GitHub → pilih repo `selapan-pkl`
4. Render otomatis baca `render.yaml`
5. Klik **Create Web Service**
6. Tunggu ~2 menit → website live!

### 3. URL Website
Render akan memberi URL seperti:
`https://selapan-pkl.onrender.com`

## 💻 Jalankan Lokal (di VS Code)
```bash
pip install -r requirements.txt
python create_db.py
python app.py
```
Buka: http://localhost:5000

## ⚠️ Catatan Netlify
Netlify TIDAK bisa menjalankan Python/Flask.
Gunakan Render.com (gratis, mudah, mirip Netlify tapi support Python).
