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
from txtCompare import txt_is_equal
import time
import zipfile
import pickle
from CompareDir import compare_files
import os
import platform
import threading
from selenium.webdriver.support import expected_conditions as EC


def notify(title, text):
    if platform.system() == 'Darwin':  # macOS
        os.system("""
                  osascript -e 'display notification "{}" with title "{}"'
                  """.format(text, title))
    elif platform.system() == 'Windows':  # Windows
        import win10toast
        toaster = win10toast.ToastNotifier()
        toaster.show_toast(title, text)
    elif platform.system() == 'Linux':  # Linux
        os.system('notify-send "{}" "{}"'.format(title, text))


# To avoid blocking the program, run the notification in a separate thread
def notify_async(title, text, teams_notifier=None):
    threading.Thread(target=notify, args=(title, text)).start()

    if teams_notifier:
        threading.Thread(target=teams_notifier.send_message, args=(title, text)).start()


class Scraper:
    def __init__(self, root_directory, internet_browser='google_chrome', teams_notifier=None):
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
            "Guia do saque e troco": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Guia_Implementacao_Pix_Saque_Troco.pdf",
            "Guia de implementação do canal secundário": "https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Guia_Implementacao_Canal_Secundario_Transmissao_Mensagens.pdf",
            "Manual do BR Code": "https://www.bcb.gov.br/content/estabilidadefinanceira/spb_docs/ManualBRCode.pdf",
            "Manual de Segurança do PIX": "https://www.bcb.gov.br/content/estabilidadefinanceira/cedsfn/Manual_de_Seguranca_PIX.pdf"
        }

        self.pix_descriptions = []

        self.teams_notifier = teams_notifier

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

    def get_url_GuiaMED(self):
        self.driver.get('https://www.bcb.gov.br/estabilidadefinanceira/participantespix')

        xpath = '/html/body/app-root/app-root/div/div/main/dynamic-comp/div/div[3]/div[2]/div/bcb-accordion/div[7]/div/div[2]/div/dynamic-comp/div/ul/li/a'
        # Wait up to 20 seconds for the element to be present
        element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        href = element.get_attribute('href')

        self.name2url["Guia do MED"] = href


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

    def compare_all(self):
        print(
            "The program will download and compare all main descriptions and regulations, it could take a fill minutes")
        self.get_url_GuiaMED()

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
                title = "The description has been updated!"
                message = "The description on the Banco Central do Brasil’s technical documents has been updated. "\
                          "You can find more information at https://www.bcb.gov.br/estabilidadefinanceira/comunicacaodados"

                with open(last_path, 'r') as f:
                    last_description = f.read()
                f.close()
                with open(new_path, 'r') as f:
                    new_description = f.read()
                f.close()

                files_text = "\n\n**Last file:**\n" + "\n" + str(last_description) + "\n\n**New file:**\n" + str(last_description)
                files_text += "\n\n**New file:**\n" + "\n".join(new_description)

                notify_async(title, message + files_text, self.teams_notifier)
                print(title)

                descriptions_changed = True

        # new file will always save
        else:
            shutil.copy(os.path.join(self.temp_directory, "description.txt"), new_path)
            descriptions_changed = True

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

            title = "New Regulations have been found"
            message = f"This new regulations have been found:\n {str(items_set)} \nYou can find more information at " \
                      f"https://www.bcb.gov.br/estabilidadefinanceira/buscanormas?conteudo=pix&tipoDocumento=Todos "

            # Print the new items
            notify_async(title, message, self.teams_notifier)

            print(title)
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

                        shutil.copy(os.path.join(self.temp_directory, name + type_file), new_path)

                        title = f"New changes in {os.path.basename(new_path)}"
                        message = f"Changes have been identified in the regulatory file {os.path.basename(new_path)}"

                        notify_async(title, message, self.teams_notifier)
                        print(title)
                    else:
                        print(name + type_file + ' equal')

                # compare catalog zip
                    # A comparação será atualizada no futuro.
                    #
                    # Próximos passos:
                    # - Salvar Catalogos antigos no old versions
                    # - Realizar comparações dos catalogos relativos (memso nome) da old versions com da temp
                    # - Realizar comparações de diferenças de catalogos novos temp que não existem na old verions

                elif descriptions_changed and catalog_old is not None and type_file == '.zip' and \
                        ('Definições detalhadas das mensagens do Catálogo de Mensagens do SPI' in name):
                    catalog_new = os.path.join(self.temp_directory, name + type_file)
                    # unzip catalog files
                    with zipfile.ZipFile(catalog_new, 'r') as zip:
                        zip.extractall(self.temp_directory)

                    catalog_new = catalog_new.replace('.zip', '').replace(
                        'Definições detalhadas das mensagens do Catálogo de Mensagens do SPI - versão ', 'v')

                    print(f"\n\n\nComparing {os.path.basename(catalog_new)} with {os.path.basename(catalog_old)}")

                    output_dir = os.path.join(self.old_versions_directory, "Diferença Catalogo " + os.path.basename(catalog_new))

                    files_changed = compare_files(catalog_new, catalog_old, output_dir)

                    if len(files_changed) > 0:
                        title = f"The catalog {os.path.basename(catalog_new)} has changes from {os.path.basename(catalog_old)}"
                        message_files_chaged = '\n'.join(map(str, files_changed))
                        message = f"The catalog {os.path.basename(catalog_new)} has changes in this files:\n" + message_files_chaged

                        notify_async(title, message, self.teams_notifier)

                    catalog_old = str(catalog_new)
                    pass
                elif descriptions_changed and type_file == '.zip' and ('Definições detalhadas das mensagens do Catálogo de Mensagens do SPI' in name):
                    catalog_old = os.path.join(self.temp_directory, name + type_file)
                    with zipfile.ZipFile(catalog_old, 'r') as zip:
                        zip.extractall(self.temp_directory)

                    catalog_old = catalog_old.replace('.zip', '').replace(
                        'Definições detalhadas das mensagens do Catálogo de Mensagens do SPI - versão ', 'v')
                    pass

