# extract.py
import requests
from bs4 import BeautifulSoup
import re
import random
import time
from typing import List, Dict, Optional

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_resep_links(keyword: str, max_pages: int = 3) -> List[str]:
    """Get recipe links from Cookpad search results."""
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
            time.sleep(random.uniform(0.5, 1.2))
        except Exception as e:
            print(f"[ERROR] Failed to access {url}: {e}")
    return list(urls)

def extract_bahan(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract ingredients from recipe page."""
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

def extract_langkah(soup: BeautifulSoup) -> List[str]:
    """Extract cooking steps from recipe page."""
    steps = []
    for p in soup.select("#steps li p"):
        text = p.get_text(strip=True)
        if text:
            steps.append(text)
    return steps

def scrape_resep_detail(url: str) -> Optional[Dict]:
    """Scrape detailed recipe information from a single URL."""
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
        durasi = waktu_elem.get_text(strip=True) if waktu_elem else "Tidak diketahui"

        return {
            "judul": judul,
            "foto": foto_url,
            "penulis": penulis,
            "porsi": porsi,
            "bahan": extract_bahan(soup),
            "langkah": extract_langkah(soup),
            "durasi": durasi,
            "url": url
        }

    except Exception as e:
        print(f"[ERROR] Failed to scrape {url}: {str(e)}")
        return None