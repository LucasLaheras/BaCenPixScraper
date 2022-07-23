import copy
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import platform
import sys
from PDFCompare import pdf_is_equal
import urllib.request
from EmailSender import email_sender
import time


class Crawler:
    def __init__(self, root_directory):
        # increase the recursion limit to handle very large searches
        sys.setrecursionlimit(5000)

        # options handler for Google Chrome
        self.options = Options()

        # saves current directory in a string
        self.root_directory = root_directory

        # saves current platform in a string
        self.current_platform = platform.system()

        self.directory_chromedriver = ''
        if self.current_platform == 'Darwin':
            self.directory_chromedriver = os.path.join(self.root_directory, 'ChromeDriver', 'ChromeDriverMac')
        elif self.current_platform == 'Windows':
            self.directory_chromedriver = os.path.join(self.root_directory, 'ChromeDriver', 'ChromeDriverWin.exe')
        else:
            self.directory_chromedriver = os.path.join(self.root_directory, 'ChromeDriver', 'ChromeDriverLin')

        # sets Chrome to run Headless (without showing the navigator window while running)
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')

        # self.options.binary_location = "C:\\Path\\To\\Chrome"

        self.pix_descriptions = []

        self.name2url = None

        self.index_progress_bar = 1

    def search_main_pix(self):
        print("Searching in main PIX")

        driver = webdriver.Chrome(self.directory_chromedriver, chrome_options=self.options)

        driver.get('https://www.bcb.gov.br/estabilidadefinanceira/pix')

        self.pix_descriptions.append("evolutive:")
        for i in range(10):
            try:
                item = driver.find_element_by_xpath(
                    '//*[@id="headingagenda_evolutiva_pix' + str(i) + '"]/button').text

                self.pix_descriptions.append(copy.copy(item))
            except:
                pass

        # closes the Google Chrome
        driver.quit()

    def search_communicatiions_pix(self):
        print("Searching in communications PIX")

        driver = webdriver.Chrome(self.directory_chromedriver, chrome_options=self.options)

        driver.get('https://www.bcb.gov.br/estabilidadefinanceira/comunicacaodados')

        self.pix_descriptions.append("tecnical documents list")
        for i in range(5):
            try:
                item = driver.find_element_by_xpath(
                    '/html/body/app-root/app-root/main/dynamic-comp/div/div/div[1]/div/div[2]/ul/li[' + str(
                        i + 1) + ']').text
                self.pix_descriptions.append(copy.copy(item))
            except:
                pass

        self.pix_descriptions.append("catalog:")

        self.pix_descriptions.append(driver.find_element_by_xpath(
            '/html/body/app-root/app-root/main/dynamic-comp/div/div/div[1]/div/h4[2]').text)

        for i in range(6):
            try:
                item = driver.find_element_by_xpath(
                    '/html/body/app-root/app-root/main/dynamic-comp/div/div/div[1]/div/div[4]/ul/li[' + str(
                        i + 1) + ']').text
                self.pix_descriptions.append(copy.copy(item))
            except:
                pass

        # closes the Google Chrome
        driver.quit()

    def save_pdf_regulation(self):
        print("Searching in regulation PIX")

        self.name2url = {
            "Manual de Marca": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/I_manual_uso_marca_pix.pdf",
            "Manual de Padroes de Iniciacao PIX": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/II_ManualdePadroesparaIniciacaodoPix.pdf",
            "Manual de Fluxos do Processo de Efetivacao_PIX": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/III_ManualdeFluxosdoProcessodeEfetivacaodoPix.pdf",
            "Requisitos Minimos de Experiencia do Usuario": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/IV_RequisitosMinimosparaExperienciadoUsuario.pdf",
            "Manual de Tempos do Pix": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/IX_ManualdeTemposdoPix.pdf",
            "Manual Operacional do DICT": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/X_ManualOperacionaldoDICT.pdf",
            "Manual de Resolucao de Disputas": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/XI_Manual_de_resolucao_de_disputa.pdf"
        }

        for name, url in self.name2url.items():
            urllib.request.urlretrieve(url, os.path.join(self.root_directory, "temp", name + ".pdf"))

    def save_descriptions(self):
        self.search_main_pix()
        self.search_communicatiions_pix()

        string_pix_description = '\n'.join(map(str, self.pix_descriptions))

        file = open(os.path.join(self.root_directory, "temp", "description.txt"), "w")
        file.writelines(string_pix_description)
        file.close()

    def compare_all(self, send_to_email=False):
        print(
            "The program will download and compare all main descriptions and regulations, it could take a fill minutes")

        self.save_descriptions()
        self.save_pdf_regulation()

        file = open(os.path.join(self.root_directory, "temp", "description.txt"))
        data1 = file.read()
        file.close()

        # read last version in path old versions
        version = 0
        while os.path.exists(os.path.join(self.root_directory, "old versions", "descriptionV" + str(version) + ".txt")):
            version += 1

        new_path = os.path.join(self.root_directory, "old versions", "descriptionV" + str(version) + ".txt")
        if version != 0:
            file = open(os.path.join(self.root_directory, "old versions", "descriptionV" + str(version - 1) + ".txt"))
            data2 = file.read()
            file.close()

            if data1 != data2:
                shutil.copy(os.path.join(self.root_directory, "temp", "description.txt"), new_path)

                email_sender(new_path, "Description")
                print("descriptions has been modify!")
        else:
            shutil.copy(os.path.join(self.root_directory, "temp", "description.txt"),
                        os.path.join(self.root_directory, "old versions", "descriptionV" + str(version) + ".txt"))
            if send_to_email:
                email_sender(new_path, "Description")
            print("descriptions has been modify!")

        # Compare pdf if is not None
        if self.name2url:
            for name, url in self.name2url.items():
                version = 0
                while os.path.exists(
                        os.path.join(self.root_directory, "old versions", name + "V" + str(version) + ".pdf")):
                    version += 1
                new_path = os.path.join(self.root_directory, "old versions", name + "V" + str(version) + ".pdf")

                if version == 0 or not(pdf_is_equal(os.path.join(self.root_directory, "temp", name + ".pdf"),
                                os.path.join(self.root_directory, "old versions",
                                             name + "V" + str(version - 1) + ".pdf"))):


                    shutil.copy(os.path.join(self.root_directory, "temp", name + ".pdf"), new_path)
                    if send_to_email:
                        email_sender(new_path, name)
                        time.sleep(10)
                    print(name + " has been modify!")
