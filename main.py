from SeleniumBaCenScraper import Crawler
import os
from PDFCompare import pdf_is_equal

if __name__ == '__main__':
    C = Crawler(os.getcwd())

    C.compare_all()