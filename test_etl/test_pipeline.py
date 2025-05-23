import unittest
from unittest.mock import patch
from app.etl import pipeline

class TestPipeline(unittest.TestCase):

    @patch("app.etl.pipeline.get_resep_links", return_value=["https://cookpad.com/id/resep/test-resep"])
    @patch("app.etl.pipeline.scrape_resep_detail")
    @patch("app.etl.pipeline.transform_data")
    @patch("app.etl.pipeline.load_and_merge")
    def test_run_pipeline(self, mock_load, mock_transform, mock_scrape, mock_get_links):
        mock_scrape.return_value = {
            "judul": "Test",
            "foto": "",
            "penulis": "tester",
            "porsi": "1",
            "bahan": [],
            "langkah": [],
            "durasi": "10 menit",
            "url": "https://cookpad.com/id/resep/test-resep"
        }
        mock_transform.return_value = []
        pipeline.run_pipeline(["ayam"], max_pages=1)

        self.assertTrue(mock_scrape.called)
        self.assertTrue(mock_transform.called)

if __name__ == '__main__':
    unittest.main()
