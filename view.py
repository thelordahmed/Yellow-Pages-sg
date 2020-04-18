from PySide2.QtWidgets import *
from PySide2.QtGui import *
from resources.design import Ui_MainWindow as design
import os


# Import your design to the class

class View(QMainWindow, design):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.setupUi(self)
        self.show()
        self.start_btn.setDisabled(True)  # to avoid clicking before browser loads





    # Customizing the close event
    def closeEvent(self, event: QCloseEvent):
        os.system("taskkill /t /F /im chromedriver.exe")

    def addToTableWidget(self, data):  # slot >> trigger singal
        row_pos = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_pos)

        for index, info in enumerate(data):
            self.tableWidget.setItem(row_pos, index, QTableWidgetItem(info))
            self.tableWidget.scrollToBottom()

    def barIncreament(self, value):  # slot >> barTrigger signal
        self.progressBar.setValue(value)

    def lcdCounter(self):
        self.counter.display(self.tableWidget.rowCount())

    def message(self, title, text, mode="question"):
        if mode == "warning":
            re = QMessageBox.warning(self,title,text,QMessageBox.Yes | QMessageBox.No)
        else:
            re = QMessageBox.question(self,title,text,QMessageBox.Yes | QMessageBox.No)
        if re == QMessageBox.Yes:
            return True
        else:
            return False

    def activateStartBtn(self):
        print("activated")
        self.start_btn.setEnabled(True)
        self.statusbar.showMessage(">>>     Ready!")

    def saveDialog(self):
        """:return saving path"""
        path = QFileDialog.getSaveFileName(self, "save data", "data", "*.csv")
        return path[0]
