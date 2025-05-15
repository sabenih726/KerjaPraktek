# Sistem Manajemen Tiket GA (General Affairs)

Aplikasi berbasis Streamlit untuk divisi General Affairs untuk menangani, melacak, dan mengelola permintaan layanan.

## Fitur

- Formulir pelaporan tiket untuk publik tanpa perlu login
- Pencarian status tiket menggunakan ID tiket
- Dashboard admin untuk manajemen tiket
- Sistem penugasan tiket
- Laporan dan analitik tiket
- Manajemen pengguna untuk administrator

## Teknologi

- Python
- Streamlit
- Pandas
- Plotly (untuk visualisasi)

## Cara Instalasi

1. Clone repository ini:
```bash
git clone https://github.com/username/ga-ticket-system.git
cd ga-ticket-system
```

2. Install dependensi:
```bash
pip install streamlit pandas plotly
```

3. Jalankan aplikasi:
```bash
streamlit run app.py
```

## Akses Admin

Kredensial default untuk akses admin:
- Username: admin
- Password: admin123

## Struktur Aplikasi

- **app.py**: Halaman utama dengan form pelaporan tiket dan login admin
- **utils.py**: Fungsi utilitas untuk manajemen data
- **pages/**: Halaman tambahan aplikasi
  - **admin_dashboard.py**: Dashboard admin
  - **user_management.py**: Manajemen pengguna (hanya admin)
  - **reports.py**: Laporan dan analitik (hanya admin)
  - **ticket_details.py**: Detail tiket

## Data

Aplikasi menyimpan data di folder `data/`:
- **tickets.csv**: Database tiket
- **users.csv**: Database pengguna

## Penggunaan

### Pelapor
1. Buka halaman utama aplikasi
2. Isi formulir pelaporan tiket
3. Simpan ID tiket yang diberikan
4. Gunakan ID tiket untuk melacak status permintaan

### Admin
1. Klik tab "Admin Login" 
2. Login dengan kredensial admin
3. Akses dashboard admin untuk mengelola tiket
4. Update status dan menugaskan tiket
5. Lihat laporan dan analitik