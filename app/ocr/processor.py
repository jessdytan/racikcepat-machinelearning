import cv2
import numpy as np
import pytesseract
from PIL import Image
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ReceiptOCR:
    def __init__(self, image_path):
        self.image_path = image_path
        self.original = cv2.imread(image_path)
        if self.original is None:
            raise ValueError("Gambar tidak dapat dimuat - periksa path")
        
        # Storage for processed images
        self.gray = None
        self.denoised = None
        self.thresholded = None
        self.deskewed = None

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

        # Morph ops (sedikit erosi lalu dilasi) → bersih tanpa kehilangan teks
        kernel = np.ones((2, 2), np.uint8)
        self.final = cv2.morphologyEx(self.thresholded, cv2.MORPH_OPEN, kernel)

        cv2.imwrite("preprocessed_debug.png", self.final)

        return self.final

    def extract_text(self):
        """Text extraction with optimized settings for receipts"""
        if not hasattr(self, 'final'):
            self.preprocess()
        
        # Custom configuration for receipt OCR
        config = r'--oem 3 --psm 6 -l ind+eng'
        
        text = pytesseract.image_to_string(
            Image.fromarray(self.final),
            config=config
        )
        
        return text

    def parse_receipt(self):
        """Improved parsing for Alfamart/Indomaret receipts"""
        text = self.extract_text()
        # print("\n--- TEXT HASIL OCR ---")
        # print(text)  # DEBUG: cek hasil OCR mentah

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
                line.startswith(('Daftar', 'Qty', '----', 'HARGA', 'TOTAL', 'TUNAT', 'KEMBALI', 'PPN', 'LAYANAN'))):
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
        
if __name__ == "__main__":
    image_path = r"app\ocr\image-test\struk-1.jpg"

    try:
        ocr = ReceiptOCR(image_path=image_path)
        
        print("Memproses OCR struk...")
        parsed_data = ocr.parse_receipt()
        
        # Cetak hasil
        ocr.print_receipt(parsed_data)
        
    except Exception as e:
        print(f"Error: {str(e)}")