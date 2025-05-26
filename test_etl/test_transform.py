import unittest
import pandas as pd
from app.etl import transform

class TestTransform(unittest.TestCase):

    def setUp(self):
        self.sample_recipe = [{
            "judul": "Ayam Goreng",
            "foto": "https://img.com/foto.jpg",
            "penulis": "Budi",
            "porsi": "1 porsi",
            "durasi": "1 jam 20 menit",
            "bahan": [{"grup": "Bahan", "jumlah": "2 sdm", "bahan": "Bawangputih"}],
            "langkah": ["Goreng hingga matang"],
            "url": "https://cookpad.com/id/resep/ayam-goreng"
        }]
        self.slang = "script/slang.txt"
        self.stop_tag = "script/stopwords-tag.txt"
        self.stop_bahan = "script/stopwords-bahan.txt"
        self.root = "script/combined_root_words.txt"

    def test_transform_data_returns_dataframe(self):
        df = transform.transform_data(
            self.sample_recipe,
            slang_file=self.slang,
            stopword_file=self.stop_tag,
            stopword_bahan_file=self.stop_bahan,
            root_word_file=self.root
        )
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("tag", df.columns)

if __name__ == '__main__':
    unittest.main()
