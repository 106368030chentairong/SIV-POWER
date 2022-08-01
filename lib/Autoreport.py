from calendar import c
import os, sys, time
from openpyxl import load_workbook
from docxtpl import DocxTemplate , InlineImage, RichText
from docx.shared import Mm
import string
from PIL import Image
import pythoncom

import tkinter as tk
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

class Autoreport_Runthread(QtCore.QThread):
    _signal = pyqtSignal(str)
    _logtext = pyqtSignal(str)
    _progressBar = pyqtSignal(str)
    def __init__(self):
        super(Autoreport_Runthread, self).__init__()
        self.timestamp = None

        self.Templatepath = None
        self.testplan_path = None

        self.context = {}
        self.doc = None

    def __del__(self):
        self.wait()
    
    def EXCEL2WORD(self, sheetname):

        wb_data = load_workbook("./Measurement data/"+self.timestamp+'/testingdata_'+self.timestamp+'.xlsx', data_only=True)
        sheet_data = wb_data[sheetname]
        wb_data.close()

        for Tag in self.doc.get_undeclared_template_variables():
            if Tag.split('_')[0] == "CL":
                cell_value = sheet_data[Tag.split('_')[-1]].internal_value
                if cell_value == 'None':
                    cell_value = ""
                self.context.setdefault(Tag ,cell_value)
            '''
            if Tag.split('_')[0] == "JG":
                try:
                    cell_value = sheet_data[Tag.split('_')[-1]].internal_value 
                    print(cell_value) 
                    if cell_value != 'None':
                        if cell_value.lower() == "fail":
                            self.context.setdefault(Tag ,RichText(cell_value, color='FF0000', bold=True))
                        else:
                            self.context.setdefault(Tag ,RichText(cell_value, color='008000', bold=True))
                except Exception:
                    continue
            '''
        self.doc.render(self.context)

        print("Report Path : ./"+self.format_save_name(sheet_data))
        #print(sheet_data)
        self.doc.save("./Measurement data/"+self.timestamp+"/"+self.format_save_name(sheet_data))     
    
    def IMG2WORD(self):
        tmp = []
        image_counter = 0
        for index_dir, (dirPath, dirNames, fileNames) in enumerate(os.walk("./Measurement data/"+self.timestamp+"/")):
            #if dirNames != []:
            #    for index, f in enumerate(fileNames):
            #        print((dirPath, dirNames, fileNames))
            #        tmp.append({'image': InlineImage(self.doc, os.path.join(dirPath, f),width=Mm(int(80)))})
            #    self.context.setdefault(os.path.split(dirPath)[-1], tmp)
            #    tmp = []
            #else:
            for Tag in self.doc.get_undeclared_template_variables():
                if Tag.split('_')[0] == "image":
                    try:
                        f = fileNames[int(Tag.split('_')[-1])]
                        if f.split(".")[-1] == "png":
                            self.context.setdefault(Tag, InlineImage(self.doc, os.path.join(dirPath, f),width=Mm(int(80))))
                    except Exception:
                        continue
                    
    def format_save_name(self, sheetdata):
        namelist = []
        local_time = time.localtime()
        timeString = time.strftime("%Y%m%d%H%M%S", local_time)
        #print(timeString)

        with open("savename_format.txt") as file:
            lines = file.readlines()
            for line in lines:
                if len(line.rstrip().split(",")) >= 2:
                    A = sheetdata[line.rstrip().split(",")[0]].internal_value
                    B = sheetdata[line.rstrip().split(",")[1]].internal_value
                    namelist.append(str(A) + "(" + str(B) + ")" )
                else:
                    A = str(sheetdata[line.rstrip()].internal_value)
                    if A != None:
                        namelist.append(A)
                    else:
                        namelist.append("None")
        
        savename = "_".join(namelist)
        for char in "<>:/\|?*\n":
            savename = savename.replace(char,'')

        savename = savename +"_"+str(timeString)+".docx"

        return savename

    def run(self):
        self.context = {}
        self.doc = DocxTemplate(self.Templatepath)
        print("Autoreport Runing ...")
        self.IMG2WORD()
        self.EXCEL2WORD("Testing")
    
    def stop(self):
        time.sleep(1)
        self._isRunning = False

        
               