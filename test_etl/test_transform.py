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

    def test_convert_time_to_minutes(self):
        self.assertEqual(transform.convert_time_to_minutes("1 jam 20 menit"), 80)
        self.assertEqual(transform.convert_time_to_minutes("45 menit"), 45)
        self.assertEqual(transform.convert_time_to_minutes("Tidak diketahui"), 0)

    def test_convert_serving_to_people(self):
        self.assertEqual(transform.convert_serving_to_people("2 porsi"), 2)
        self.assertEqual(transform.convert_serving_to_people("1 kg"), 8)
        self.assertEqual(transform.convert_serving_to_people("250 g"), 2)
        self.assertEqual(transform.convert_serving_to_people("unknown"), 1)

    def test_split_combined_words_found(self):
        result = transform.split_combined_words("bawangputih", {"bawang", "putih"})
        self.assertEqual(result, "bawang putih")

    def test_split_combined_words_not_found(self):
        result = transform.split_combined_words("xyzabc", {"bawang", "putih"})
        self.assertEqual(result, "xyzabc")

    def test_clean_text_replaces_slang(self):
        slang_dict = {"gpp": "tidak apa-apa"}
        result = transform.clean_text("gpp aja", slang_dict)
        self.assertIn("tidak apaapa", result)

    def test_capitalize_each_word(self):
        result = transform.capitalize_each_word("ikan dan telur serta daging")
        self.assertEqual(result, "Ikan dan Telur serta Daging")

    def test_clean_bahan_field(self):
        text = "2 sdm gula"
        slang_dict = {"sdm": "sdm"}
        stopwords = set()
        rootwords = {"sdm", "gula", "2"}
        result = transform.clean_bahan_field(
            text,
            slang_dict=slang_dict,
            stopwords=stopwords,
            rootwords=rootwords,
            capitalize_bahan=True
        )
        self.assertTrue("Gula" in result or "2" in result)

if __name__ == '__main__':
    unittest.main()