from SeleniumBaCenScraper import Scraper
import os

if __name__ == '__main__':
    # C = Scraper(os.getcwd())
    C = Scraper('/Users/lucaslaheras/PycharmProjects/BaCenDocumentation', 'firefox')

    C.compare_all(send_to_email=True)
    # C.search_main_pix()