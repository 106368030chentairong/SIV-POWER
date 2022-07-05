import os, sys, time
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import logging
from colorama import Fore, Back, Style

import pyvisa as visa
from openpyxl import load_workbook, Workbook

# UI/UX 
from untitled import *

# import from lib 
from lib.logcolors import bcolors

class mainProgram(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(mainProgram, self).__init__(parent)
        self.setupUi(self)

        self.wb = None

        self.continue_single = 0

        self.pushButton_testplan.clicked.connect(self.open_testplan)
        self.pushButton_template.clicked.connect(self.open_template)

        # VISA ADDRESS REFRESH FUNCTION
        self.Refresh_VISA()
        self.pushButton_refresh.clicked.connect(self.Refresh_VISA)

        self.excel_data = []
    
    def w2table(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(self.excel_data))
        self.tableWidget.setColumnCount(len(self.excel_data[0]))

        for i, row in enumerate(self.excel_data):
            if i == 0:
                self.tableWidget.setHorizontalHeaderLabels(row)
            else:
                for j, col in enumerate(row):
                    if j == 0 :
                        chkBoxItem = QTableWidgetItem(str(col))
                        chkBoxItem.setText(str(col))
                        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
                        self.tableWidget.setItem(i-1, j, chkBoxItem)
                    else:    
                        item = QTableWidgetItem(str(col))
                        self.tableWidget.setItem(i-1, j, item)
    
    def load_excel(self):
        sheet = self.wb[self.comboBox_sheet.currentText()]
        self.excel_data = []
        self.tmp = []
        try:
            for row in sheet.values:
                try:
                    self.tmp.append(row)
                    self.excel_data.append(row)
                except Exception:
                    continue
            try:
                self.w2table()
                #self.w2measure()
            except Exception as e: 
                print(e)
                logging.error("w2table error!")
        except Exception as e:
            logging.error("Loading Excel sheet Error !" , e)
    
    def read_sheetnames(self, CSV_path):
        self.wb =  load_workbook(CSV_path)
        sheetnames = self.wb.sheetnames
        return sheetnames

    def set_comboBox_sheet(self, sheet_list):
        self.comboBox_sheet.clear()
        self.comboBox_sheet.addItems(sheet_list)
    
    def open_testplan(self):
        try:
            filename, filetype = QFileDialog.getOpenFileName(self, "Open file", "./", "Excel (*.xlsx *.xls)")
            if filename != "":
                self.lineEdit_testplan.setText(filename)
                #self.settings.setValue('SETUP/TESTPLAN_PATH', filename) 
                sheetnames = self.read_sheetnames(self.lineEdit_testplan.text())
                self.set_comboBox_sheet(sheetnames)
                self.load_excel()
        except Exception as e:
            logging.error(e)
            logging.error("Open Excel File Error ! ")
    
    def open_template(self):
        try:
            filename, filetype = QFileDialog.getOpenFileName(self, "Open file", "./", "Word (*.docx)")
            if filename != "":
                self.lineEdit_template.setText(filename)
        except Exception as e:
            print(e)
            logging.error("Open Word File Error ! ")

    def getusblist(self):
        try:
            rm = visa.ResourceManager()
            self.usb_list = rm.list_resources()
            rm.close
        except Exception:
            self.usb_list = []

    def Refresh_VISA(self):
        self.getusblist()
        self.comboBox_visa.clear()
        logging.info(self.usb_list)
        try:
            if len(self.usb_list) != 0:
                self.comboBox_visa.addItems(self.usb_list)
            else:
                self.comboBox_visa.addItems("")
        except Exception as e:
            self.comboBox_visa.addItems("")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    AutoRepor = mainProgram()
    AutoRepor.show()
    sys.exit(app.exec_())