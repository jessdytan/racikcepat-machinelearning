# %%
import json
import pandas as pd
import re
import nltk
import os
from scipy.sparse import save_npz
import numpy as np
from tqdm import tqdm
import pickle
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
nltk.download('punkt', download_dir=nltk_data_dir)
nltk.data.path.append(nltk_data_dir)

with open('../data/resep.json', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df.head()

df = df[df['bahan'].apply(lambda x: isinstance(x, list) and len(x) > 0)]
df = df[df['judul'].notnull() & df['judul'].apply(lambda x: x.strip().lower() != 'judul tidak ditemukan')]

def extract_ingredients(bahan_list):
    return ' '.join(item['bahan'] for item in bahan_list if 'bahan' in item)

df['bahan_text'] = df['bahan'].apply(extract_ingredients)

df['bahan_text']

stemmer = StemmerFactory().create_stemmer()

slang_path = '../script/slang.txt'
slang_dict = {}
with open(slang_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or ' : ' not in line:
            continue
        slang, formal = line.split(' : ', 1)
        slang_dict[slang.strip()] = formal.strip()

stopword_path = '../script/stopwords-tag.txt'
with open(stopword_path, 'r', encoding='utf-8') as f:
    bahan_stopwords = set(line.strip().lower() for line in f if line.strip())

def preprocess_bahan(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = word_tokenize(text, preserve_line=True)
    tokens = [slang_dict.get(word, word) for word in tokens]
    tokens = [word for word in tokens if word not in bahan_stopwords]
    tokens = [stemmer.stem(word) for word in tokens]
    return ' '.join(tokens)

tqdm.pandas(desc="Preprocessing bahan")
df['clean_bahan'] = df['bahan_text'].progress_apply(preprocess_bahan)

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['clean_bahan'])

with open('../data/tfidf_data.pkl', 'wb') as f:
    pickle.dump({
        'matrix': tfidf_matrix,
        'features': vectorizer.get_feature_names_out(),
        'index': df.index 
    }, f)

save_npz('../data/full_tfidf_matrix.npz', tfidf_matrix)

np.save('../data/tfidf_feature_names.npy', vectorizer.get_feature_names_out())
