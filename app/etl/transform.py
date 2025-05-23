import os
import re
from typing import Dict, List
import pandas as pd
from collections import Counter

# Load slang dictionary
def load_slang_dict(slang_file: str = None) -> Dict[str, str]:
    if slang_file is None:
        slang_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'script', 'slang.txt'))

    if not os.path.exists(slang_file):
        raise FileNotFoundError(f"Slang file not found at: {slang_file}")

    slang_dict = {}
    with open(slang_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ' : ' not in line:
                continue
            slang, formal = line.split(' : ', 1)
            slang_dict[slang.strip()] = formal.strip()
    return slang_dict

# Protect and restore parentheses
def protect_parentheses_content(text):
    matches = re.findall(r'\([^)]*\)', text)
    for i, match in enumerate(matches):
        text = text.replace(match, f"__p{i}__")
    return text, matches

def restore_parentheses_content(text, matches):
    for i, match in enumerate(matches):
        text = text.replace(f"__p{i}__", match)
    return text

# Clean and normalize text
def clean_text(text: str, slang_dict: Dict[str, str]) -> str:
    if not isinstance(text, str):
        return ""

    text = text.replace("²", "")
    words = text.split()
    cleaned_words = [slang_dict.get(word.lower(), word) for word in words]
    text = ' '.join(cleaned_words)

    text = re.sub(r'[^\w\s(),]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s+,', ',', text)
    return text

# Capitalization
def capitalize_each_word(text: str) -> str:
    konjungsi = {"dan", "atau", "serta"}
    words = text.lower().split()
    return ' '.join(
        word if word in konjungsi else word.capitalize()
        for word in words
    )

def capitalize_jumlah_preserving_units(text: str) -> str:
    units = {
        "ml": "mL", "l": "L", "kg": "kg", "g": "gr", "gram": "gr", "kilogram": "kg",
        "liter": "L", "sdt": "sdt", "sdk": "sdk", "sdm": "sdm"
    }
    words = text.split()
    result = []
    for word in words:
        low = word.lower()
        if low in units:
            result.append(units[low])
        else:
            result.append(word.capitalize())
    return ' '.join(result)

# Time & Serving Conversion
def convert_time_to_minutes(time_str: str) -> int:
    if not isinstance(time_str, str):
        return 0
    time_str = time_str.lower()
    minutes = 0
    hour_match = re.search(r'(\d+)\s*jam', time_str)
    if hour_match:
        minutes += int(hour_match.group(1)) * 60
    minute_match = re.search(r'(\d+)\s*menit', time_str)
    if minute_match:
        minutes += int(minute_match.group(1))
    return minutes

def format_time(durasi):
    if isinstance(durasi, int) and durasi > 0:
        return f"{durasi} Menit"
    return "Tidak ada"

def format_serving(porsi):
    if isinstance(porsi, int) and porsi > 0:
        return f"{porsi} Orang"
    return "Tidak ada"

def convert_serving_to_people(serving_str: str) -> int:
    if not isinstance(serving_str, str):
        return 1
    serving_str = serving_str.lower()
    num_match = re.search(r'(\d+)', serving_str)
    if num_match:
        return int(num_match.group(1))
    kg_match = re.search(r'(\d+\.?\d*)\s*kg', serving_str)
    if kg_match:
        kg = float(kg_match.group(1))
        return int(kg * 8)
    gram_match = re.search(r'(\d+)\s*g', serving_str)
    if gram_match:
        grams = int(gram_match.group(1))
        return max(1, grams // 125)
    return 1

def load_stopwords_tag(filepath: str = None) -> set:
    if filepath is None:
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'script', 'stopwords-tag.txt'))

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Stopwords-tag file not found at: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())

def load_stopwords_bahan(filepath: str = None) -> set:
    if filepath is None:
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'script', 'stopwords-bahan.txt'))

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Stopwords-bahan file not found at: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())

def load_root_words(filepath: str = None) -> set:
    if filepath is None:
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'script', 'combined_root_words.txt'))

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Root word file not found at: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())

def split_combined_words(text: str, word_set: set) -> str:
    original = text.lower()
    i = 0
    result = []
    matched = False
    while i < len(original):
        for j in range(len(original), i, -1):
            candidate = original[i:j]
            if candidate in word_set:
                result.append(candidate)
                i = j
                matched = True
                break
        else:
            result.append(original[i:])
            break
    return ' '.join(result) if matched else text

def clean_bahan_field(text: str, slang_dict: Dict[str, str], stopwords: set, rootwords: set, capitalize_bahan=False, capitalize_jumlah=False) -> str:
    text_protected, parentheses = protect_parentheses_content(text)
    cleaned = clean_text(text_protected, slang_dict)

    # Cek jika semua kata sudah ada di rootwords, baru split
    all_words = re.findall(r'\w+', cleaned.lower())
    should_split = all(word in rootwords for word in all_words)
    splitted = split_combined_words(cleaned, rootwords) if should_split else cleaned

    filtered = ' '.join([
        w for w in splitted.split()
        if w.lower().strip("(),") not in stopwords
    ])
    restored = restore_parentheses_content(filtered, parentheses)
    restored = re.sub(r'\s+,', ',', restored)

    if capitalize_bahan:
        return capitalize_each_word(restored)
    else:
        return capitalize_jumlah_preserving_units(restored)

def extract_tags(texts: List[str], stopwords: set, max_tags: int = 3) -> List[str]:
    all_words = []
    for text in texts:
        words = re.findall(r'\b\w+\b', text.lower())
        all_words.extend(word for word in words if word not in stopwords)
    counter = Counter(all_words)
    most_common = [word for word, _ in counter.most_common(max_tags)]
    return most_common

def unescape_url(text: str) -> str:
    return text.replace('\\/', '/')

def transform_data(recipes: List[Dict], slang_file: str = None, stopword_file: str = None, stopword_bahan_file: str = None, root_word_file: str = None) -> pd.DataFrame:
    stopwords = load_stopwords_tag(stopword_file)
    slang_dict = load_slang_dict(slang_file)
    bahan_stopwords = load_stopwords_bahan(stopword_bahan_file)
    root_words = load_root_words(root_word_file)

    df = pd.DataFrame(recipes)
    df = df[df['judul'].apply(lambda x: isinstance(x, str) and x.strip() != '')].copy()
    df = df[df['judul'].apply(lambda x: x.lower() != 'judul tidak ditemukan')]

    df['durasi'] = df['durasi'].apply(convert_time_to_minutes).apply(format_time)
    df['porsi'] = df['porsi'].apply(convert_serving_to_people).apply(format_serving)
    df['url'] = df['url'].apply(unescape_url)
    df['foto'] = df['foto'].apply(unescape_url)

    df['bahan'] = df['bahan'].apply(lambda bahan_list: [
        {
            'grup': clean_bahan_field(item['grup'], slang_dict, bahan_stopwords, root_words),
            'jumlah': clean_bahan_field(item['jumlah'], slang_dict, bahan_stopwords, root_words, capitalize_jumlah=True),
            'bahan': clean_bahan_field(item['bahan'], slang_dict, bahan_stopwords, root_words, capitalize_bahan=True)
        } for item in bahan_list
    ])

    df['langkah'] = df['langkah'].apply(lambda steps: [
        clean_text(step, slang_dict).capitalize() for step in steps
    ])

    df['tag'] = df.apply(lambda row: extract_tags(
        [row['judul']] + row['langkah'], stopwords=stopwords), axis=1)

    df = df.drop_duplicates(subset=['judul', 'penulis'])

    return df
