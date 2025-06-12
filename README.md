Berikut adalah isi `README.md` dan `requirements.txt` yang cocok untuk proyek Python Anda yang melakukan scraping tempat wisata di Indonesia menggunakan Google Maps dan Selenium:

---

### 📄 `README.md`

````markdown
# Scraper Tempat Wisata Indonesia dari Google Maps 🗺️🇮🇩

Skrip Python ini digunakan untuk mengumpulkan data tempat wisata dari Google Maps di seluruh provinsi dan kabupaten/kota di Indonesia. Data yang dikumpulkan meliputi nama tempat, kategori, rating, jumlah ulasan, koordinat, dan gambar.

## 🔧 Fitur
- Menggunakan `Selenium` untuk mengakses dan menavigasi Google Maps secara otomatis.
- Scraping seluruh provinsi dan kabupaten/kota di Indonesia.
- Otomatis mendeteksi kategori wisata berdasarkan nama tempat.
- Ekstraksi koordinat dari URL atau fallback ke geolokasi dengan `geopy`.
- Menyimpan hasil scraping ke dalam file `.csv` per provinsi dan satu file gabungan nasional.

## 🧰 Instalasi & Persiapan

### 1. Clone repositori atau salin skrip
Simpan file `scraping tempat wisata indonesia.py`.

### 2. Buat virtual environment (opsional tapi disarankan)
```bash
python -m venv env
source env/bin/activate  # Untuk Linux/Mac
env\Scripts\activate     # Untuk Windows
````

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Google Chrome

Pastikan Google Chrome terinstal di sistem Anda. Script akan otomatis mendeteksi lokasi Chrome umum.

### 5. Jalankan program

```bash
python "scraping tempat wisata indonesia.py"
```

## 📦 Output

* File CSV per provinsi: `data_wisata_Nama_Provinsi.csv`
* File gabungan: `data_wisata_indonesia.csv`

## 🛠️ Troubleshooting

* **Chrome tidak ditemukan**: Pastikan Chrome terinstal dan tersedia di path umum.
* **Timeout/No data**: Koneksi internet harus stabil, dan Google Maps terkadang memperlambat pemuatan data.

## 📋 Lisensi

Proyek ini menggunakan lisensi MIT.

````

---

### 📦 `requirements.txt`

```txt
selenium>=4.10.0
pandas>=2.0.0
geopy>=2.4.0
webdriver-manager>=4.0.0
````

---
