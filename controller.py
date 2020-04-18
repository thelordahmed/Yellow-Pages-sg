from view import View
from model import Model
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from threading import Thread
from driver import Driver
from selenium.common.exceptions import NoSuchElementException
import random
from time import sleep
import webbrowser
import csv
from pubsub import pub


class Signals(QObject):
    trigger = Signal(tuple)
    barTrigger = Signal(int)
    lcdTrigger = Signal()
    browserReady = Signal()


class Controller():
    stopChecker = 0
    isThisFirstRun = True

    def __init__(self):
        self.view = View()
        self.view.statusbar.showMessage(">>>    Loading the browser... ")
        self.process_thread = Thread(target=self.process)
        self.driver = Driver()
        self.modelConn2 = Model()
        self.singals = Signals(None)
        self.pages = None

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
        ####################################################
        pub.subscribe(self.view.activateStartBtn, "browser is ready")
################################################################
        self.loadDataToView()   # this must come after connections made (to activate the lcd signal)




#############################################################
######### the main loop #####################################
#############################################################


    def process(self):
        model = Model()  # sqlite3 must be in same thread
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
        page_counter = 5
        for index, page in enumerate(self.pages):
            page_counter += 1
            if self.stopChecker == 1:
                break
            if model.findUrl(page) is not None:
                continue
            self.view.statusbar.showMessage(">>>    Delaying Randomly (10-25 seconds) to avoid block... ")
            sleep(random.randint(15, 25))  # to break the pattern
            if self.stopChecker == 0:
                self.view.statusbar.showMessage(">>>    Scraping the data... ")
            print("loading the page")
            if page_counter == 6:
                #----------- refreshing the browser every 5 pages to avoid (aw, snap) ----------
                win.quit()
                sleep(2)
                self.driver.open_again()
                sleep(1)
                win = self.driver.window
                page_counter = 0
                #--------------------------------------------------------------------------------

            win.get(page)
            results = win.find_elements_by_xpath(self.driver.xpaths["result"])
            print("got the result")
    # RESULT LOOP
            for result in results:
                print("now in line 88")
                if self.stopChecker == 1:
                    break
                name = self.driver.get_data(result, self.driver.xpaths["name"])
                address = self.driver.get_data(result, self.driver.xpaths["address"])
                phone = self.driver.get_data(result, self.driver.xpaths["phone"], "href").replace("tel:", "")
                sleep(random.randint(1,2))  # to break the pattern
                email = self.driver.get_data(result, self.driver.xpaths["email"], "data-email")
                website = self.driver.get_data(result, self.driver.xpaths["website"], "href")
                print("scraped the data .. now in line 96")

                # removing it to avoid a bug in the view (it shows https://...)
                if "https://" in website:
                    website = website.replace("https://", "")
                elif "http://" in website:
                    website = website.replace("http://", "")
                model.addTodata((name, address, phone, email, website, page))          ## ---> Model
                self.singals.trigger.emit((name, address, phone, email, website))           ## ---> TableWidget
                self.singals.lcdTrigger.emit()                      #---> LCDCounter
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