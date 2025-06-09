import os
import json
import pandas as pd
from extract import get_resep_links, scrape_resep_detail
from transform import transform_data
from load import load_and_merge
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def run_pipeline(
    keywords,
    max_pages,
    slang_file: str = None,
    stopword_file: str = None,
    stopword_bahan_file: str = None,
    root_word_file: str = None,
    output_path="data/raw/resep.csv"
):
    all_recipes = []

    print("Memulai pencarian resep...")

    for keyword in keywords:
        print(f"Mencari resep untuk: {keyword}")
        urls = get_resep_links(keyword, max_pages=max_pages)

        print(f"Ditemukan {len(urls)} link. Mengambil detail resep...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(tqdm(executor.map(scrape_resep_detail, urls), total=len(urls), desc=f"Scraping {keyword}"))

        all_recipes.extend([r for r in results if r is not None])

    if not all_recipes:
        print("Tidak ada data yang berhasil diambil.")
        return

    print("Membersihkan dan mentransformasi data...")
    df_clean = transform_data(all_recipes, slang_file=slang_file)

    print("Menyimpan data ke file CSV...")
    load_and_merge(df_clean, output_path=output_path)

    print("Pipeline selesai!")

if __name__ == "__main__":
    keywords = ["sederhana", "kos", "gampang", "cepat", "mudah", "instan", "murah","pemula"]
    slang_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'script', 'slang.txt'))
    stopword_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'script', 'stopwords-tag.txt'))
    stopword_bahan_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'script', 'stopwords-bahan.txt'))
    root_word_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'script', 'combined_root_words.txt'))
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'resep.csv'))

    run_pipeline(
        keywords=keywords,
        max_pages=1,
        slang_file=slang_file,
        stopword_file=stopword_file,
        stopword_bahan_file=stopword_bahan_file,
        root_word_file=root_word_file,
        output_path=output_path
    )
