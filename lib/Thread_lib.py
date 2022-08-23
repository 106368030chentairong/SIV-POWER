import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

import logging

#from lib.tektronix_4000 import DPO4000_visa
from lib.Auto_trig import Auto_trig
from lib.Auto_dc_loading import Auto_dc_loding
from lib.get_measure_data import get_measure_data
from lib.Autoreport import Autoreport_Runthread
from lib.get_device_info import get_info

class Runthread(QtCore.QThread):
    _testype = pyqtSignal(str)
    _stop_signal = pyqtSignal()
    _respones = pyqtSignal(list)
    _device_info = pyqtSignal(list)
    def __init__(self):
        super(Runthread, self).__init__()
        self.timestamp = None
        self.temperature_index = None

        self.TK_VISA_ADDRESS = None
        self.PW_VISA_ADDRESS = None
        self.LD_VISA_ADDRESS = None

        self.testype = None
        self.excel_data = None
        self.test_item = {"Regulation":"1", "Load":"2","Line":"3","Eff":"4"}

        # Spec
        self.Voltage_1 = None
        self.Voltage_2 = None
        self.Imax = None

        self.VMax_Up = None
        self.VMax_Low = None
        self.VMin_Up = None
        self.VMin_Low = None
        self.VRMS_Up = None
        self.VRMS_Low = None
        self.VP2P_Up = None
        self.VP2P_Low = None

        self.CurrDynH = None
        self.CurrDynL = None

        self.image_index = None

    def run(self):
        try:
            get_info_obj = get_info()
            get_info_obj.TK_VISA_ADDRESS = self.TK_VISA_ADDRESS
            get_info_obj.PW_VISA_ADDRESS = self.PW_VISA_ADDRESS
            get_info_obj.LD_VISA_ADDRESS = self.LD_VISA_ADDRESS
            info_data = get_info_obj.run()

            self._device_info.emit(info_data)
        except Exception as e:
            print(e)
            logging.error(e)
        
        # Runing to the table row data
        for index, row in enumerate(self.excel_data):
            # Start in to 2 num row 
            if index >= 2 :
                try:
                    self.image_index = str(index-1)
                    self.setup_rel(row)
                    result = self.auto_control(self.testype)
                    self._respones.emit([index,result])
                except Exception as e:
                    print(e)
                    logging.error(e)

                #result = ["5", "5", "5","5"] #test
                #if self.testype != "Eff":
                #    judge = self.judge(result)
                #    result.append(judge)
                #time.sleep(1)  #test

        time.sleep(5)
        self._stop_signal.emit()
    
    def auto_control(self, testype):
        logging.info("-"*20 + (testype) + "-"*20 )
        if testype == "Regulation" or testype == "Load":
            # Auto setup power & loading
            load_scope = Auto_dc_loding()
            load_scope.PW_VISA_ADDRESS = self.PW_VISA_ADDRESS
            load_scope.LD_VISA_ADDRESS = self.LD_VISA_ADDRESS
            load_scope.Voltage   = self.Voltage_1
            load_scope.Imax      = self.Imax
            load_scope.CurrDynH  = self.CurrDynH
            load_scope.CurrDynL  = self.CurrDynL
            load_scope.start(testype)

            # Auto trig
            auto_scope = Auto_trig()
            auto_scope.VISA_ADDRESS = self.TK_VISA_ADDRESS
            auto_scope.start(testype)

            # set up measure items & get values
            measure_scope = get_measure_data()
            measure_scope.VISA_ADDRESS = self.TK_VISA_ADDRESS
            measure_scope.add_measurement()
            result_list = measure_scope.get_value()

        elif testype == "Line" :
            auto_scope = Auto_trig()
            auto_scope.VISA_ADDRESS = self.TK_VISA_ADDRESS
            auto_scope.start("Line")

            load_scope = Auto_dc_loding()
            load_scope.PW_VISA_ADDRESS = self.PW_VISA_ADDRESS
            load_scope.LD_VISA_ADDRESS = self.LD_VISA_ADDRESS

            # setup Hight level
            load_scope.PW_setup(self.Voltage_1)
            time.sleep(2)

            # Setup loading Curr
            load_scope.CurrDynH  = self.CurrDynH
            load_scope.LD_setup(0)

            if float(self.Voltage_1) > float(self.Voltage_2) :
                SLOpe = "FALL"
            else:
                SLOpe = "RISe"
            trig_votage = ((float(self.Voltage_1) - float(self.Voltage_2))/2 ) + float(self.Voltage_2)
            
            #trig_votage = str(trigger_level)

            # Setup Trig level
            time.sleep(2)
            logging.info(SLOpe)
            logging.info("trig votage :"+ str(trig_votage))
            auto_scope.setup_trig(str(trig_votage) , SLOpe) #  {RISe|FALL}

            # setup Low level
            time.sleep(2)
            load_scope.PW_setup(self.Voltage_2)

            # set up measure items & get values
            measure_scope = get_measure_data()
            measure_scope.VISA_ADDRESS = self.TK_VISA_ADDRESS
            measure_scope.add_measurement()
            result_list = measure_scope.get_value()
            time.sleep(2)

        elif testype == "Eff" :
            # Auto trig
            auto_scope = Auto_trig()
            auto_scope.VISA_ADDRESS = self.TK_VISA_ADDRESS
            auto_scope.start("Line")

            load_scope = Auto_dc_loding()
            load_scope.PW_VISA_ADDRESS = self.PW_VISA_ADDRESS
            load_scope.LD_VISA_ADDRESS = self.LD_VISA_ADDRESS

            # setup Hight level
            load_scope.PW_setup(self.Voltage_1)
            time.sleep(2)

            # Setup loading Curr
            load_scope.CurrDynH  = self.CurrDynH
            load_scope.LD_setup(0)

            time.sleep(2)
            result_list = load_scope.get_Eff()

        if self.testype != "Eff":
            judge = self.judge(result_list)
            result_list.append(judge)
            auto_scope.get_IMAGe("./Measurement data/"+self.timestamp+"/"+ self.test_item[testype] +"_"+ str(self.temperature_index) +"_"+ self.image_index )
            logging.info("./Measurement data/"+self.timestamp+"/"+ self.test_item[testype] +"_"+ str(self.temperature_index) +"_"+ self.image_index )
        return result_list

    def setup_rel(self, rowdata):
        if self.testype == "Regulation":
            self.Voltage_1  = rowdata[2]
            self.Imax       = rowdata[3]

            self.VMax_Up    = rowdata[4]
            self.VMax_Low   = rowdata[5]
            self.VMin_Up    = rowdata[6]
            self.VMin_Low   = rowdata[7]
            self.VRMS_Up    = rowdata[8]
            self.VRMS_Low   = rowdata[9]
            self.VP2P_Up    = rowdata[10]
            self.VP2P_Low   = rowdata[11]

            self.CurrDynH   = rowdata[12]
            self.CurrDynL   = rowdata[13]

        elif self.testype == "Load":
            self.Voltage_1  = rowdata[2]
            self.Imax       = rowdata[3]

            self.VMax_Up    = rowdata[4]
            self.VMax_Low   = rowdata[5]
            self.VMin_Up    = rowdata[6]
            self.VMin_Low   = rowdata[7]

            self.CurrDynH   = rowdata[8]
            self.CurrDynL   = rowdata[9]
        
        elif self.testype == "Line":
            self.Voltage_1  = rowdata[2]
            self.Voltage_2  = rowdata[3]
            self.Imax       = rowdata[4]

            self.VMax_Up    = rowdata[5]
            self.VMax_Low   = rowdata[6]
            self.VMin_Up    = rowdata[7]
            self.VMin_Low   = rowdata[8]

            self.CurrDynH   = rowdata[9]
            self.CurrDynL   = rowdata[10]
        
        elif self.testype == "Eff":
            self.Voltage_1  = rowdata[2]
            self.Imax       = rowdata[3]

            self.CurrDynH   = rowdata[4]
            self.CurrDynL   = rowdata[5]

    def judge(self, result_list ):
        Max_value = result_list[0]
        Min_value = result_list[1]
        RMS_value = result_list[2]
        PK2PK_value = result_list[3]

        Judge_num = 0
        if self.VMax_Up != self.VMax_Low:
            if float(Max_value) > float(self.VMax_Up):
                Judge_num += 1
            if float(Max_value) < float(self.VMax_Low):
                Judge_num += 1    
        
        if self.VMin_Up != self.VMin_Low:
            if float(Min_value) > float(self.VMin_Up):
                Judge_num += 1
            if float(Min_value) < float(self.VMin_Low):
                Judge_num += 1    

        if self.VRMS_Up != self.VRMS_Low:
            if float(RMS_value) > float(self.VRMS_Up):
                Judge_num += 1
            if float(RMS_value) < float(self.VRMS_Low):
                Judge_num += 1
    
        if self.VP2P_Up != self.VP2P_Low:
            if float(PK2PK_value) > float(self.VP2P_Up):
                Judge_num += 1
            if float(PK2PK_value) < float(self.VP2P_Low):
                Judge_num += 1
        
        if Judge_num > 0:
            return "FALL"
        else:
            return "PASS"    


    def stop(self):
        time.sleep(1)
        self._isRunning = False