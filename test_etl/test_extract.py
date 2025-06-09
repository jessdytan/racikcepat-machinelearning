import unittest
from bs4 import BeautifulSoup
from app.etl import extract

class TestExtractFunctions(unittest.TestCase):

    def test_get_resep_links(self):
        links = extract.get_resep_links("ayam", max_pages=1)
        self.assertIsInstance(links, list)
        self.assertTrue(all(link.startswith("https://cookpad.com/id/resep/") for link in links))

    def test_extract_bahan(self):
        html = '''
        <div class="ingredient-list">
            <ol>
                <li><span><bdi>2</bdi> siung Bawang Putih</span></li>
            </ol>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        result = extract.extract_bahan(soup)
        self.assertEqual(len(result), 1)
        self.assertIn("bahan", result[0])
        self.assertEqual(result[0]["jumlah"], "2")

    def test_extract_langkah(self):
        html = '<ul id="steps"><li><p>Langkah pertama.</p></li></ul>'
        soup = BeautifulSoup(html, 'html.parser')
        result = extract.extract_langkah(soup)
        self.assertEqual(result, ["Langkah pertama."])

    def test_scrape_resep_detail_success(self):
        html = '''
        <html>
            <h1>Ayam Bakar</h1>
            <a href="/pengguna/abc"><span class="font-semibold">Budi</span></a>
            <div id="serving_recipe_123"><span class="mise-icon-text">2 porsi</span></div>
            <div id="cooking_time_recipe_123"><span class="mise-icon-text">1 jam</span></div>
            <img alt="Foto resep ayam" src="https://img-global.cpcdn.com/recipes/abc123/1280x1280sq70/foto.jpg">
        </html>
        '''
        from unittest.mock import patch
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = html
            result = extract.scrape_resep_detail("https://cookpad.com/id/resep/test")
            self.assertIsInstance(result, dict)
            self.assertEqual(result["judul"], "Ayam Bakar")
            self.assertEqual(result["penulis"], "Budi")
            self.assertIn("durasi", result)
            self.assertIn("porsi", result)

    def test_scrape_resep_detail_missing_fields(self):
        html = '<html><body><p>tidak ada h1</p></body></html>' 
        from unittest.mock import patch
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = html
            result = extract.scrape_resep_detail("https://cookpad.com/id/resep/test")
            self.assertIsInstance(result, dict)
            self.assertEqual(result["judul"], "Judul tidak ditemukan")
            self.assertEqual(result["penulis"], "Tidak ditemukan")

    def test_get_resep_links_invalid_page(self):
        from unittest.mock import patch
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Page not found")
            result = extract.get_resep_links("ayam", max_pages=1)
            self.assertEqual(result, []) 

if __name__ == '__main__':
    unittest.main()