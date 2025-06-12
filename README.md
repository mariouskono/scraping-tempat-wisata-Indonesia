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
