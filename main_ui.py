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
from lib.Thread_lib import Runthread
from lib.Autoreport import Autoreport_Runthread

class mainProgram(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(mainProgram, self).__init__(parent)
        self.setupUi(self)
        self.timestamp = None

        self.wb = None
        self.continue_single = 0

        self.test_item = ["Regulation", "Load","Line","Eff",]
        self.switch_index = 0

        # Push Button
        # VISA ADDRESS REFRESH FUNCTION
        self.Refresh_VISA(self.comboBox_TK_visa)
        self.Refresh_VISA(self.comboBox_PS_visa)
        self.Refresh_VISA(self.comboBox_EL_visa)

        self.pushButton_TK_visa.clicked.connect(self.setup_TK_addres)
        self.pushButton_PS_visa.clicked.connect(self.setup_PS_addres)
        self.pushButton_EL_visa.clicked.connect(self.setup_EL_addres)

        self.pushButton_testplan.clicked.connect(self.open_testplan)
        self.pushButton_template.clicked.connect(self.open_template)

        self.pushButton_RUN.clicked.connect(self.btn_run)
        #self.pushButton_Cancel.clicked.connect(self.close)

        self.excel_data = []
    
    def check_folder(self):
        if not os.path.isfile("./Measurement data/"+self.timestamp):
            os.mkdir( "./Measurement data/"+self.timestamp)
    
    def setup_timestamp(self):
        nowTime = int(time.time())
        struct_time = time.localtime(nowTime)
        self.timestamp = str(time.strftime("%Y%m%d%H%M%S", struct_time))

    def btn_run(self):
        self.setup_timestamp()
        self.check_folder()
        self.switch_index = 0
        self.load_excel(self.test_item[0])

        self.autotest()
    
    def autotest(self):
        self.thread = Runthread()
        self.thread.testype = self.test_item[self.switch_index]
        self.thread.TK_VISA_ADDRESS = self.comboBox_TK_visa.currentText()
        self.thread.PW_VISA_ADDRESS = self.comboBox_PS_visa.currentText()
        self.thread.LD_VISA_ADDRESS = self.comboBox_EL_visa.currentText()
        self.thread.excel_data = self.excel_data
        self.thread.timestamp = self.timestamp
        self.thread._respones.connect(self.respones2table)
        self.thread._stop_signal.connect(self.switch_table)
        self.thread.start()
    
    def table2excel(self):
        if self.switch_index == 0:
            wb_data = load_workbook(self.lineEdit_testplan.text(), data_only=True)
            basicsheet = wb_data.copy_worksheet(wb_data["Basic"])
            basicsheet.title = "Testing"
        elif self.switch_index > 0:
            wb_data = load_workbook("Measurement data/"+self.timestamp+"/testingdata_"+self.timestamp+".xlsx", data_only=True)
            basicsheet = wb_data["Testing"]

        index_dic = {"Regulation": 4 , "Load": 24, "Line":40, "Eff":57}
        sheet_con = 0
        type_name = self.test_item[self.switch_index]
        print(index_dic[type_name] , type_name)
        col = self.tableWidget_testplan.columnCount()
        row = self.tableWidget_testplan.rowCount()

        print(col,row)
        
        for row_index in range(row):
            sheet_con += 1
            #print(sheet_con)
            logging.debug(str(self.tableWidget_testplan.item(row_index, 0).text()))
            for col_index in range(col):
                teext = str(self.tableWidget_testplan.item(row_index, col_index).text())
                basicsheet.cell(row=sheet_con+2, column=col_index+index_dic[type_name]).value = teext
     
        wb_data.save("Measurement data/"+self.timestamp+"/testingdata_"+self.timestamp+".xlsx")

    def rum_autoreport(self):
        try: 
            self.thread_autoreport = Autoreport_Runthread()
            self.thread_autoreport.timestamp = self.timestamp
            self.thread_autoreport.Templatepath = self.lineEdit_template.text()
            self.thread_autoreport.testplan_path = self.lineEdit_testplan.text()
            self.thread_autoreport.start()
        except Exception as e:
            logging.error(e)

    def switch_table(self):
        self.table2excel()
        self.switch_index += 1
        if self.switch_index < len(self.test_item):
            self.load_excel(self.test_item[self.switch_index])
            self.autotest()
        if self.switch_index == len(self.test_item) :
            self.rum_autoreport()

    def w2table(self):
        self.tableWidget_testplan.clearContents()
        self.tableWidget_testplan.setRowCount(len(self.excel_data)-1)
        self.tableWidget_testplan.setColumnCount(len(self.excel_data[0]))

        for i, row in enumerate(self.excel_data):
            if i == 0:
                self.tableWidget_testplan.setHorizontalHeaderLabels(row)
            else:
                for j, col in enumerate(row):
                    if str(col) == "None":
                        col = ""
                    if j == 0 :
                        chkBoxItem = QTableWidgetItem(str(col))
                        chkBoxItem.setText(str(col))
                        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
                        self.tableWidget_testplan.setItem(i-1, j, chkBoxItem)
                    else:    
                        item = QTableWidgetItem(str(col))
                        self.tableWidget_testplan.setItem(i-1, j, item)
    
    def load_excel(self, sheet_name):
        sheet = self.wb[sheet_name]
        self.excel_data = []
        try:
            for row in sheet.values:
                try:
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

    def set_comboBox_sheet(self, combobox, sheet_list):
        combobox.clear()
        combobox.addItems(sheet_list)
    
    def open_testplan(self):
        try:
            filename, filetype = QFileDialog.getOpenFileName(self, "Open file", "./", "Excel (*.xlsx *.xls)")
            if filename != "":
                self.lineEdit_testplan.setText(filename)
                #self.settings.setValue('SETUP/TESTPLAN_PATH', filename) 
                sheetnames = self.read_sheetnames(self.lineEdit_testplan.text())
                self.set_comboBox_sheet(self.comboBox_testplan, sheetnames)
                self.switch_index = 0
                print(self.test_item[0])
                self.load_excel(self.test_item[0])

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
            usb_list = rm.list_resources()
            rm.close
        except Exception:
            usb_list = []
        
        return usb_list
    
    def setup_TK_addres(self):
       self.Refresh_VISA(self.comboBox_TK_visa)
    def setup_PS_addres(self):
        self.Refresh_VISA(self.comboBox_PS_visa)
    def setup_EL_addres(self):
        self.Refresh_VISA(self.comboBox_EL_visa)

    def Refresh_VISA(self, combobox_obj ):
        usb_list = self.getusblist()
        combobox_obj.clear()
        logging.info(usb_list)
        try:
            if len(usb_list) != 0:
                combobox_obj.addItems(usb_list)
            else:
                combobox_obj.addItems("")
        except Exception as e:
            combobox_obj.addItems("")
    
    def respones2table(self, msg):
        print(msg)
        index_dic = {"Line":11,"Regulation": 14 , "Load": 10,  "Eff":6}
        index_shift = index_dic[self.test_item[self.switch_index]]

        for index, col in enumerate(msg[1]):
            item = QTableWidgetItem(str(col))
            self.tableWidget_testplan.setItem(msg[0]-1, index+index_shift , item)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    AutoRepor = mainProgram()
    AutoRepor.show()
    sys.exit(app.exec_())