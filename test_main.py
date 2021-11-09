import os
import random
import unittest
from main import *

import validators
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        self.radius = random.randint(1, 5000)
        self.zipcode = random.choice([94301, 94302, 94303, 94304, 94305, 94306, 94309, 0, 11111, 333, 45372])
        self.driver = wb.Chrome('chromedriver', options=options)
        self.car_list = get_car_list()
        self.car_links_list = extract_links_from_result(self.car_list)
        self.car_details = get_car_details_from_link(self.car_links_list)

    def test_round_off_radius(self):
        """assert that the radius is correctly rounded off to the nearest 25"""
        r = round_off_radius(self.radius)
        self.assertTrue(r in range(25, 5000, 25))

    def test_do_search(self):
        """assert that scraper object passes in correct selection and input and scrolls to bottom of scroll page and
        assert that search returns True if results and False if not """
        self.driver.get(
            "https://www.tred.com/buy?body_style=&distance=50&exterior_color_id=&make=&miles_max=100000&miles_min=0&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated&status=active&year_end=2022&year_start=1998&zip=")
        do_search(round_off_radius(self.radius), self.zipcode)
        if driver.find_element_by_class_name('search-error'):
            self.assertTrue(False)
        else:
            self.assertTrue(True)

    def test_get_car_list(self):
        """assert car list is scraped from results page"""
        self.assertTrue(len(self.car_list) > 0)

    def test_extract_links_from_result(self):
        """assert car link is extracted from each search result in car list"""
        self.assertTrue(len(self.car_links_list) == len(self.car_list))
        for car_link in self.car_links_list:
            self.assertTrue(validators.url(car_link))

    def test_get_car_details_from_link(self):
        """assert car name, price, list of summary and list of options is saved in list of car details"""
        self.assertTrue(len(self.car_details) == len(self.car_links_list))
        for car in self.car_details:
            self.assertTrue(car['name'] is not None)
            self.assertTrue("'s" and "For Sale" not in car['name'])
            self.assertTrue(car['price'] is not None)
            self.assertTrue(car['summary'] is not None)
            self.assertTrue(car['options'] is not None)

    def test_save_as_xlsx(self, file_name='test_save_as_xlsx.xlsx'):
        """assert that car details are saved as xlsx file"""
        save_as_xlsx(self.car_details, file_name)
        self.assertTrue(os.path.isfile(file_name))

    def tearDown(self) -> None:
        self.driver.quit()


if __name__ == '__main__':
    unittest.main()
