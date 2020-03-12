from view import View
from model import Model
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from threading import Thread
from driver import Driver
from selenium.common.exceptions import NoSuchElementException
import random
from time import sleep


class Singals(QObject):
    trigger = Signal(tuple)
    barTrigger = Signal(int)
    lcdTrigger = Signal()


class Controller():
    stopChecker = 0
    isThisFirstRun = True

    def __init__(self):
        self.driver_thread = Thread(target=self.start_driver).start()  # a thread for the driver to open the browser at the same time with bot
        self.model = None
        self.view = View()
        self.driver = None
        self.process_thread = Thread(target=self.process)
        self.singals = Singals()
        self.pages = None

################################################################
########################   SIGNALS   ###########################
################################################################
        self.singals.trigger.connect(self.view.addToTableWidget)
        self.singals.barTrigger.connect(self.view.barIncreament)
        self.singals.lcdTrigger.connect(self.view.lcdCounter)
        self.view.start_btn.clicked.connect(self.start_process)
        self.view.stop_btn.clicked.connect(self.stop_func)
################################################################



    def start_driver(self):
        win = Driver()
        self.driver = win


    #############################################################
    ######### the main loop #####################################
    #############################################################


    def process(self):
        self.model = Model()  # sqlite3 must be in same thread
        win = self.driver.window
        try:
            returnedPages = self.driver.pages_links()
        except NoSuchElementException:
            self.stopProcess()
            return False  # just to get out of the function
        if len(returnedPages) > 0:  # zero means that we found "?page=" in the current url .. means we are in the same search
            self.pages =returnedPages
        self.view.progressBar.setRange(0, len(self.pages))
        # this counter will count how many pages skipped ..
        # if no pages skipped (counter = 0) means that we are in a new search >> so reassign the pages list


        for index, page in enumerate(self.pages):
            if self.stopChecker == 1:
                break
            if self.model.findUrl(page) is not None:
                continue

            # sleep(random.randint(10,25))  # to break the pattern
            win.get(page)
            results = win.find_elements_by_xpath(self.driver.xpaths["result"])
            for result in results:
                if self.stopChecker == 1:
                    break
                name = self.driver.get_data(result, self.driver.xpaths["name"])
                address = self.driver.get_data(result, self.driver.xpaths["address"])
                phone = self.driver.get_data(result, self.driver.xpaths["phone"], "href").replace("tel:", "")
                email = self.driver.get_data(result, self.driver.xpaths["email"], "data-email")
                website = self.driver.get_data(result, self.driver.xpaths["website"], "href")
                # removing it to avoid a bug in the view (it shows https://...)
                if "https://" in website:
                    website = website.replace("https://", "")
                elif "http://" in website:
                    website = website.replace("http://", "")
                self.model.addTodata((name, address, phone, email, website, page))                ## ---> Model
                self.singals.trigger.emit((name, address, phone, email, website))         ## ---> TableWidget
                self.singals.lcdTrigger.emit()
            # incrementing the PROGRESS BAR
            steps = index + 1
            self.singals.barTrigger.emit(steps)

        self.stopProcess()


    def stopProcess(self):
        self.stopChecker = 0
        self.view.stop_btn.setDisabled(True)
        self.view.start_btn.setEnabled(True)
##########################################
############   SLOTS   ###################
##########################################


    def start_process(self):
        self.process_thread = Thread(target=self.process)
        self.process_thread.start()
        self.view.stop_btn.setEnabled(True)
        self.view.start_btn.setDisabled(True)

    def stop_func(self):
        self.stopChecker = 1

    def clear_func(self):
        pass

    def export_func(self):
        pass


if __name__ == "__main__":
    app = QApplication()
    controller = Controller()
    app.exec_()