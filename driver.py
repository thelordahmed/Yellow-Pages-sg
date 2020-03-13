from selenium.webdriver import Chrome
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException, NoSuchElementException
import requests, zipfile, io
from time import sleep
import random
from pubsub import pub

class Driver:
    def __init__(self):
        self.window = self.open()
        pub.sendMessage("driver has loaded")
        self.xpaths = {
            "result": '*//div[@class="list_companies cmc_list"]/div',
            "last_page": '//*[@id="load_companies"]//div[@class="pag"]//li[last()]/a',
            "name": 'div[3]//a[@class="normal_title"]',  # .text
            "address": 'div[3]//div[@class="mapItem"]',  # .text
            "phone": 'div[3]//div[@class="show_number list_comp_label"]/a',  # .get_attribute("href") >> replace("tel:","")
            "website": 'div[3]//div[@class="compnay_website list_comp_label"]/a',  # .get_attribute("href")
            "email": 'div[3]//div[@class="company_enquiry list_comp_label"]/a'  # .get_attribute("data-email")
        }

    #############################################################
    ######### getting search pages urls #########################
    #############################################################
    def pages_links(self):
        """:return a list of all pages links"""
        cur_url = self.window.current_url
        last_page = self.window.find_element_by_xpath(self.xpaths["last_page"]).get_attribute("value")
        pages = []
        for page in range(1,int(last_page)+1):
            if "?page=" in cur_url:
                break
            page = cur_url + f"?page={str(page)}"
            pages.append(page)
        return pages

    @staticmethod
    def get_data(element,xpath, text_or_attr = "text"):  # to simplify the code
        if text_or_attr == "text":
            try:
                data = element.find_element_by_xpath(xpath).text
            except NoSuchElementException:
                data = "-"
            return data
        else:
            try:
                data = element.find_element_by_xpath(xpath).get_attribute(text_or_attr)
            except NoSuchElementException:
                data = "-"
            return data

    @staticmethod
    def open():
        def chromedriver_update(zip_extract_path):
            stable_ver = requests.get("https://chromedriver.storage.googleapis.com/LATEST_RELEASE").text
            file = requests.get(f"https://chromedriver.storage.googleapis.com/{stable_ver}/chromedriver_win32.zip")
            z = zipfile.ZipFile(io.BytesIO(file.content))
            z.extractall(zip_extract_path)

        try:
            win = Chrome(r"C:\ProgramData\chromedriver.exe")
        except SessionNotCreatedException:
            print("chromedriver.exe is outdated .. Updating...")
            chromedriver_update(r"C:\ProgramData")
            win = Chrome(r"C:\ProgramData\chromedriver.exe")
        except WebDriverException:
            print("chromedriver.exe is outdated .. Updating...")
            chromedriver_update(r"C:\ProgramData")
            sleep(1)
            win = Chrome(r"C:\ProgramData\chromedriver.exe")
        win.get("https://www.yellowpages.com.sg")
        return win

