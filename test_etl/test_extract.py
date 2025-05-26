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

    def test_extract_langkah(self):
        html = '<ul id="steps"><li><p>Langkah pertama.</p></li></ul>'
        soup = BeautifulSoup(html, 'html.parser')
        result = extract.extract_langkah(soup)
        self.assertEqual(result, ["Langkah pertama."])

if __name__ == '__main__':
    unittest.main()
