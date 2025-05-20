# cookpad_scraper.py
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import csv
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from difflib import SequenceMatcher

HEADERS = {"User-Agent": "Mozilla/5.0"}

KEYWORD_KATEGORI = [
    "ayam", "ikan", "telur", "tahu", "tempe", "daging", "mie", "nasi", "sapi",
    "kambing", "babi", "sambal", "kangkung", "sayur", "kuah", "pedas", "asam",
    "manis", "gurih", "kue", "sederhana", "simple", "cepat"
]

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'^\d+[.)]?\s*', '', text)
    return text.strip()

def is_similar(title1, title2, threshold=0.85):
    ratio = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
    return ratio >= threshold

def get_resep_links(keyword, max_pages=3):
    urls = set()
    for page in range(1, max_pages + 1):
        url = f"https://cookpad.com/id/cari/{keyword}?page={page}"
        try:
            res = requests.get(url, headers=HEADERS)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            links = soup.select("a[href^='/id/resep/']")
            for link in links:
                href = link.get("href")
                if href:
                    full_url = f"https://cookpad.com{href.split('?')[0]}"
                    urls.add(full_url)
            time.sleep(random.uniform(0.5, 1.2))  # faster sleep
        except Exception as e:
            print(f"[ERROR] Gagal mengakses {url}: {e}")
    return list(urls)

# def extract_bahan(soup):
#     hasil = []
#     for li in soup.select("#ingredients ol li"):
#         qty = li.find("bdi").get_text(strip=True) if li.find("bdi") else ""
#         desc = li.find("span").get_text(strip=True) if li.find("span") else ""
#         bahan = f"{qty} {desc}".strip()
#         if bahan:
#             hasil.append(bahan)
#     return hasil

def extract_langkah(soup):
    return [clean_text(p.get_text()) for p in soup.select("#steps li p") if p.get_text(strip=True)]

def extract_kategori(judul):
    judul_lc = judul.lower()
    return [kat for kat in KEYWORD_KATEGORI if kat in judul_lc]

def extract_bahan(soup):
    bahan_container = soup.select_one("div.ingredient-list ol")
    if not bahan_container:
        return []

    bahan_list = []
    current_group = "Bahan Utama"

    for li in bahan_container.select("li"):
        span = li.find("span")
        if not span:
            continue
        text = span.get_text(strip=True)

        if li.get("class") and "font-semibold" in li["class"] and not li.find("bdi").get_text(strip=True):
            current_group = text.rstrip(":")
            continue

        jumlah = li.find("bdi").get_text(strip=True) if li.find("bdi") else ""
        nama_bahan = span.get_text(strip=True)

        bahan_list.append({
            "grup": current_group,
            "jumlah": jumlah,
            "bahan": nama_bahan
        })

    return bahan_list

def scrape_resep_detail(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        judul = soup.select_one("h1")
        judul = judul.get_text(strip=True) if judul else "Judul tidak ditemukan"

        foto_url = ""
        img_tag = soup.select_one("img[alt^='Foto resep']")
        if img_tag and img_tag.get("src"):
            src = img_tag["src"]
            match = re.search(r"recipes/([a-z0-9]+)/[^/]+/([^/]+)$", src)
            if match:
                recipe_id = match.group(1)
                filename = match.group(2)
                foto_url = f"https://img-global.cpcdn.com/recipes/{recipe_id}/1280x1280sq70/{filename}"
            else:
                foto_url = src

        penulis_tag = soup.select_one("a[href*='/pengguna/'] span.font-semibold")
        penulis = penulis_tag.get_text(strip=True) if penulis_tag else "Tidak ditemukan"

        porsi_elem = soup.select_one("div[id^='serving_recipe_'] span.mise-icon-text")
        porsi = porsi_elem.get_text(strip=True) if porsi_elem else "Tidak disebutkan"

        waktu_elem = soup.select_one("div[id^='cooking_time_recipe_'] span.mise-icon-text")
        waktu_masak = waktu_elem.get_text(strip=True) if waktu_elem else "Tidak diketahui"

        return {
            "judul": judul,
            "foto": foto_url,
            "penulis": penulis,
            "porsi": porsi,
            "bahan": extract_bahan(soup),
            "langkah": extract_langkah(soup),
            # "grup": ", ".join(extract_kategori(judul)) or "lainnya",
            "waktu_masak": waktu_masak,
            "url": url
        }

    except Exception as e:
        print(f"[ERROR] Gagal scraping {url}: {str(e)}")
        return None

def scrape_keyword_antrian(keyword_list, max_pages=2):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

    # Path ke data/raw
    output_dir = os.path.join(BASE_DIR, "data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    semua_hasil = []

    for keyword in keyword_list:
        print(f"\n📌 Memproses keyword: {keyword}")
        urls = get_resep_links(keyword, max_pages=max_pages)
        print(f"🔗 Ditemukan {len(urls)} link resep.")

        hasil = []
        judul_set = []
        lock = Lock()

        def scrape_and_filter(url):
            if "https://cookpad.com/id/resep/baru" in url:
                return
            data = scrape_resep_detail(url)
            if data:
                with lock:
                    if any(is_similar(data["judul"], existing) for existing in judul_set):
                        return
                    judul_set.append(data["judul"])
                    data["kategori"] = keyword  # tambahkan kategori
                    hasil.append(data)
            time.sleep(random.uniform(1, 1.5))  # biar gak terlalu ngebut

        with ThreadPoolExecutor(max_workers=20) as executor:
            list(tqdm(executor.map(scrape_and_filter, urls), total=len(urls), desc=f"🔄 Scraping {keyword}"))

        semua_hasil.extend(hasil)  # tambahkan hasil tiap keyword ke semua_hasil

    # Simpan ke satu CSV
    output_file = os.path.join(output_dir, "resep.csv")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "judul", "foto", "penulis", "porsi",
            "bahan", "langkah", "waktu_masak", "url", "kategori"
        ])
        writer.writeheader()
        for item in semua_hasil:
            writer.writerow({
                "judul": item["judul"],
                "foto": item["foto"],
                "penulis": item["penulis"],
                "porsi": item["porsi"],
                "bahan": "\n".join([
                    f"[{b['grup']}] {b['jumlah']} {b['bahan']}" for b in item["bahan"]
                ]),
                # "bahan": "\n".join(item["bahan"]),
                "langkah": "\n".join(item["langkah"]),
                # "grup": item["grup"],
                "waktu_masak": item["waktu_masak"],
                "url": item["url"],
                "kategori": item["kategori"]
            })

    print(f"\n✅ Semua resep disimpan di: {output_file}")

if __name__ == "__main__":
    kategori_keywords = KEYWORD_KATEGORI
    scrape_keyword_antrian(kategori_keywords, max_pages=2)
