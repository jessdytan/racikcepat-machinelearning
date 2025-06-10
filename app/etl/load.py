import os
import pandas as pd
import json

def load_and_merge(clean_df: pd.DataFrame, output_path: str = "data/final/resep.csv") -> None:
    """Simpan DataFrame ke file CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Simpan ke file CSV
    clean_df.to_csv(output_path, index=False, encoding='utf-8')

    print(f"Data berhasil disimpan ke {output_path}")
