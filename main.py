from SeleniumBaCenScraper import Scraper
import os
from TeamsSender import TeamsNotifier
from inputimeout import inputimeout, TimeoutOccurred

def input_with_timeout(prompt, timeout):
    """
    Solicita entrada do usuário com um tempo limite.

    Args:
        prompt (str): Mensagem exibida ao usuário.
        timeout (int): Tempo limite em segundos.

    Returns:
        str or None: Entrada do usuário ou None se o tempo expirar.
    """

    try:
        ans = inputimeout(prompt=prompt, timeout=timeout)
        return ans
    except:
        print("Input timeout. Defaulting to None.")
        return None

def get_teams_webhook_url():
    teams_webhook_url = None
    if os.path.exists('teams_webhook_url.txt'):
        with open('teams_webhook_url.txt', 'r') as f:
            teams_webhook_url = f.read()
    else:
        answer_time = 30

        print("Select the notification method:")
        print("1. Teams incoming webhook")
        print("2. None")
        print("Note: The first execution of items will not trigger a notification.")
        choice = input_with_timeout(f"Enter the number of your choice (1/2) (you have {answer_time} seconds to answer): ", answer_time)

        if choice == '1':
            teams_webhook_url = input("Enter teams webhook url: ")
            with open('teams_webhook_url.txt', 'w') as f:
                f.write(teams_webhook_url)
            return teams_webhook_url
        if choice != '2':
            print("Invalid choice. Defaulting to None.")
        return None


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
    teams_webhook_url = get_teams_webhook_url()
    if teams_webhook_url:
        teams_notifier = TeamsNotifier(webhook_url=teams_webhook_url)
    else:
        teams_notifier = None
    C = Scraper(file_path, browser, teams_notifier)

    C.compare_all()
    # C.search_main_pix()