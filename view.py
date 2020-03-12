from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from resources.design import Ui_MainWindow


class View(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.setupUi(self)
        self.show()

    def addToTableWidget(self, data):  # slot >> trigger singal
        row_pos = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_pos)

        for index, info in enumerate(data):
            self.tableWidget.setItem(row_pos, index, QTableWidgetItem(info))

    def barIncreament(self, value):  # slot >> barTrigger signal
        self.progressBar.setValue(value)

    def lcdCounter(self):
        self.counter.display(self.tableWidget.rowCount())