import copy
import shutil

import selenium.webdriver.firefox.options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import platform
import sys
from PDFCompare import pdf_is_equal
import urllib.request
from EmailSender import email_sender
from xlsxCompare import xlsx_is_equal
from txtCompare import txt_is_equal
import time
import zipfile


def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


class Scraper:
    def __init__(self, root_directory, internet_browser='google_chrome'):
        # increase the recursion limit to handle very large searches
        sys.setrecursionlimit(5000)

        # saves current directory in a string
        self.root_directory = root_directory

        # saves a temporary directory
        self.temp_directory = os.path.join(self.root_directory, "temp")

        # saves old versions directory
        self.old_versions_directory = os.path.join(self.root_directory, "old versions")

        # saves current platform in a string
        self.current_platform = platform.system()

        self.directory_driver = ''

        self.driver = []

        self.select_browser(internet_browser)

        # define dictionary of all names and urls statics
        self.name2url = {
            "Manual de Marca": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/I_manual_uso_marca_pix.pdf",
            "Manual de Padroes de Iniciacao PIX": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/II_ManualdePadroesparaIniciacaodoPix.pdf",
            "Manual de Fluxos do Processo de Efetivacao_PIX": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/III_ManualdeFluxosdoProcessodeEfetivacaodoPix.pdf",
            "Requisitos Minimos de Experiencia do Usuario": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/IV_RequisitosMinimosparaExperienciadoUsuario.pdf",
            "Manual de Tempos do Pix": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/IX_ManualdeTemposdoPix.pdf",
            "Manual Operacional do DICT": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/X_ManualOperacionaldoDICT.pdf",
            "Manual de Resolucao de Disputas": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/XI_Manual_de_resolucao_de_disputa.pdf",
            "Guia do MED": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Guia%20MED%20-%20vers%C3%A3o%201.0.pdf",
            "Guia do saque e troco": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Guia_Implementacao_Pix_Saque_Troco.pdf",
            "Guia de implementação do canal secundário": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Guia_Implementacao_Canal_Secundario_Transmissao_Mensagens.pdf",
            "Lista de geracao e leitura de QRcodes": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/ListadeverificacaoparageracaoevalidacaodeQRCodes.pdf"
        }

        self.ISO2022 = ['REDA041', 'REDA031', 'REDA022', 'REDA017', 'REDA016', 'REDA014', 'PIBR001', 'PIBR002',
                        'PAIN014', 'PAIN013', 'PACS008', 'PACS004', 'PACS002', 'HEAD001', 'CAMT060', 'CAMT054',
                        'CAMT053', 'CAMT052', 'CAMT014', 'ADMI004', 'ADMI002']

        self.pix_descriptions = []

        self.index_progress_bar = 1

    def select_browser(self, internet_browser):
        if internet_browser == 'google_chrome':
            if self.current_platform == 'Darwin':
                self.directory_driver = os.path.join(self.root_directory, 'ChromeDriver', 'ChromeDriverMac')
            elif self.current_platform == 'Windows':
                self.directory_driver = os.path.join(self.root_directory, 'ChromeDriver', 'ChromeDriverWin.exe')
            else:
                self.directory_driver = os.path.join(self.root_directory, 'ChromeDriver', 'ChromeDriverLin')

            # options handler for Google Chrome
            self.options = selenium.webdriver.chrome.options.Options()

            # sets Chrome to run Headless (without showing the navigator window while running)
            # self.options.add_argument('--window-size=1920,1080')
            # self.options.add_argument('--start-maximized')
            self.options.add_argument('--headless')
            # self.options.add_argument('--no-sandbox')
            # self.options.add_argument('--disable-gpu')

            self.driver = webdriver.Chrome(self.directory_driver, options=self.options)

        elif internet_browser == 'firefox':
            if self.current_platform == 'Darwin':
                self.directory_driver = os.path.join(self.root_directory, 'FirefoxDriver', 'FirefoxDriverMac')
            elif self.current_platform == 'Windows':
                self.directory_driver = os.path.join(self.root_directory, 'FirefoxDriver', 'FirefoxDriverWin.exe')
            else:
                self.directory_driver = os.path.join(self.root_directory, 'ChromeDriver', 'FirefoxDriverLin')

            # options handler for Firefox
            self.options = selenium.webdriver.firefox.options.Options()

            # sets Firefox to run Headless (without showing the navigator window while running)
            self.options.headless = True

            self.driver = webdriver.Firefox(executable_path=self.directory_driver, options=self.options)

    def search_main_pix(self):
        print("Searching in main PIX")

        self.driver.get('https://www.bcb.gov.br/estabilidadefinanceira/pix')
        time.sleep(10)

        self.pix_descriptions.append("evolutive:")
        for i in range(10):
            try:
                item = self.driver.find_element_by_xpath(
                    '//*[@id="headingagenda_evolutiva_pix' + str(i) + '"]/button/span[1]').text

                self.pix_descriptions.append(copy.copy(item))
            except:
                pass

    def search_communications_pix(self):
        print("Searching in communications PIX")

        self.driver.get('https://www.bcb.gov.br/estabilidadefinanceira/comunicacaodados')
        time.sleep(10)

        self.pix_descriptions.append("tecnical documents list")
        for i in range(20):
            try:
                item = self.driver.find_element_by_xpath(
                    '/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div/div[1]/div/div[2]/ul/li[' + str(
                        i + 1) + ']/a').text
                self.pix_descriptions.append(copy.copy(item))
            except:
                pass

        self.get_catalog_href()

        self.pix_descriptions.append("catalog:")

        self.pix_descriptions.append(self.driver.find_element_by_xpath(
            '/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div/div[1]/div/h4[2]').text)

        for i in range(30):
            try:
                item = self.driver.find_element_by_xpath(
                    '/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div/div[1]/div/div[4]/ul/li[' + str(
                        i + 1) + ']').text
                self.pix_descriptions.append(copy.copy(item))
            except:
                pass

    # download url items to temp directory
    def download_url_files(self):
        print("Downloading files")
        name = None

        try:
            for name, url in self.name2url.items():
                type_file = url[url.rfind('.'):]
                urllib.request.urlretrieve(url, os.path.join(self.temp_directory, name + type_file))
        except:
            print(name)

    # search for names and urls related with catalog
    def get_catalog_href(self):

        for i in range(20):
            try:
                item = self.driver.find_element_by_xpath(
                    '/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div/div[1]/div/div[2]/ul/li[' + str(
                        i + 1) + ']/a')
                name = item.text[:item.text.rfind(' (')]

                self.name2url[name] = item.get_attribute("href")

            except:
                pass

        return self.name2url

    def save_descriptions(self):
        self.search_main_pix()
        self.search_communications_pix()

        string_pix_description = '\n'.join(map(str, self.pix_descriptions))

        file = open(os.path.join(self.temp_directory, 'description.txt'), 'w')
        file.writelines(string_pix_description)
        file.close()

    def get_version_path_name(self, name, type_file):
        version = 0
        new_path = os.path.join(self.old_versions_directory, name + 'V' + str(version) + type_file)
        last_path = None
        while os.path.exists(new_path):
            last_path = os.path.join(self.old_versions_directory, name + 'V' + str(version) + type_file)
            version += 1
            new_path = os.path.join(self.old_versions_directory, name + 'V' + str(version) + type_file)

        return new_path, last_path

    def compare_catalog(self, catalog_new, catalog_old):
        # unzip catalog files
        with zipfile.ZipFile(catalog_new, 'r') as zip:
            zip.extractall(self.temp_directory)

        with zipfile.ZipFile(catalog_old, 'r') as zip:
            zip.extractall(self.temp_directory)

        catalog_new = catalog_new.replace('.zip', '').replace('Definições detalhadas das mensagens do Catálogo de Mensagens do SPI - versão ', 'v')
        catalog_old = catalog_old.replace('.zip', '').replace('Definições detalhadas das mensagens do Catálogo de Mensagens do SPI - versão ', 'v')

        for item in self.ISO2022:
            diff_file_name = catalog_new[catalog_new.rfind('/') + 1:] + ' ' + item + ' diferences.xlsx'

            equal = xlsx_is_equal(os.path.join(catalog_new, 'xlsx', item + '.xlsx'),
                                  os.path.join(catalog_old, 'xlsx', item + '.xlsx'),
                                  os.path.join(self.old_versions_directory, diff_file_name))

            if equal:
                print(item + ' equal')
            else:
                notify("Alert", item + ' has been modify!')
                print(item + ' has been modify!')

    def compare_all(self, send_to_email=False):
        print(
            "The program will download and compare all main descriptions and regulations, it could take a fill minutes")

        self.save_descriptions()

        self.driver.quit()

        self.download_url_files()

        # read last version in path old versions
        new_path, last_path = self.get_version_path_name("description", ".txt")

        descriptions_changed = False

        # compare descriptions
        if last_path is not None:
            if txt_is_equal(os.path.join(self.temp_directory, "description.txt"), last_path):
                print("descriptions equal")

            else:
                shutil.copy(os.path.join(self.temp_directory, "description.txt"), new_path)
                notify("Alert", 'description has been modify!')
                print("descriptions has been modify!")

                descriptions_changed = True

                if send_to_email:
                    email_sender(new_path, "Description")

        # new file will always save
        else:
            notify("Alert", 'description has been modify!')
            shutil.copy(os.path.join(self.temp_directory, "description.txt"), new_path)
            descriptions_changed = True
            if send_to_email:
                email_sender(new_path, "Description.txt")
            print("descriptions equal")

        # Compare files
        if self.name2url:
            catalog_old = None

            # for each file downloaded compare
            for name, url in self.name2url.items():
                type_file = url[url.rfind('.'):]
                new_path, last_path = self.get_version_path_name(name, type_file)

                # compare pdf
                if type_file == '.pdf':
                    if last_path is None or not(pdf_is_equal(os.path.join(self.temp_directory, name + type_file),
                                                             last_path)):
                        notify("Alert", name + type_file + ' has been modify!')
                        print(name + type_file + ' has been modify!')
                        shutil.copy(os.path.join(self.temp_directory, name + type_file), new_path)
                        if send_to_email:
                            email_sender(new_path, name + type_file)
                            time.sleep(10)
                    else:
                        print(name + type_file + ' equal')

                # compare catalog zip
                elif type_file == '.zip' and descriptions_changed and ('Definições detalhadas das mensagens do Catálogo de Mensagens do SPI' in name) and catalog_old is not None:
                    self.compare_catalog(os.path.join(self.temp_directory, name + type_file), catalog_old)
                    pass
                elif type_file == '.zip' and descriptions_changed and ('Definições detalhadas das mensagens do Catálogo de Mensagens do SPI' in name):
                    catalog_old = os.path.join(self.temp_directory, name + type_file)
                    pass

