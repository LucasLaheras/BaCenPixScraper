from SeleniumBaCenScraper import Scraper
import os

def get_file_path():
    file_path = None
    if os.path.exists('file_path.txt'):
        with open('file_path.txt', 'r') as f:
            file_path = f.read()
    else:
        file_path = input("Please enter the file path: ")
        with open('file_path.txt', 'w') as f:
            f.write(file_path)
    return file_path

def get_browser():
    browser = None
    if os.path.exists('browser.txt'):
        with open('browser.txt', 'r') as f:
            browser = f.read()
    else:
        print("Please select a browser:")
        print("1. Google Chrome")
        print("2. Firefox")
        print("3. Safari")
        print("4. Edge")
        choice = input("Enter the number of your choice: ")
        if choice == '1':
            browser = 'google_chrome'
        elif choice == '2':
            browser = 'firefox'
        elif choice == '3':
            browser = 'safari'
        elif choice == '4':
            browser = 'edge'
        else:
            print("Invalid choice. Defaulting to Firefox.")
            browser = 'firefox'
        with open('browser.txt', 'w') as f:
            f.write(browser)
    return browser

if __name__ == '__main__':
    file_path = get_file_path()
    browser = get_browser()
    C = Scraper(file_path, browser)

    C.compare_all(send_to_email=False)
    # C.search_main_pix()