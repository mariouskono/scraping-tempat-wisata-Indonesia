# -*- coding: utf-8 -*-
import re
import csv
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# Import Nominatim from geopy.geolocators AFTER installation
from geopy import Nominatim
from webdriver_manager.chrome import ChromeDriverManager
import os
import logging
import shutil # Import shutil to check for executable

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_category(name):
    name = name.lower()
    kategori_keywords = {
        "Pantai": ["pantai", "beach", "shore", "coast"],
        "Gunung": ["gunung", "mountain", "volcano", "hill"],
        "Air Terjun": ["air terjun", "waterfall", "cascade"],
        "Danau": ["danau", "lake", "lagoon", "pond"],
        "Taman": ["taman", "park", "garden", "botanical"],
        "Museum": ["museum", "galeri", "gallery", "art space"],
        "Candi": ["candi", "temple", "pura", "pagoda"],
        "Pulau": ["pulau", "island", "archipelago"],
        "Goa": ["goa", "cave", "cavern", "grotto"],
        "Hutan": ["hutan", "forest", "rainforest", "jungle"],
        "Restoran": ["restoran", "restaurant", "cafe", "warung", "kedai", "diner"],
        "Belanja": ["mall", "shopping", "pasar", "market", "plaza"],
        "Religi": ["masjid", "mosque", "gereja", "church", "kuil", "vihara", "pura", "klenteng"],
        "Sejarah": ["benteng", "fort", "monumen", "monument", "situs", "heritage"],
        "Adventure": ["adventure", "rafting", "diving", "hiking", "trekking", "camping"]
    }
    for category, keywords in kategori_keywords.items():
        if any(keyword in name for keyword in keywords):
            return category
    return "Lainnya"

def extract_coordinates(url, title):
    patterns = [
        r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)',
        r'@(-?\d+\.\d+),(-?\d+\.\d+)',
        r'&q=(-?\d+\.\d+)%2C(-?\d+\.\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2)
    try:
        geolocator = Nominatim(user_agent="indonesia_tourism")
        location = geolocator.geocode(title)
        if location:
            return str(location.latitude), str(location.longitude)
    except Exception:
        pass
    return None, None

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # Headless baru lebih stabil
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Attempt to find the Chrome binary. Prioritize common locations.
    chrome_binary_path = shutil.which('google-chrome') or shutil.which('chromium-browser') or shutil.which('chrome')

    # Add a specific path check for google-chrome-stable if shutil.which fails
    if not chrome_binary_path:
        possible_paths = [
            "/usr/bin/google-chrome-stable",
            
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chrome",
            # Tambahkan path default Windows
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                chrome_binary_path = path
                break

    if chrome_binary_path:
        chrome_options.binary_location = chrome_binary_path
        logging.info(f"Menggunakan binary Chrome di: {chrome_binary_path}")
    else:
        logging.error("Chrome binary tidak ditemukan di path standar atau lokasi umum.")
        logging.error("Pastikan Google Chrome atau Chromium Browser terinstal dengan benar.")
        # Tampilkan instruksi ke user
        raise FileNotFoundError("Chrome binary not found. Pastikan Google Chrome sudah terinstal di Windows.")

    try:
        # ChromeDriverManager().install() will download and cache the correct chromedriver executable
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logging.error(f"Error starting Chrome: {e}")
        logging.error("Pastikan Google Chrome atau Chromium Browser terinstal dan berada di PATH sistem atau lokasi umum.")
        raise

provinsi_data = {
    "Nanggroe Aceh Darussalam": [
        "Kabupaten Simeulue", "Kabupaten Aceh Singkil", "Kabupaten Aceh Selatan",
        "Kabupaten Aceh Tenggara", "Kabupaten Aceh Timur", "Kabupaten Aceh Tengah",
        "Kabupaten Aceh Barat", "Kabupaten Aceh Besar", "Kabupaten Pidie",
        "Kabupaten Bireuen", "Kabupaten Aceh Utara", "Kabupaten Aceh Barat Daya",
        "Kabupaten Gayo Lues", "Kabupaten Aceh Tamiang", "Kabupaten Nagan Raya",
        "Kabupaten Aceh Jaya", "Kabupaten Bener Meriah", "Kabupaten Pidie Jaya",
        "Kota Banda Aceh", "Kota Sabang", "Kota Langsa", "Kota Lhokseumawe", "Kota Subulussalam"
    ],

    "Sumatera Utara": [
        "Kabupaten Nias", "Kabupaten Mandailing Natal", "Kabupaten Tapanuli Selatan",
        "Kabupaten Tapanuli Tengah", "Kabupaten Tapanuli Utara", "Kabupaten Toba Samosir",
        "Kabupaten Labuhan Batu", "Kabupaten Asahan", "Kabupaten Simalungun",
        "Kabupaten Dairi", "Kabupaten Karo", "Kabupaten Deli Serdang",
        "Kabupaten Langkat", "Kabupaten Nias Selatan", "Kabupaten Humbang Hasundutan",
        "Kabupaten Pakpak Bharat", "Kabupaten Samosir", "Kabupaten Serdang Bedagai",
        "Kabupaten Batu Bara", "Kabupaten Padang Lawas Utara", "Kabupaten Padang Lawas",
        "Kabupaten Labuhan Batu Selatan", "Kabupaten Labuhan Batu Utara", "Kabupaten Nias Utara",
        "Kabupaten Nias Barat", "Kota Sibolga", "Kota Tanjung Balai", "Kota Pematang Siantar",
        "Kota Tebing Tinggi", "Kota Medan", "Kota Binjai", "Kota Padangsidimpuan", "Kota Gunungsitoli"
    ],

    "Sumatera Selatan": [
        "Kabupaten Ogan Komering Ulu", "Kabupaten Ogan Komering Ulu Timur",
        "Kabupaten Ogan Komering Ulu Selatan", "Kabupaten Ogan Komering Ilir",
        "Kabupaten Muara Enim", "Kabupaten Lahat", "Kabupaten Musi Rawas",
        "Kabupaten Musi Banyuasin", "Kabupaten Banyuasin", "Kabupaten Empat Lawang",
        "Kabupaten Penukal Abab Lematang Ilir", "Kabupaten Musi Rawas Utara",
        "Kota Palembang", "Kota Lubuklinggau", "Kota Prabumulih", "Kota Pagar Alam"
    ],

    "Sumatera Barat": [
        "Kabupaten Kepulauan Mentawai", "Kabupaten Pesisir Selatan", "Kabupaten Solok",
        "Kabupaten Sijunjung", "Kabupaten Tanah Datar", "Kabupaten Padang Pariaman",
        "Kabupaten Agam", "Kabupaten Lima Puluh Kota", "Kabupaten Pasaman",
        "Kabupaten Solok Selatan", "Kabupaten Dharmasraya", "Kabupaten Pasaman Barat",
        "Kota Padang", "Kota Solok", "Kota Sawahlunto", "Kota Padang Panjang",
        "Kota Bukittinggi", "Kota Payakumbuh", "Kota Pariaman"
    ],

    "Bengkulu": [
        "Kabupaten Bengkulu Selatan", "Kabupaten Rejang Lebong", "Kabupaten Bengkulu Utara",
        "Kabupaten Kaur", "Kabupaten Seluma", "Kabupaten Mukomuko",
        "Kabupaten Lebong", "Kabupaten Kepahiang", "Kabupaten Bengkulu Tengah",
        "Kota Bengkulu"
    ],

    "Riau": [
        "Kabupaten Kuantan Singingi", "Kabupaten Indragiri Hulu", "Kabupaten Indragiri Hilir",
        "Kabupaten Pelalawan", "Kabupaten Siak", "Kabupaten Kampar",
        "Kabupaten Rokan Hulu", "Kabupaten Bengkalis", "Kabupaten Rokan Hilir",
        "Kabupaten Kepulauan Meranti", "Kota Pekanbaru", "Kota Dumai"
    ],

    "Kepulauan Riau": [
        "Kabupaten Karimun", "Kabupaten Bintan", "Kabupaten Natuna",
        "Kabupaten Lingga", "Kabupaten Kepulauan Anambas",
        "Kota Batam", "Kota Tanjung Pinang"
    ],

    "Jambi": [
        "Kabupaten Kerinci", "Kabupaten Merangin", "Kabupaten Sarolangun",
        "Kabupaten Batang Hari", "Kabupaten Muaro Jambi", "Kabupaten Tanjung Jabung Timur",
        "Kabupaten Tanjung Jabung Barat", "Kabupaten Tebo", "Kabupaten Bungo",
        "Kota Jambi", "Kota Sungai Penuh"
    ],

    "Lampung": [
        "Kabupaten Lampung Barat", "Kabupaten Tanggamus", "Kabupaten Lampung Selatan",
        "Kabupaten Lampung Timur", "Kabupaten Lampung Tengah", "Kabupaten Lampung Utara",
        "Kabupaten Way Kanan", "Kabupaten Tulangbawang", "Kabupaten Pesawaran",
        "Kabupaten Pringsewu", "Kabupaten Mesuji", "Kabupaten Tulang Bawang Barat",
        "Kabupaten Pesisir Barat", "Kota Bandar Lampung", "Kota Metro"
    ],

    "Bangka Belitung": [
        "Kabupaten Bangka", "Kabupaten Belitung", "Kabupaten Bangka Barat",
        "Kabupaten Bangka Tengah", "Kabupaten Bangka Selatan", "Kabupaten Belitung Timur",
        "Kota Pangkalpinang"
    ],

    "Kalimantan Barat": [
        "Kabupaten Sambas", "Kabupaten Bengkayang", "Kabupaten Landak",
        "Kabupaten Mempawah", "Kabupaten Sanggau", "Kabupaten Ketapang",
        "Kabupaten Sintang", "Kabupaten Kapuas Hulu", "Kabupaten Sekadau",
        "Kabupaten Melawi", "Kabupaten Kayong Utara", "Kabupaten Kubu Raya",
        "Kota Pontianak", "Kota Singkawang"
    ],

    "Kalimantan Timur": [
        "Kabupaten Paser", "Kabupaten Kutai Barat", "Kabupaten Kutai Kartanegara",
        "Kabupaten Kutai Timur", "Kabupaten Berau", "Kabupaten Penajam Paser Utara",
        "Kabupaten Mahakam Ulu", "Kota Balikpapan", "Kota Samarinda", "Kota Bontang"
    ],

    "Kalimantan Selatan": [
        "Kabupaten Tanah Laut", "Kabupaten Kota Baru", "Kabupaten Banjar",
        "Kabupaten Barito Kuala", "Kabupaten Tapin", "Kabupaten Hulu Sungai Selatan",
        "Kabupaten Hulu Sungai Tengah", "Kabupaten Hulu Sungai Utara", "Kabupaten Tabalong",
        "Kabupaten Tanah Bumbu", "Kabupaten Balangan", "Kota Banjarmasin", "Kota Banjar Baru"
    ],

    "Kalimantan Tengah": [
        "Kabupaten Kotawaringin Barat", "Kabupaten Kotawaringin Timur", "Kabupaten Kapuas",
        "Kabupaten Barito Selatan", "Kabupaten Barito Utara", "Kabupaten Sukamara",
        "Kabupaten Lamandau", "Kabupaten Seruyan", "Kabupaten Katingan",
        "Kabupaten Pulang Pisau", "Kabupaten Gunung Mas", "Kabupaten Barito Timur",
        "Kabupaten Murung Raya", "Kota Palangka Raya"
    ],

    "Kalimantan Utara": [
        "Kabupaten Malinau", "Kabupaten Bulungan", "Kabupaten Tana Tidung",
        "Kabupaten Nunukan", "Kota Tarakan"
    ],

    "Banten": [
        "Kabupaten Pandeglang", "Kabupaten Lebak", "Kabupaten Tangerang",
        "Kabupaten Serang", "Kota Tangerang", "Kota Cilegon",
        "Kota Serang", "Kota Tangerang Selatan"
    ],

    "DKI Jakarta": [
        "Kabupaten Kepulauan Seribu", "Jakarta Selatan", "Jakarta Timur",
        "Jakarta Pusat", "Jakarta Barat", "Jakarta Utara"
    ],

    "Jawa Barat": [
        "Kabupaten Bogor", "Kabupaten Sukabumi", "Kabupaten Cianjur",
        "Kabupaten Bandung", "Kabupaten Garut", "Kabupaten Tasikmalaya",
        "Kabupaten Ciamis", "Kabupaten Kuningan", "Kabupaten Cirebon",
        "Kabupaten Majalengka", "Kabupaten Sumedang", "Kabupaten Indramayu",
        "Kabupaten Subang", "Kabupaten Purwakarta", "Kabupaten Karawang",
        "Kabupaten Bekasi", "Kabupaten Bandung Barat", "Kabupaten Pangandaran",
        "Kota Bogor", "Kota Sukabumi", "Kota Bandung", "Kota Cirebon",
        "Kota Bekasi", "Kota Depok", "Kota Cimahi", "Kota Tasikmalaya", "Kota Banjar"
    ],

    "Jawa Tengah": [
        "Kabupaten Cilacap", "Kabupaten Banyumas", "Kabupaten Purbalingga",
        "Kabupaten Banjarnegara", "Kabupaten Kebumen", "Kabupaten Purworejo",
        "Kabupaten Wonosobo", "Kabupaten Magelang", "Kabupaten Boyolali",
        "Kabupaten Klaten", "Kabupaten Sukoharjo", "Kabupaten Wonogiri",
        "Kabupaten Karanganyar", "Kabupaten Sragen", "Kabupaten Grobogan",
        "Kabupaten Blora", "Kabupaten Rembang", "Kabupaten Pati",
        "Kabupaten Kudus", "Kabupaten Jepara", "Kabupaten Demak",
        "Kabupaten Semarang", "Kabupaten Temanggung", "Kabupaten Kendal",
        "Kabupaten Batang", "Kabupaten Pekalongan", "Kabupaten Pemalang",
        "Kabupaten Tegal", "Kabupaten Brebes", "Kota Magelang",
        "Kota Surakarta", "Kota Salatiga", "Kota Semarang", "Kota Pekalongan", "Kota Tegal"
    ],

    "Daerah Istimewa Yogyakarta": [
        "Kabupaten Kulonprogo", "Kabupaten Bantul", "Kabupaten Gunungkidul",
        "Kabupaten Sleman", "Kota Yogyakarta"
    ],

    "Jawa Timur": [
        "Kabupaten Pacitan", "Kabupaten Ponorogo", "Kabupaten Trenggalek",
        "Kabupaten Tulungagung", "Kabupaten Blitar", "Kabupaten Kediri",
        "Kabupaten Malang", "Kabupaten Lumajang", "Kabupaten Jember",
        "Kabupaten Banyuwangi", "Kabupaten Bondowoso", "Kabupaten Situbondo",
        "Kabupaten Probolinggo", "Kabupaten Pasuruan", "Kabupaten Sidoarjo",
        "Kabupaten Mojokerto", "Kabupaten Jombang", "Kabupaten Nganjuk",
        "Kabupaten Madiun", "Kabupaten Magetan", "Kabupaten Ngawi",
        "Kabupaten Bojonegoro", "Kabupaten Tuban", "Kabupaten Lamongan",
        "Kabupaten Gresik", "Kabupaten Bangkalan", "Kabupaten Sampang",
        "Kabupaten Pamekasan", "Kabupaten Sumenep", "Kota Kediri",
        "Kota Blitar", "Kota Malang", "Kota Probolinggo", "Kota Pasuruan",
        "Kota Mojokerto", "Kota Madiun", "Kota Surabaya", "Kota Batu"
    ],

    "Bali": [
        "Kabupaten Jembrana", "Kabupaten Tabanan", "Kabupaten Badung",
        "Kabupaten Gianyar", "Kabupaten Klungkung", "Kabupaten Bangli",
        "Kabupaten Karangasem", "Kabupaten Buleleng", "Kota Denpasar"
    ],

    "Nusa Tenggara Barat": [
        "Kabupaten Lombok Barat", "Kabupaten Lombok Tengah", "Kabupaten Lombok Timur",
        "Kabupaten Sumbawa", "Kabupaten Dompu", "Kabupaten Bima",
        "Kabupaten Sumbawa Barat", "Kabupaten Lombok Utara",
        "Kota Mataram", "Kota Bima"
    ],

    "Nusa Tenggara Timur": [
        "Kabupaten Sumba Barat", "Kabupaten Sumba Timur", "Kabupaten Kupang",
        "Kabupaten Timor Tengah Selatan", "Kabupaten Timor Tengah Utara", "Kabupaten Belu",
        "Kabupaten Alor", "Kabupaten Lembata", "Kabupaten Flores Timur",
        "Kabupaten Sikka", "Kabupaten Ende", "Kabupaten Ngada",
        "Kabupaten Manggarai", "Kabupaten Rote Ndao", "Kabupaten Manggarai Barat", # Corrected Rata to Ndao
        "Kabupaten Sumba Tengah", "Kabupaten Sumba Barat Daya", "Kabupaten Nagekeo",
        "Kabupaten Manggarai Timur", "Kabupaten Sabu Raijua", "Kabupaten Malaka",
        "Kota Kupang"
    ],

    "Gorontalo": [
        "Kabupaten Boalemo", "Kabupaten Gorontalo", "Kabupaten Pohuwato",
        "Kabupaten Bone Bolango", "Kabupaten Gorontalo Utara", "Kota Gorontalo"
    ],

    "Sulawesi Barat": [
        "Kabupaten Majene", "Kabupaten Polewali Mandar", "Kabupaten Mamasa",
        "Kabupaten Mamuju", "Kabupaten Pasangkayu", "Kabupaten Mamuju Tengah"
    ],

    "Sulawesi Tengah": [
        "Kabupaten Banggai Kepulauan", "Kabupaten Banggai", "Kabupaten Morowali",
        "Kabupaten Poso", "Kabupaten Donggala", "Kabupaten Tolitoli",
        "Kabupaten Buol", "Kabupaten Parigi Moutong", "Kabupaten Tojo Una-una",
        "Kabupaten Sigi", "Kabupaten Banggai Laut", "Kabupaten Morowali Utara",
        "Kota Palu"
    ],

    "Sulawesi Utara": [
        "Kabupaten Bolaang Mongondow", "Kabupaten Minahasa", "Kabupaten Kepulauan Sangihe",
        "Kabupaten Kepulauan Talaud", "Kabupaten Minahasa Selatan", "Kabupaten Minahasa Utara",
        "Kabupaten Bolaang Mongondow Utara", "Kabupaten Kepulauan Sitaro", "Kabupaten Minahasa Tenggara",
        "Kabupaten Bolaang Mongondow Selatan", "Kabupaten Bolaang Mongondow Timur",
        "Kota Manado", "Kota Bitung", "Kota Tomohon", "Kota Kotamobagu"
    ],

    "Sulawesi Tenggara": [
        "Kabupaten Buton", "Kabupaten Muna", "Kabupaten Konawe",
        "Kabupaten Kolaka", "Kabupaten Konawe Selatan", "Kabupaten Bombana",
        "Kabupaten Wakatobi", "Kabupaten Kolaka Utara", "Kabupaten Buton Utara",
        "Kabupaten Konawe Utara", "Kabupaten Kolaka Timur", "Kabupaten Konawe Kepulauan",
        "Kabupaten Muna Barat", "Kabupaten Buton Tengah", "Kabupaten Buton Selatan",
        "Kota Kendari", "Kota Baubau"
    ],

    "Sulawesi Selatan": [
        "Kabupaten Kepulauan Selayar", "Kabupaten Bulukumba", "Kabupaten Bantaeng",
        "Kabupaten Jeneponto", "Kabupaten Takalar", "Kabupaten Gowa",
        "Kabupaten Sinjai", "Kabupaten Maros", "Kabupaten Pangkajene dan Kepulauan",
        "Kabupaten Barru", "Kabupaten Bone", "Kabupaten Soppeng",
        "Kabupaten Wajo", "Kabupaten Sindereng Rappang", "Kabupaten Pinrang",
        "Kabupaten Enrekang", "Kabupaten Luwu", "Kabupaten Tana Toraja",
        "Kabupaten Luwu Utara", "Kabupaten Luwu Timur", "Kabupaten Toraja Utara",
        "Kota Makassar", "Kota Parepare", "Kota Palopo"
    ],

    "Maluku Utara": [
        "Kabupaten Halmahera Barat", "Kabupaten Halmahera Tengah", "Kabupaten Kepulauan Sula",
        "Kabupaten Halmahera Selatan", "Kabupaten Halmahera Utara", "Kabupaten Halmahera Timur",
        "Kabupaten Pulau Morotai", "Kabupaten Pulau Taliabu",
        "Kota Ternate", "Kota Tidore Kepulauan"
    ],

    "Maluku": [
        "Kabupaten Kepulauan Tanimbar", "Kabupaten Maluku Tenggara", "Kabupaten Maluku Tengah",
        "Kabupaten Buru", "Kabupaten Kepulauan Aru", "Kabupaten Seram Bagian Barat",
        "Kabupaten Seram Bagian Timur", "Kabupaten Maluku Barat Daya", "Kabupaten Buru Selatan",
        "Kota Ambon", "Kota Tual"
    ],

    "Papua Barat": [
        "Kabupaten Fakfak", "Kabupaten Kaimana", "Kabupaten Teluk Wondama",
        "Kabupaten Teluk Bintuni", "Kabupaten Manokwari", "Kabupaten Manokwari Selatan",
        "Kabupaten Pegunungan Arfak"
    ],

    "Papua": [
        "Kabupaten Biak Numfor", "Kabupaten Jayapura", "Kabupaten Keerom",
        "Kabupaten Kepulauan Yapen", "Kabupaten Mamberamo Raya", "Kabupaten Sarmi",
        "Kabupaten Supiori", "Kabupaten Waropen", "Kota Jayapura"
    ],

    "Papua Tengah": [
        "Kabupaten Deiyai", "Kabupaten Dogiyai", "Kabupaten Intan Jaya",
        "Kabupaten Mimika", "Kabupaten Nabire", "Kabupaten Paniai",
        "Kabupaten Puncak", "Kabupaten Puncak Jaya"
    ],

    "Papua Pegunungan": [
        "Kabupaten Jayawijaya", "Kabupaten Lanny Jaya", "Kabupaten Mamberamo Tengah",
        "Kabupaten Nduga", "Kabupaten Pegunungan Bintang", "Kabupaten Tolikara",
        "Kabupaten Yalimo", "Kabupaten Yahukimo"
    ],

    "Papua Selatan": [
        "Kabupaten Asmat", "Kabupaten Boven Digoel", "Kabupaten Mappi", "Kabupaten Merauke"
    ],

    "Papua Barat Daya": [
        "Kabupaten Maybrat", "Kabupaten Raja Ampat", "Kabupaten Sorong",
        "Kabupaten Sorong Selatan", "Kabupaten Tambrauw", "Kota Sorong"
    ]
}

if __name__ == "__main__":
    print(f"Total provinsi: {len(provinsi_data)}")
    print(f"\nContoh akses data:")
    print(f"Kabupaten/Kota di DKI Jakarta: {provinsi_data['DKI Jakarta']}")
    print(f"Jumlah Kabupaten/Kota di Jawa Barat: {len(provinsi_data['Jawa Barat'])}")
    print(f"\nDaftar semua provinsi:")
    for i, provinsi in enumerate(provinsi_data.keys(), 1):
        print(f"{i}. {provinsi} ({len(provinsi_data[provinsi])} Kabupaten/Kota)")

    driver = None # Initialize driver to None
    try:
        driver = setup_driver()
        for provinsi, kabupaten_list in provinsi_data.items():
            all_items = []
            logging.info(f"Memulai scraping untuk provinsi {provinsi}")
            for kabupaten in kabupaten_list:
                logging.info(f"Mencari tempat wisata di {kabupaten}, {provinsi}...")
                try:
                    driver.get("https://www.google.com/maps")
                    time.sleep(2)
                    # Terima cookies jika muncul
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Accept all']"))
                        ).click()
                    except Exception:
                        pass
                    # Lakukan pencarian
                    search_box = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#searchboxinput"))
                    )
                    search_box.clear()
                    search_box.send_keys(f"Tempat wisata di {kabupaten}, {provinsi}", Keys.RETURN)
                    time.sleep(3)
                    # Tunggu hasil muncul
                    try:
                        scrollable_div = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
                        )
                    except TimeoutException:
                        logging.warning(f"Tidak ditemukan hasil untuk {kabupaten}, {provinsi}")
                        continue
                    # Scroll sampai bawah
                    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                    scroll_attempts = 0
                    max_scroll_attempts = 15
                    while scroll_attempts < max_scroll_attempts:
                        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scrollable_div)
                        time.sleep(2)
                        try:
                            more_button = driver.find_element(By.CSS_SELECTOR, 'button[jsaction="pane.paginationSection.nextPage"]')
                            if more_button.is_displayed() and more_button.is_enabled():
                                more_button.click()
                                time.sleep(1.5)
                        except NoSuchElementException:
                            pass
                        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                        if new_height == last_height:
                            scroll_attempts += 1
                        else:
                            scroll_attempts = 0
                            last_height = new_height
                    # Ekstrak item
                    items = driver.find_elements(By.XPATH, '//div[@role="feed"]//div[contains(@class, "THOPZb")]')
                    logging.info(f"Ditemukan {len(items)} tempat wisata di {kabupaten}, {provinsi}")
                    for item in items:
                        try:
                            title = item.find_element(By.CSS_SELECTOR, 'div.qBF1Pd').text
                            link = item.find_element(By.CSS_SELECTOR, 'a.hfpxzc').get_attribute('href')
                            # Ambil rating
                            try:
                                rating_element = item.find_element(By.CSS_SELECTOR, 'span[aria-label*="bintang"]')
                                rating_text = rating_element.get_attribute('aria-label')
                                rating = float(rating_text.split()[0].replace(',', '.')) if rating_text else None
                            except Exception:
                                try:
                                    rating_element = item.find_element(By.CSS_SELECTOR, 'span.MW4etd')
                                    rating = float(rating_element.text.replace(',', '.')) if rating_element.text else None
                                except Exception:
                                    rating = None
                            # Ambil jumlah rating
                            try:
                                rating_count_element = item.find_element(By.CSS_SELECTOR, 'span[aria-label*="ulasan"]')
                                rating_count_text = rating_count_element.get_attribute('aria-label')
                                rating_count = ''.join(filter(str.isdigit, rating_count_text)) if rating_count_text else None
                            except Exception:
                                try:
                                    rating_count_element = item.find_element(By.CSS_SELECTOR, 'span[aria-label*="review"]')
                                    rating_count_text = rating_count_element.get_attribute('aria-label')
                                    rating_count = ''.join(filter(str.isdigit, rating_count_text)) if rating_count_text else None
                                except Exception:
                                    rating_count = None
                            # Ambil link gambar (satu gambar saja)
                            try:
                                img_elem = item.find_element(By.CSS_SELECTOR, 'img')
                                link_gambar = img_elem.get_attribute('src')
                            except Exception:
                                link_gambar = None
                            latitude, longitude = extract_coordinates(link, title)
                            category = get_category(title)
                            all_items.append({
                                "nama": title,
                                "kategori": category,
                                "provinsi": provinsi,
                                "kabupaten": kabupaten,
                                "rating": rating,
                                "jumlah_rating": rating_count,
                                "link": link,
                                "link_gambar": link_gambar,
                                "latitude": latitude,
                                "longitude": longitude
                            })
                        except Exception as e:
                            logging.warning(f"Error memproses item: {str(e)}")
                except Exception as e:
                    logging.error(f"Error saat scraping {kabupaten}, {provinsi}: {str(e)}")
                time.sleep(5)  # Tambahkan delay antar kabupaten
            # Simpan ke CSV per provinsi
            if all_items:
                filename = f"data_wisata_{provinsi.replace(' ', '_')}.csv"
                df = pd.DataFrame(all_items)
                df.to_csv(filename, index=False)
                logging.info(f"Data untuk {provinsi} berhasil disimpan dalam {filename}")
    finally:
        # Ensure driver is quit only if it was successfully initialized
        if driver:
            driver.quit()

    # Gabungkan semua file CSV yang sudah dihasilkan
    csv_files = [f"data_wisata_{provinsi.replace(' ', '_')}.csv" for provinsi in provinsi_data.keys()]
    existing_csv_files = [f for f in csv_files if os.path.exists(f)]
    if existing_csv_files:
        all_data = pd.concat([pd.read_csv(file) for file in existing_csv_files], ignore_index=True)
        all_data.to_csv("data_wisata_indonesia.csv", index=False)
        print("✅ Data lengkap untuk seluruh Indonesia telah disimpan dalam data_wisata_indonesia.csv")
    else:
        print("❌ Tidak ada file CSV yang dihasilkan untuk digabungkan.")