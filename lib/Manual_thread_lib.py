import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

import logging

from lib.get_device_info import get_info
from lib.tektronix_4000 import DPO4000_visa

class Manual_Runthread(QtCore.QThread):
    _device_info = pyqtSignal(list)
    _CH_label = pyqtSignal(list)

    def __init__(self):
        super(Manual_Runthread, self).__init__()
        self.switch = None
        self.TK_VISA_ADDRESS = None
        self.PW_VISA_ADDRESS = None
        self.LD_VISA_ADDRESS = None

        self.CH1 = ""
        self.CH2 = ""
        self.CH3 = ""
        self.CH4 = ""

        self.label_tmp = []

    def run(self):
        if self.switch == "1":
            try:
                get_info_obj = get_info()
                get_info_obj.TK_VISA_ADDRESS = self.TK_VISA_ADDRESS
                get_info_obj.PW_VISA_ADDRESS = self.PW_VISA_ADDRESS
                get_info_obj.LD_VISA_ADDRESS = self.LD_VISA_ADDRESS
                info_data = get_info_obj.run()

                self._device_info.emit(info_data)
            except Exception:
                print("get_info ERROR")
        elif self.switch == "2":
            self.read_label()
        elif self.switch == "3":
            self.write_label()

    def read_label(self):
        if self.TK_VISA_ADDRESS != None:
            try:
                self.scope_TK = DPO4000_visa()
                self.scope_TK.VISA_ADDRESS = self.TK_VISA_ADDRESS
                self.scope_TK.GLOBAL_TOUT = 1000
                self.scope_TK.connect()

                self.CH1 = self.scope_TK.do_query("CH1:LABel?")
                self.CH2 = self.scope_TK.do_query("CH2:LABel?")
                self.CH3 = self.scope_TK.do_query("CH3:LABel?")
                self.CH4 = self.scope_TK.do_query("CH4:LABel?")
                self.scope_TK.close()
            except Exception as e :
                print(e)
                self.scope_TK.close()
                pass
            
            self._CH_label.emit([self.CH1,self.CH2,self.CH3,self.CH4])

    def write_label(self):
        if self.TK_VISA_ADDRESS != None:
            try:
                logging.info(self.label_tmp)
                self.TK_VISA_ADDRESS
                self.scope_TK = DPO4000_visa()
                self.scope_TK.VISA_ADDRESS = self.TK_VISA_ADDRESS
                self.scope_TK.GLOBAL_TOUT = 1000
                self.scope_TK.connect()

                self.scope_TK.do_command("CH1:LABel "+ str(self.label_tmp[0]))
                self.scope_TK.do_command("CH2:LABel "+ str(self.label_tmp[1]))
                self.scope_TK.do_command("CH3:LABel "+ str(self.label_tmp[2]))
                self.scope_TK.do_command("CH4:LABel "+ str(self.label_tmp[3]))
                self.scope_TK.close()
            except Exception as e:
                print(e)
                self.scope_TK.close()
                pass

    def stop(self):
        time.sleep(1)
        self._isRunning = False