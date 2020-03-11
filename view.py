from PySide2.QtWidgets import *
from PySide2.QtGui import *
from resources.design import Ui_MainWindow
from pubsub.pub import sendMessage


class View(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        self.setupUi(self)
        self.show()

        ##############################
        ###### buttons Events ########
        ##############################
        self.start_btn.clicked.connect(self.start_func)
        self.stop_btn.clicked.connect(self.stop_func)
        self.clear_btn.clicked.connect(self.clear_func)
        self.save_btn.clicked.connect(self.export_func)



###########################################################
    #       buttons functions         #
    ###################################
    def start_func(self):
        sendMessage("start loop")
        self.stop_btn.setEnabled(True)
        self.start_btn.setDisabled(True)

    def stop_func(self):
        pass

    def clear_func(self):
        pass

    def export_func(self):
        pass


###############################################
###### add data to tableWidget ####

    def addToTableWidget(self, data):
        row_pos = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_pos)

        for index, info in enumerate(data):
            self.tableWidget.setItem(row_pos, index, QTableWidgetItem(info))