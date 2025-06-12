import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
from fuzzywuzzy import fuzz

pytesseract.pytesseract.tesseract_cmd = 'tesseract'

class ReceiptOCR:
    def __init__(self, image_array, products_file='./data/product.txt'):
        self.original = image_array
        if self.original is None:
            raise ValueError("Gambar tidak valid.")

        # Storage untuk hasil preprocessing
        self.gray = None
        self.denoised = None
        self.thresholded = None
        self.deskewed = None

        self.known_products = self._load_products_from_file(products_file)

    def _normalize_text(self, text):
        """
        Menghapus semua karakter non-alfanumerik dan ubah ke huruf kecil
        untuk meningkatkan pencocokan fuzzy.
        """
        return re.sub(r'[^a-z0-9]', '', text.lower())

    def preprocess(self):
        self.gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        self.gray = cv2.resize(self.gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Tingkatkan kontras
        self.gray = cv2.convertScaleAbs(self.gray, alpha=1.8, beta=20)

        # CLAHE untuk perbaikan lokal
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        self.enhanced = clahe.apply(self.gray)

        # Thresholding adaptif
        self.thresholded = cv2.adaptiveThreshold(
            self.enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Morph ops untuk membersihkan noise tanpa kehilangan teks
        kernel = np.ones((2, 2), np.uint8)
        self.final = cv2.morphologyEx(self.thresholded, cv2.MORPH_OPEN, kernel)

        return self.final

    def extract_text(self):
        """Text extraction with optimized settings for receipts"""
        if not hasattr(self, 'final'):
            self.preprocess()
        
        # Konfigurasi Tesseract untuk OCR
        # Menggunakan mode OEM 3 (LSTM) dan PSM 6 (Assume a single uniform block of text)
        config = r'--oem 3 --psm 6 -l ind+eng'
        
        text = pytesseract.image_to_string(
            Image.fromarray(self.final),
            config=config
        )
        
        return text

    def parse_receipt(self):
        text = self.extract_text()

        if not text:
            raise ValueError("Tidak ada teks yang terdeteksi pada gambar")
        
        # Items pattern - lebih fleksibel untuk format yang bervariasi
        items = []
        item_pattern = re.compile(r'^(.+?)\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)$')
        alt_pattern = re.compile(r'^(.+?)\s+([\d.,]+)\s+(\d+)\s+([\d.,]+)$')
        simple_pattern = re.compile(r'^(.+?)\s+([\d.,]+)\s+([\d.,]+)$')

        for line in text.splitlines():
            line = line.strip()
            # Bersihkan karakter khusus dan normalisasi
            line = re.sub(r'[—|"~]', '', line)  # Hapus karakter khusus
            line = re.sub(r'\s+', ' ', line)   # Normalisasi spasi
            
            # Skip line kosong atau header/total
            if (not line or 
                line.startswith(('Daftar', 'Qty', '----', 'HARGA', 'TOTAL', 'TUNAI', 'KEMBALI', 'PPN', 'LAYANAN'))):
                continue
                
            match = item_pattern.match(line) or alt_pattern.match(line) or simple_pattern.match(line)
            if match:
                try:
                    groups = match.groups()
                    nama = groups[0].strip()
                    
                    items.append({
                        'nama': nama,
                    })
                except (ValueError, IndexError) as e:
                    print(f"Error parsing line: {line} - {str(e)}")
            else:
                continue

        return {
            'items': items,
        }

    def print_receipt(self, parsed_data):
        """Improved receipt printing"""
        
        if parsed_data['items']:
            print("\nDaftar Bahan Belanjaan:")
            
            for item in parsed_data['items']:
                name = (item['nama'][:20] + '..') if len(item['nama']) > 20 else item['nama']
                print(f"- {name:<20}")

            print("\n")

    @staticmethod
    def _load_products_from_file(filepath):
        """
        Memuat produk yang dikenal dan kategori mereka dari file teks.
        Setiap baris dalam file harus dalam format: 'Nama Produk | Kategori'.
        """
        products = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split('|')
                        if len(parts) == 2:
                            product_name = parts[0].strip()
                            category = parts[1].strip()
                            products.append({'name': product_name.lower(), 'category': category})
                        else:
                            print(f"Peringatan: Melewatkan baris yang salah format di product.txt: {line}")
        except FileNotFoundError:
            print(f"Error: File produk '{filepath}' tidak ditemukan. Pastikan 'product.txt' ada di direktori yang sama.")
        return products
    
    def find_closest_product(self, item_name, threshold=60):
        """
        Cari produk paling mirip berdasarkan fuzzy matching yang ditingkatkan.

        Args:
            item_name (str): Nama dari hasil OCR.
            threshold (int): Ambang minimal skor kemiripan.

        Returns:
            dict: Hasil pencocokan produk, termasuk nama, kategori, dan skor.
        """
        best_match = None
        best_score = -1

        item_norm = self._normalize_text(item_name)

        for product in self.known_products:
            product_norm = self._normalize_text(product['name'])

            score = max(
                fuzz.token_set_ratio(item_norm, product_norm),
                fuzz.partial_ratio(item_norm, product_norm),
                fuzz.token_sort_ratio(item_norm, product_norm),
            )

            if score > best_score:
                best_score = score
                best_match = product

        if best_match and best_score >= threshold:
            return {
                'nama': best_match['name'].title(),
                'kategori': best_match['category'],
                'skor_kesamaan': best_score
            }
        else:
            return {
                'nama': item_name.strip(),
                'kategori': 'Tidak Diketahui',
                'skor_kesamaan': best_score
            }

# Contoh penggunaan:      
# if __name__ == "__main__":
#     image_path = r"app\ocr\image-test\struk-1.jpg"

#     try:
#         ocr = ReceiptOCR(image_path=image_path)
        
#         print("Memproses OCR struk...")
#         parsed_data = ocr.parse_receipt()
        
#         # Cetak hasil
#         ocr.print_receipt(parsed_data)
        
#     except Exception as e:
#         print(f"Error: {str(e)}")