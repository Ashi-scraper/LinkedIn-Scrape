import unittest
from selenium.webdriver.chrome.options import Options
from linkedin_scraper import setup_driver, extract_profile_details  # Import your functions
from unittest.mock import MagicMock

class TestLinkedInScraper(unittest.TestCase):

    def test_setup_driver(self):
        """Test if the Selenium driver is initialized correctly."""
        driver, wait = setup_driver()
        self.assertIsNotNone(driver)
        self.assertIsNotNone(wait)
        driver.quit()  # Close driver after testing

    def test_extract_profile_details(self):
        """Test if extract_profile_details returns valid data structure."""
        mock_driver = MagicMock()
        mock_wait = MagicMock()

        # Simulated LinkedIn profile URL
        profile_link = "https://www.linkedin.com/in/sample-profile/"

        profile_data = extract_profile_details(mock_driver, mock_wait, profile_link)

        self.assertIsInstance(profile_data, dict)
        self.assertIn("profile_url", profile_data)
        self.assertIn("name", profile_data)
        self.assertIn("headline", profile_data)
        self.assertIn("experience", profile_data)
        self.assertIn("education", profile_data)

if __name__ == "__main__":
    unittest.main()
