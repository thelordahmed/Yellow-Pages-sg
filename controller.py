from view import View
from model import Model
from PySide2.QtWidgets import *
from pubsub.pub import subscribe
from threading import Thread
from driver import Driver


class Controller:
    def __init__(self):
        self.driver_thread = Thread(target=self.start_driver).start()  # a thread for the driver to open the browser at the same time with bot
        self.model = None
        self.view = View()
        self.driver = None
        self.process_thread = Thread(target=self.process)

        # listening to start button event from the view
        subscribe(self.start_process, "start loop")




    def start_driver(self):
        win = Driver()
        self.driver = win

    def start_process(self):
        self.process_thread.start()

    #############################################################
    ######### the main loop #####################################
    #############################################################

    def process(self):
        self.model = Model()  # sqlite3 must be in same thread
        win = self.driver.window
        pages = self.driver.pages_links()

        for page in pages:
            # sleep(random.randint(5,10))  # to break the pattern
            win.get(page)
            results = win.find_elements_by_xpath(self.driver.xpaths["result"])
            for result in results:
                name = self.driver.get_data(result, self.driver.xpaths["name"])
                address = self.driver.get_data(result, self.driver.xpaths["address"])
                phone = self.driver.get_data(result, self.driver.xpaths["phone"], "href").replace("tel:", "")
                email = self.driver.get_data(result, self.driver.xpaths["email"], "data-email")
                website = self.driver.get_data(result, self.driver.xpaths["website"], "href")
                self.model.addTodata((name, address, phone, email, website))                ## ---> Model
                self.view.addToTableWidget((name, address, phone, email, website))





if __name__ == "__main__":
    app = QApplication()
    controller = Controller()
    app.exec_()