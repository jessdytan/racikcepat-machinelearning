import os
import pandas as pd
import json

def load_and_merge(clean_df: pd.DataFrame, output_path: str = "data/final/resep.json") -> None:
    """Simpan DataFrame ke file JSON tanpa escaping karakter seperti '/'."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Konversi ke Python list of dict
    data = clean_df.to_dict(orient="records")

    # Simpan menggunakan json.dump agar tidak escape /
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Data berhasil disimpan ke {output_path}")
