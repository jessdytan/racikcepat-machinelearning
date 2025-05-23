import unittest
import os
import json
import pandas as pd
from app.etl import load

class TestLoad(unittest.TestCase):

    def test_load_and_merge_creates_file(self):
        df = pd.DataFrame([{
            "judul": "Test",
            "foto": "https://img.com",
            "penulis": "tester",
            "porsi": "1 Orang",
            "durasi": "20 Menit",
            "bahan": [],
            "langkah": [],
            "url": "https://cookpad.com/test",
            "tag": ["test"]
        }])
        output_path = "test_etl/test_output.json"
        load.load_and_merge(df, output_path)

        self.assertTrue(os.path.exists(output_path))

        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data[0]["judul"], "Test")

        os.remove(output_path)

if __name__ == '__main__':
    unittest.main()
