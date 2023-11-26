import pandas as pd
import requests
from bs4 import BeautifulSoup


class Sitemap:
    def __init__(self, base_url="https://openai.com/"):
        """
        Initialize the Sitemap scraper with a base URL.

        Parameters:
        - base_url (str): The base URL of the website containing the sitemap.
        """
        self.base_url = base_url

    def robots_txt(self):
        """
        Fetch the content of the robots.txt file for the website.

        Returns:
        - str: Content of the robots.txt file.
        """
        robots_url = f"{self.base_url}/robots.txt"
        response = requests.get(robots_url)
        return response.text

    def parse_sitemaps(self, robots_txt):
        """
        Parse sitemap URLs from the content of the robots.txt file.

        Parameters:
        - robots_txt (str): Content of the robots.txt file.

        Returns:
        - list: List of sitemap URLs.
        """
        sitemap_urls = []

        # Parse the robots.txt file to find sitemap URLs
        for line in robots_txt.split("\n"):
            if line.startswith("Sitemap:"):
                sitemap_url = line.split(":", 1)[1].strip()
                sitemap_urls.append(sitemap_url)

        return sitemap_urls

    def sitemap_content(self, sitemap_url):
        """
        Fetch the content of a specific sitemap.

        Parameters:
        - sitemap_url (str): URL of the sitemap.

        Returns:
        - str: Content of the sitemap.
        """
        response = requests.get(sitemap_url)
        return response.text

    def xml_to_df(self, xml_data):
        """
        Parse XML data and convert it into a DataFrame.

        Parameters:
        - xml_data (str): XML content.

        Returns:
        - pd.DataFrame: DataFrame containing parsed data from the XML.
        """
        root = BeautifulSoup(xml_data, "xml")
        all_records = []

        # Assuming each 'url' element in the XML contains the data record
        for url in root.find_all("url"):
            loc_elem = url.find("loc")
            loc_e = url.find("lastmod")
            frequency = url.find("changefreq")

            if loc_elem:
                record = {
                    "loc": loc_elem.text,
                    "last modified": loc_e,
                    "Url_Change_frequency": frequency,
                }
                all_records.append(record)

        return pd.DataFrame(all_records)

    def run(self):
        """
        Run the sitemap scraper to fetch and parse data from sitemaps.

        Returns:
        - pd.DataFrame: Combined data from all sitemaps into a single DataFrame.
        """
        # Fetch and parse robots.txt
        robots_txt = self.robots_txt()

        # Parse sitemaps from robots.txt
        sitemap_urls = self.parse_sitemaps(robots_txt)

        # Fetch and parse data from each sitemap
        all_data = []
        for sitemap_url in sitemap_urls:
            sitemap_content = self.sitemap_content(sitemap_url)
            sitemap_data = self.xml_to_df(sitemap_content)
            all_data.append(sitemap_data)

        # Combine data from all sitemaps into a single DataFrame
        result_df = pd.concat(all_data, ignore_index=True)

        return result_df
