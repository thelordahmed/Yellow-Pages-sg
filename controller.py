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
import webbrowser
import csv


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
        self.modelConn2 = Model()
        self.view = View()
        self.driver = None
        self.process_thread = Thread(target=self.process)
        self.singals = Singals()
        self.pages = None
        self.view.statusbar.showMessage(">>>    Loading the browser... ")

################################################################
########################   SIGNALS   ###########################
################################################################
        self.singals.trigger.connect(self.view.addToTableWidget)
        self.singals.barTrigger.connect(self.view.barIncreament)
        self.singals.lcdTrigger.connect(self.view.lcdCounter)
        self.view.start_btn.clicked.connect(self.start_process)
        self.view.stop_btn.clicked.connect(self.stop_func)
        self.view.commandLinkButton.clicked.connect(self.copyright_func)
        self.view.clear_btn.clicked.connect(self.clear_func)
        self.view.save_btn.clicked.connect(self.export_func)
################################################################
        self.loadDataToView()   # this must come after connections made (to activate the lcd signal)


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
# PAGE LOOP
        for index, page in enumerate(self.pages):
            if self.stopChecker == 1:
                break
            if self.model.findUrl(page) is not None:
                continue
            self.view.statusbar.showMessage(">>>    Delaying Randomly (10-25 seconds) to avoid block... ")
            sleep(random.randint(15,25))  # to break the pattern
            if self.stopChecker == 0:
                self.view.statusbar.showMessage(">>>    Scraping the data... ")
            win.get(page)
            results = win.find_elements_by_xpath(self.driver.xpaths["result"])
    # RESULT LOOP
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
                self.model.addTodata((name, address, phone, email, website, page))          ## ---> Model
                self.singals.trigger.emit((name, address, phone, email, website))           ## ---> TableWidget
                self.singals.lcdTrigger.emit()                                              ## ---> LCDCounter
            # increasing the PROGRESS BAR
            steps = index + 1
            self.singals.barTrigger.emit(steps)

        self.stopProcess()

    def stopProcess(self):
        self.stopChecker = 0
        self.view.stop_btn.setDisabled(True)
        self.view.start_btn.setEnabled(True)
        self.view.start_btn.setFocus()
        self.view.statusbar.showMessage(">>>    Ready! ")


    def loadDataToView(self):
        records = self.modelConn2.getAllRecords()
        for tup in records:
            self.view.addToTableWidget(tup)
        self.singals.lcdTrigger.emit()

##########################################
############   SLOTS   ###################
##########################################

    def start_process(self):
        self.process_thread = Thread(target=self.process)
        self.process_thread.start()
        self.view.stop_btn.setEnabled(True)
        self.view.start_btn.setDisabled(True)
        self.view.stop_btn.setFocus()

    def stop_func(self):
        self.view.statusbar.showMessage(">>>    Stopping...")
        self.stopChecker = 1

    def clear_func(self):
        re = self.view.message("Confirm Clearing", "Do you wanna Delete all records ?", "warning")
        if re is True:
            self.view.tableWidget.setRowCount(0)   ## that removes all rows items
            self.modelConn2.clearDatabase()
            self.singals.lcdTrigger.emit()
            self.view.progressBar.reset()

    def export_func(self):
        try:
            path = self.view.saveDialog()
            data = self.modelConn2.getAllRecords()
            with open(path, "w", encoding = "utf-8", newline = "") as f:
                for row in data:
                    writer = csv.writer(f)
                    writer.writerow(row)
        except FileNotFoundError:
            print("saving cancelled!")


    @staticmethod
    def copyright_func():
        webbrowser.open("https://www.fiverr.com/lordahmed")


if __name__ == "__main__":
    app = QApplication()
    controller = Controller()
    app.exec_()