from SeleniumBaCenScraper import Crawler
import os

if __name__ == '__main__':
    C = Crawler(os.getcwd())

    C.compare_all(send_to_email=True)