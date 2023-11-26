from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import xml


class Pararius:
    def __init__(self, url="https://www.pararius.com/apartments/amsterdam?ac=1", headless=True):
        """
        Initialize the Pararius site with the specified URL and headless mode option.

        Parameters:
        - url (str): The URL of the Pararius page to scrape.
        - headless (bool): Flag to run Chrome in headless mode .
        """
        self.url = url
        self.headless = headless

    def get_page_source(self):
        """
        Open the Pararius page using Chrome WebDriver.

        Returns:
        - str: Page source after JavaScript execution.
        """
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.url)
        # 10 seconds wait time because of dynamic loading
        driver.implicitly_wait(10)
        page_source = driver.page_source
        # Close webdriver
        driver.quit()

        return page_source

    def scrape_listings(self):
        """
        Scrape Pararius page for apartment listings and return the data as a DataFrame.

        Returns:
        - pd.DataFrame: DataFrame containing apartment listing data.
        """
        # Get the page source after JavaScript execution by calling method
        page_source = self.get_page_source()

        # Use BeautifulSoup to parse the page source
        soup = BeautifulSoup(page_source, "html.parser")

        # Find all apartment listings on the page
        apartment_details = soup.find_all("section", class_="listing-search-item")

        data = []

        # Extract information from each listing
        for listing in apartment_details:
            """Exract required findings by inspecting script <a class="listing-search-item__link listing-search-item__link--title" href="/apartment-for-rent/amsterdam/cbc0b9c6/singel" data-action="click->listing-search-item#onClick">

            Flat Singel</a>"""
            title_elem = listing.find(
                "a", class_="listing-search-item__link listing-search-item__link--title"
            )
            # strip the text
            title_text = title_elem.text.strip() if title_elem else "NoData"

            # Extract location information by using lambda function
            location_elem = listing.find(
                "div", class_=lambda value: value and "sub-title" in value
            )
            location_text = location_elem.text.strip() if location_elem else "NoData"

            # Extract price information
            price_elem = listing.find("div", class_="listing-search-item__price")
            price_text = price_elem.text.strip() if price_elem else "NoData"

            # Extract number of rooms information
            rooms_elem = listing.find(
                "li", class_=lambda value: value and "number-of-rooms" in value
            )
            rooms_text = rooms_elem.text.strip() if rooms_elem else "Nodata"

            # Extract area information
            area_elem = listing.find(
                "li",
                class_="illustrated-features__item illustrated-features__item--surface-area",
            )
            area_text = area_elem.text.strip() if area_elem else "NoData"

            # Create a dictionary for each listing and append to data list
            info = {
                "Flat": title_text,
                "Location": location_text,
                "Price": price_text,
                "Area": area_text,
                "Number of Rooms": rooms_text,
            }
            data.append(info)

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data)
        return df


