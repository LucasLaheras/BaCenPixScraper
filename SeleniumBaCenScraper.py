import copy
import shutil
import selenium.webdriver.firefox.options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import sys
from PDFCompare import compare_pdfs
import urllib.request
from EmailSender import email_sender
from txtCompare import txt_is_equal
import time
import zipfile
import pickle
from CompareDir import compare_files
import os
import platform

def notify(title, text):
    if platform.system() == 'Darwin':  # macOS
        os.system("""
                  osascript -e 'display notification "{}" with title "{}"'
                  """.format(text, title))
    elif platform.system() == 'Windows':  # Windows
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, title, 0)
    elif platform.system() == 'Linux':  # Linux
        os.system('notify-send "{}" "{}"'.format(title, text))


class Scraper:
    def __init__(self, root_directory, internet_browser='google_chrome'):
        # increase the recursion limit to handle very large searches
        sys.setrecursionlimit(5000)

        # saves current directory in a string
        self.root_directory = root_directory

        # saves a temporary directory
        self.temp_directory = os.path.join(self.root_directory, "temp")
        os.makedirs(os.path.dirname(self.temp_directory), exist_ok=True)

        # saves old versions directory
        self.old_versions_directory = os.path.join(self.root_directory, "old versions")
        os.makedirs(os.path.dirname(self.old_versions_directory), exist_ok=True)

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
            "Guia do MED": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Guia%20MED%20-%20vers%C3%A3o%202.0.pdf",
            "Guia do saque e troco": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Guia_Implementacao_Pix_Saque_Troco.pdf",
            "Guia de implementação do canal secundário": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Guia_Implementacao_Canal_Secundario_Transmissao_Mensagens.pdf",
            "Manual do BR Code": "https://www.bcb.gov.br/content/estabilidadefinanceira/spb_docs/ManualBRCode.pdf",
            "Manual de Segurança do PIX": "https://www.bcb.gov.br/content/estabilidadefinanceira/cedsfn/Manual_de_Seguranca_PIX.pdf"
        }

        self.ISO2022 = ['REDA041', 'REDA031', 'REDA022', 'REDA017', 'REDA016', 'REDA014', 'PIBR001', 'PIBR002',
                        'PAIN014', 'PAIN013', 'PACS008', 'PACS004', 'PACS002', 'HEAD001', 'CAMT060', 'CAMT054',
                        'CAMT053', 'CAMT052', 'CAMT014', 'ADMI004', 'ADMI002', 'PAIN009', 'PAIN011', 'PAIN012',
                        'CAMT055', 'CAMT029']

        self.pix_descriptions = []

        self.index_progress_bar = 1

    def select_browser(self, internet_browser):
        if internet_browser == 'google_chrome':
            # options handler for chrome to run Headless
            self.options = selenium.webdriver.chrome.options.Options()
            self.options.headless = True

            self.driver = webdriver.Chrome(options=self.options)

        elif internet_browser == 'firefox':
            # options handler for Firefox to run Headless
            self.options = selenium.webdriver.firefox.options.Options()
            self.options.headless = True

            self.driver = webdriver.Firefox(options=self.options)

        elif internet_browser == 'safari':
            self.options = selenium.webdriver.safari.options.Options()
            self.options.headless = True

            self.driver = selenium.webdriver.Safari(options=self.options)

        elif internet_browser == 'edge':
            self.options = selenium.webdriver.edge.options.Options()
            self.options.headless = True

            self.driver = selenium.webdriver.Edge(options=self.options)


    def search_main_pix(self):
        print("Searching in main PIX")

        self.driver.get('https://www.bcb.gov.br/estabilidadefinanceira/pix')
        WebDriverWait(self.driver, 10).until(lambda x: x.find_element(By.XPATH, '//*[@id="headingagenda_evolutiva_pix0"]/button/span[1]'))

        self.pix_descriptions.append("evolutive:")
        for i in range(10):
            try:
                item = self.driver.find_element(By.XPATH,
                    '//*[@id="headingagenda_evolutiva_pix' + str(i) + '"]/button/span[1]').text

                self.pix_descriptions.append(copy.copy(item))
            except:
                pass

    def search_communications_pix(self):
        print("Searching in communications PIX")

        self.driver.get('https://www.bcb.gov.br/estabilidadefinanceira/comunicacaodados')
        WebDriverWait(self.driver, 10).until(lambda x: x.find_element(By.XPATH,
                    '/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div/div[1]/div/div[2]/ul/li[1]/a'))


        self.pix_descriptions.append("tecnical documents list")

        for i in range(20):
            try:
                item = self.driver.find_element(By.XPATH,
                    '/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div/div[1]/div/div[2]/ul/li[' + str(
                        i + 1) + ']/a').text
                self.pix_descriptions.append(copy.copy(item))
            except:
                pass

        self.get_catalog_href()

        self.pix_descriptions.append("catalog:")

        self.pix_descriptions.append(self.driver.find_element(By.XPATH,
            '/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div/div[1]/div/h4[2]').text)

        for i in range(30):
            try:
                item = self.driver.find_element(By.XPATH,
                    '/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div/div[1]/div/div[4]/ul/li[' + str(
                        i + 1) + ']').text
                self.pix_descriptions.append(copy.copy(item))
            except:
                pass

    # download url items to temp directory
    def download_url_files(self):
        print("Downloading files")
        name = None


        for name, url in self.name2url.items():
            try:
                type_file = url[url.rfind('.'):]
                urllib.request.urlretrieve(url, os.path.join(self.temp_directory, name + type_file))
                print("Download " + name)
            except:
                print("ERROR Download " + name)

    # search for names and urls related with catalog
    def get_catalog_href(self):

        for i in range(20):
            try:
                item = self.driver.find_element(By.XPATH,
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

    def save_regulations(self):
        # Navigate to the website
        self.driver.get("https://www.bcb.gov.br/estabilidadefinanceira/buscanormas?conteudo=pix&tipoDocumento=Todos")

        # Wait for the page to load
        self.wait = WebDriverWait(self.driver, 10)

        # Wait for the element to be present
        WebDriverWait(self.driver, 10).until(
            lambda x: x.find_element(By.CLASS_NAME, "encontrados")
        )

        item = self.driver.find_element(By.CLASS_NAME, "encontrados")

        normas_list_items = item.text.split("\n")

        items_set = set()
        conjunto = ""
        i = 0
        for item in normas_list_items:
            conjunto = conjunto + item + "\n"
            i += 1

            if i == 4:
                items_set.add(conjunto)
                conjunto = ""
                i = 0
        with open(os.path.join(self.temp_directory, 'Binary Regulations.txt'), 'wb') as f:
            pickle.dump(items_set, f)
        f.close()

    def compare_all(self, send_to_email=False):
        print(
            "The program will download and compare all main descriptions and regulations, it could take a fill minutes")

        self.save_descriptions()

        self.save_regulations()

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

        # Compare Regulations
        binary_new_path, binary_last_path = self.get_version_path_name("Binary Regulations", ".txt")
        new_path, last_path = self.get_version_path_name("Regulations", ".txt")

        # Load existing items from the text file
        try:
            with open(binary_last_path, "rb") as f:
                existing_items = pickle.load(f)
            f.close()
        except:
            existing_items = set()

        with open(os.path.join(self.temp_directory, 'Binary Regulations.txt'), "rb") as f:
            items_set = pickle.load(f)
        f.close()

        # Get union of sets to save all regulations to future compares
        union_set = items_set.union(existing_items)

        # Identify new items by comparing the items in items_set with the existing_items and selecting the ones that are not already present
        items_set.difference_update(existing_items)

        if len(items_set) != 0:
            with open(binary_new_path, 'wb') as f:
                pickle.dump(union_set, f)

            # Print the new items
            notify("Alert", "New Regulations have been found!")
            print("New Regulations have been found!")
            with open(new_path, 'w', encoding="utf-8") as f:
                for item in items_set:
                    f.write(item)
                    print(item)
            f.close()
        else:
            print("Regulations equal")


        # Compare files
        if self.name2url:
            catalog_old = None

            # for each file downloaded compare
            for name, url in self.name2url.items():
                type_file = url[url.rfind('.'):]
                new_path, last_path = self.get_version_path_name(name, type_file)

                # compare pdf
                if type_file == '.pdf':
                    if last_path is None or not(compare_pdfs(os.path.join(self.temp_directory, name + type_file),
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
                elif descriptions_changed and catalog_old is not None and type_file == '.zip' and ('Definições detalhadas das mensagens do Catálogo de Mensagens do SPI' in name):
                    catalog_new = os.path.join(self.temp_directory, name + type_file)
                    # unzip catalog files
                    with zipfile.ZipFile(catalog_new, 'r') as zip:
                        zip.extractall(self.temp_directory)

                    catalog_new = catalog_new.replace('.zip', '').replace(
                        'Definições detalhadas das mensagens do Catálogo de Mensagens do SPI - versão ', 'v')

                    print(f"\n\n\nComparing {os.path.basename(catalog_new)} with {os.path.basename(catalog_old)}")

                    compare_files(catalog_new, catalog_old, os.path.join(self.old_versions_directory, "Diferença Catalogo " + os.path.basename(catalog_new)))

                    catalog_old = str(catalog_new)
                    pass
                elif descriptions_changed and type_file == '.zip' and ('Definições detalhadas das mensagens do Catálogo de Mensagens do SPI' in name):
                    catalog_old = os.path.join(self.temp_directory, name + type_file)
                    with zipfile.ZipFile(catalog_old, 'r') as zip:
                        zip.extractall(self.temp_directory)

                    catalog_old = catalog_old.replace('.zip', '').replace(
                        'Definições detalhadas das mensagens do Catálogo de Mensagens do SPI - versão ', 'v')
                    pass

