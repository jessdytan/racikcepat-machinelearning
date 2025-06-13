import os
import unittest
import numpy as np
import cv2
from app.ocr.processor import ReceiptOCR

class TestReceiptOCR(unittest.TestCase):
    def setUp(self):
        # Buat gambar dummy berisi teks agar bisa dibaca OCR
        dummy_image = np.ones((400, 1000, 3), dtype=np.uint8) * 255

        cv2.putText(
            dummy_image,
            "Indomie Goreng 1 2500 2500",
            (50, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            3,              # ukuran font diperbesar
            (0, 0, 0),
            6               # ketebalan huruf
        )

        # Simpan (opsional untuk debug manual)
        cv2.imwrite("debug_dummy_image.jpg", dummy_image)

        self.dummy_image = dummy_image

        # Buat file produk sementara
        self.temp_product_file = "test_ocr/temp_product.txt"
        os.makedirs(os.path.dirname(self.temp_product_file), exist_ok=True)
        with open(self.temp_product_file, "w", encoding="utf-8") as f:
            f.write("Indomie Goreng|Makanan\n")
            f.write("Minyak Goreng|Minyak Goreng\n")
            f.write("Sabun Mandi|Kebutuhan Rumah Tangga\n")

        # Inisialisasi OCR
        self.ocr = ReceiptOCR(
            image_array=self.dummy_image,
            products_file=self.temp_product_file
        )

    def tearDown(self):
        if os.path.exists(self.temp_product_file):
            os.remove(self.temp_product_file)
        if os.path.exists("debug_dummy_image.jpg"):
            os.remove("debug_dummy_image.jpg")

    def test_find_closest_product_exact(self):
        result = self.ocr.find_closest_product("Indomie Goreng")
        self.assertEqual(result['kategori'], "Makanan")

    def test_find_closest_product_typo(self):
        result = self.ocr.find_closest_product("Indome Goreng")
        self.assertIn(result['kategori'], ["Makanan", "Tidak Diketahui"])

    def test_find_closest_product_unknown(self):
        result = self.ocr.find_closest_product("Barang Ga Ada")
        self.assertEqual(result['kategori'], "Tidak Diketahui")

    def test_process_image_returns_list(self):
        parsed = self.ocr.parse_receipt()

        self.assertIsInstance(parsed, dict)
        self.assertIn('items', parsed)
        self.assertIsInstance(parsed['items'], list)

        # Karena hasil OCR bisa fluktuatif, kita longgar dalam validasi
        item_nama_list = [item['nama'].lower() for item in parsed['items']]
        ada_indomie = any("indomie" in nama for nama in item_nama_list)
        self.assertTrue(ada_indomie, f"Hasil OCR tidak mendeteksi 'Indomie': {item_nama_list}")

    def test_empty_product_file(self):
        empty_file = "test_ocr/empty_product.txt"
        with open(empty_file, "w", encoding="utf-8"):
            pass
        ocr_empty = ReceiptOCR(image_array=self.dummy_image, products_file=empty_file)
        result = ocr_empty.find_closest_product("Indomie Goreng")
        self.assertEqual(result['kategori'], "Tidak Diketahui")
        os.remove(empty_file)

if __name__ == '__main__':
    unittest.main()