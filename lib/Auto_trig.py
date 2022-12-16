from cmath import log
import logging
import time
import numpy as np
from struct import unpack

from PyQt5 import QtCore

import matplotlib.pyplot as plt

import calendar

from lib.tektronix_4000 import DPO4000_visa
from lib.Auto_FFT import Auto_FFT

class Auto_trig():
    def __init__(self):
        self.config = None
        self.VISA_ADDRESS = None
        self.scope = None
        #self.record_length = None
        self.normal_scale = "1E-3"
        self.trig_level = 0
        self.pk2pk = 0
        self.stack_p2p = []
        self.frequency = 0
        self.check_frq_num = 0
        self.check_trig_num = 0

        self.input_Voltage = 5
        self.Output_Voltage = 20

        self.display_wavform = 99
        self.display_graticule = 99

        self.lineEdit_scale_period = None
        self.Default_scale = None
        self.FFT_image_path = None

    def check_stack_dif(self):
        max_index = 0
        mini_index = 0
        for index, p2p_valu in enumerate(self.stack_p2p):
            if p2p_valu > self.stack_p2p[max_index]: 
                max_index == index
            elif p2p_valu < self.stack_p2p[mini_index]:
                mini_index == index
        if abs((mini_index/max_index)-1) >= 0.2:
            return abs((mini_index/max_index)-1)
        else:
            return 0
    
    def check_single_state(self):
        self.check_trig_num += 1
        state = self.scope.do_query('ACQUIRE:STATE?')
        #print(state)
        if state == '1':
            if self.check_trig_num >= 20:
                time.sleep(1)
                self.scope.do_command('FPAnel:PRESS FORCetrig')
                time.sleep(1)
                self.check_single_state()

            time.sleep(0.1)
            self.check_single_state()
        elif state == '0':
            time.sleep(1)
            return "STOP"
    
    def setup(self, record_length):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()
        #self.scope.do_command('FPAnel:PRESS DEFaultsetup')
        self.scope.do_command('FPAnel:PRESS DEFaultsetup')
        self.scope.do_command('FPAnel:PRESS MENUOff')
        self.scope.do_command('DISplay:INTENSITy:WAVEform '+str(self.display_wavform))
        self.scope.do_command('DISplay:INTENSITy:GRAticule '+str(self.display_graticule))
        self.scope.do_command('HORizontal:RECOrdlength '+ str(record_length))
        self.scope.do_command('FPAnel:PRESS MENUOff')
        self.scope.do_command('SELECT:CH1 ON')
        self.scope.do_command('SELECT:CH2 ON')
        self.scope.do_command('SELECT:CH3 ON')
        self.scope.do_command('SELECT:CH3 ON')
        self.scope.do_command('HORizontal:SAMPLERate 100e6')
        self.scope.do_command('HORIZONTAL:SCALE ' + self.normal_scale)
        #Default settings for CH
        self.scope.do_command('CH1:POSition -2') #Default position is CH1
        self.scope.do_command('CH3:POSition -2') #Default position is CH3
        self.scope.do_command('CH1:OFFSet 0') #Default offset is CH1
        self.scope.do_command('CH1:SCAle 2') #Default value for voltage
        self.scope.do_command('CH3:SCALe 1') #Default value for current
        self.scope.do_command('CH3:PRObe:FORCEDRange 5')
        
        self.scope.close()

    def set_scale(self, scale):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()
        self.scope.do_command('HORIZONTAL:SCALE '+str(scale))
        self.scope.do_command('acquire:state ON')
        self.check_trig_num = 0
        self.check_single_state() # check while loop
        self.scope.close()

    def set_measurement(self):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()

        channel_list = [1,1,1,1,1,1]
        MEASUrement_Type = ["MAXimum","MINImum","MAXimum","MINImum","FREQuency","pk2pk"]

        for i in range(8):
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':STATE OFF')
        for i in range(len(MEASUrement_Type)):
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':SOURCE1 CH'+str(channel_list[i]))
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':TYPe '+ MEASUrement_Type[i])
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':STATE ON')
        time.sleep(3)
        self.Output_Voltage = float(self.scope.do_query('MEASUrement:MEAS1:VALue?'))

        self.scope.close()

    def get_IMAGe(self, save_path):
        try:
            self.scope = DPO4000_visa()
            self.scope.VISA_ADDRESS = self.VISA_ADDRESS
            self.scope.connect()

            self.scope.do_command("SAVe:IMAGe:FILEF PNG")
            self.scope.do_command("HARDCopy STARt")
            imgData = self.scope.read_raw()

            imgFile = open(save_path+".png", "wb")
            imgFile.write(imgData)
            imgFile.close()
        except Exception as e:
            imgFile = open(save_path+".png", "w")
            imgFile.close()
        self.scope.close()

    def get_frequency(self):
        self.check_frq_num += 1 
        frequency = float(self.scope.do_query('MEASUrement:MEAS5:VALue?'))
        #print(frequency)
        if self.check_frq_num <20:
            if frequency >= float("9.91e+36"):
                time.sleep(0.1)
                return self.get_frequency()
            else:
                return frequency
        return None
    
    '''def auto_getdef_vale(self):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()

        self.scope.close()'''

    def Auto_cale(self, channel, div_num):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()

        self.scope.do_command('SELECT:CH1 ON')
        self.scope.do_command('SELECT:CH2 ON')
        self.scope.do_command('SELECT:CH3 ON')
        self.scope.do_command('SELECT:CH3 ON')

        channel_list = [channel,channel,channel,channel]
        MEASUrement_Type = ["MAXimum","MINImum","MEAN","pk2pk"]

        for i in range(len(MEASUrement_Type)):
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':SOURCE1 CH'+str(channel_list[i]))
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':TYPe '+ MEASUrement_Type[i])
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':STATE ON')

        for index in range(3):
            print("{}{}{}".format("-"*50,index,"-"*50))
            time.sleep(0.1)
            self.scope.do_command('ACQuire:STOPAfter SEQuence')
            self.scope.do_command('acquire:state ON')
            self.check_trig_num = 0
            self.check_single_state()
            
            CH1_MAX_VALue = float(self.scope.do_query('MEASUrement:MEAS1:VALue?'))
            CH1_MINI_VALue = float(self.scope.do_query('MEASUrement:MEAS2:VALue?'))
            CH1_MEAN_VALue = float(self.scope.do_query('MEASUrement:MEAS3:VALue?'))
            CH1_AMPlitude_VALue = float(self.scope.do_query('MEASUrement:MEAS4:VALue?'))
            offset_value = ((CH1_MAX_VALue-CH1_MINI_VALue)/2)+CH1_MINI_VALue
            Scale_value = CH1_AMPlitude_VALue/div_num
            print(Scale_value)
            #self.scope.do_command('CH%s:BANdwidth 20E+6' %(channel))
            self.scope.do_command('CH%s:OFFSet %s' %(channel,offset_value))
            self.scope.do_command('CH%s:SCAle %s' %(channel,Scale_value))

            print("OffSet：{}, Scale：{}".format(offset_value, Scale_value))

            self.scope.do_command('TRIGger:A:EDGE:SOUrce CH%s' %(channel))
            self.scope.do_command('TRIGger:A SETLevel %s' %(offset_value))
            self.scope.do_command('TRIGger:A:MODe AUTO')
        self.scope.close()
    
    def get_rawdata(self, channel, scale):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()
        
        self.scope.do_command('AUTOSet EXECute')
        time.sleep(2)
        self.scope.do_command('CH'+str(channel)+':BANdwidth 20E+6')
        self.scope.do_command('CH3:PRObe:FORCEDRange 5') # Set Channel 3 to 5A range
        ##self.scope.do_command('CH1:OFFSet 0')
        ##self.scope.do_command('CH1:SCAle 2')
        self.scope.do_command('HORIZONTAL:SCALE '+str(scale))

        self.scope.do_command('TRIGger:A:EDGE:SOUrce CH'+str(channel))
        self.scope.do_command('TRIGger:A:LEVel '+str(self.trig_level))
        self.scope.do_command('TRIGger:A:EDGE:SOUrce CH1')
        self.scope.do_command('TRIGger:A:TYPe EDGe')
        self.scope.do_command('TRIGger:A:MODe auto')
        self.scope.do_command('TRIGger:A:EDGE:SLOpe FALL')

        self.scope.do_command('DATA:SOU CH'+str(channel))
        self.scope.do_command('DATA:WIDTH 1')
        self.scope.do_command('DATA:ENC RPB')
        
        self.scope.do_command('ACQuire:STOPAfter SEQuence')
        self.scope.do_command('acquire:state ON')
        self.check_single_state() # check state off while loop

        ymult = float(self.scope.do_query('WFMPRE:YMULT?'))
        yzero = float(self.scope.do_query('WFMPRE:YZERO?'))
        yoff = float(self.scope.do_query('WFMPRE:YOFF?'))
        xincr = float(self.scope.do_query('WFMPRE:XINCR?'))

        print("{} {} {} {}".format(ymult, yoff, xincr, yoff))
        
        self.check_frq_num = 0
        self.frequency = self.get_frequency()
        
        # Get raw data
        raw_data = self.scope.get_raw()
        headerlen = 2 + int(raw_data[1])
        header = raw_data[:headerlen]
        ADC_wave_ch1 = raw_data[headerlen:-1]
        ADC_wave_ch1 = np.array(unpack('%sB' % len(ADC_wave_ch1),ADC_wave_ch1))
        Volts = (ADC_wave_ch1 - yoff) * ymult  + yzero

        # Calculate the adjustment ratio
        max_volume = max(Volts)
        min_volume = min(Volts)
        self.trig_level = ((max_volume-min_volume)/2) +min_volume
        self.pk2pk = abs(max_volume - min_volume)
        self.pk2pk_OS = float(self.scope.do_query('MEASUrement:MEAS6:VALue?'))
        self.stack_p2p.append(abs(max_volume - min_volume))

        print("get_rawdata() function : {} {} {} {}".format(self.trig_level,self.pk2pk,self.pk2pk_OS,self.stack_p2p))
        #SCAle = self.Auto_cale(self.pk2pk/2)

        self.scope.do_command('CH1:OFFSet '+str(self.trig_level))
        self.scope.do_command('CH1:SCAle '+str(self.pk2pk/2))
        self.scope.do_command('ACQuire:STOPAfter SEQuence')
        self.scope.do_command('acquire:state ON')
        self.check_single_state() # check while loop
        self.scope.do_command('CH1:POSition 1')

        print("PK2PK : "+ str( self.pk2pk ))
        print("satck PK2PK :"+str( self.stack_p2p ))
        print("frequency : "+str(self.frequency))
        print("-"*10)
        Time = np.arange(0, xincr * len(Volts), xincr)
        
        self.scope.close()

        #self.save_np([Volts, Time])
        return Volts, Time

    def find_timedif(self, Rawdata, Time, scale):
        delta = 0.8
        #avg = 0.04
        #print((avg)*delta)
        #plt.plot(Rawdata)
        #plt.savefig('Rawdata.png')
        logging.debug(str((self.trig_level)*delta))
        tmp = []
        for index, val in enumerate(Rawdata):
            if val >= (self.trig_level)*delta:
                tmp.append([index, val])

        pk2pk_time = []
        avg_dif_time = []
        for index, val in enumerate(tmp):
            if index < len(tmp)-1:
                #print(tmp[index+1][0] - val[0])
                time_dif = Time[tmp[index+1][0] ]- Time[val[0]]
                if (abs(time_dif)) >= scale*0.02:
                    #print(time_dif)
                    pk2pk_time.append([time_dif, [val[0], val[1]], [tmp[index+1][0], tmp[index+1][1]]])
                    avg_dif_time.append(time_dif)

        if avg_dif_time != []:
            avg_time = sum(avg_dif_time)/len(avg_dif_time)
        else:
            avg_time = None
            pk2pk_time = None
        
        return pk2pk_time, avg_time

    def save_np(self, data):
        current_GMT = time.gmtime()

        # ts stores timestamp
        ts = calendar.timegm(current_GMT)
        print("Current timestamp:", ts)
        
        with open('np_tmp/'+str(ts)+'.npy', 'wb') as f:
            np.save(f, np.array(data))
    
    def cl_dif(self, pk2pk_list):
        print(pk2pk_list)
        ver_val = 0
        while pk2pk_list != [] :
            ver_val = pk2pk_list.pop()
            if pk2pk_list != []:
                print(abs(pk2pk_list[-1] - ver_val)/pk2pk_list[-1])

    def setup_trig(self, Voltage_1, Voltage_2):

        trig_votage = ((Voltage_1 - Voltage_2)/2 ) + Voltage_2
        if float(Voltage_1) > float(Voltage_2) :
            SLOpe = "FALL"
        else:
            SLOpe = "RISe"

        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()

        #self.scope.do_command('FPAnel:PRESS DEFaultsetup')
        self.scope.do_command('DISplay:INTENSITy:WAVEform '+str(self.display_wavform))
        self.scope.do_command('DISplay:INTENSITy:GRAticule '+str(self.display_graticule))
        self.scope.do_command('HORizontal:RECOrdlength 1E+6')
        self.scope.do_command('FPAnel:PRESS MENUOff')
        self.scope.do_command('SELECT:CH1 ON')
        self.scope.do_command('SELECT:CH2 ON')
        self.scope.do_command('SELECT:CH3 ON')
        self.scope.do_command('CH1:POSition 2')
        self.scope.do_command('CH2:POSition 0')
        self.scope.do_command('CH3:POSition -3')
        #self.scope.do_command('CH1:OFFSet '+str(self.Output_Voltage))
        #self.scope.do_command('CH1:SCAle '+str(self.Output_Voltage))
        self.scope.do_command('CH2:OFFSet '+str(trig_votage))
        self.scope.do_command('CH2:SCAle '+str(abs(Voltage_1-Voltage_2)/2))
        self.scope.do_command('HORIZONTAL:SCALE 1E-3')
        
        #self.scope.do_command('acquire:state ON')
        self.scope.do_command('TRIGger:A:EDGE:SOUrce CH2')
        self.scope.do_command('TRIGger:A:LEVel '+str(trig_votage))
        self.scope.do_command('TRIGger:A:MODe AUTO')
        self.scope.do_command('TRIGger:A:EDGE:SLOpe '+str(SLOpe))
        self.scope.do_command('TRIGger:A:EDGE:SOUrce CH2')
        self.scope.do_command('FPAnel:PRESS SINGleseq')
        #self.check_single_state() # check while loop
        self.scope.close()
    
    def start(self, testype):
        if testype == "Regulation" :
            '''scale_list = ["400E-3", "40E-3", "400E-6", "200E-6", "40E-6"]
            #scale_list = ["400E-3", "40E-6"]
            self.VISA_ADDRESS = self.VISA_ADDRESS

            self.setup( "1E+6")
            self.set_measurement()
            
            for scale in scale_list:
                scale = float(scale)
                Volts, Time = self.get_rawdata( 1,scale)
                pk2pk_time = []
                pk2pk_time, avg_time = self.find_timedif(Volts, Time, scale)

            msg = "pk2pk time len: {0} \n, avg time : {1}".format(pk2pk_time, avg_time)
            #print(msg)
            if pk2pk_time != None:
                #print("avg_time/scale :" + str(avg_time/scale))
                if (avg_time/scale) < 1 :
                    self.set_scale(self.normal_scale)
                if (avg_time/scale) > 1 :
                    self.set_scale(2/self.frequency)
                    print(2/self.frequency)
            else:
                self.cl_dif(self.stack_p2p)
                self.set_scale(self.normal_scale)'''

            self.setup( "1E+6")

            thread = Auto_FFT()
            thread.VISA_ADDRESS = self.VISA_ADDRESS
            thread.lineEdit_scale_period = self.lineEdit_scale_period
            thread.Default_scale = self.Default_scale
            thread.FFT_image_path = self.FFT_image_path
            thread.main()

        elif testype == "Load":
            #self.setup("20E+6")
            #self.set_measurement()
            #self.get_rawdata( 1, "1E-3")

            self.scope = DPO4000_visa()
            self.scope.VISA_ADDRESS = self.VISA_ADDRESS
            self.scope.connect()
            #self.scope.do_command('FPAnel:PRESS DEFaultsetup')
            #self.scope.do_command('FPAnel:PRESS MENUOff')
            #self.scope.do_command('CH3:PRObe:FORCEDRange 5')
            
            #self.scope.do_command('DISplay:INTENSITy:WAVEform '+str(self.display_wavform))
            #self.scope.do_command('DISplay:INTENSITy:GRAticule '+str(self.display_graticule))
            self.scope.do_command('HORizontal:RECOrdlength 1E+6')

            #self.scope.do_command('AUTOSet EXECute')
            self.scope.do_command('acquire:state ON')
            self.check_trig_num = 0
            self.check_single_state() # check while loop

            self.scope.do_command('SELECT:CH1 ON')
            self.scope.do_command('SELECT:CH2 OFF')
            self.scope.do_command('SELECT:CH3 ON')
            self.scope.do_command('SELECT:CH4 OFF')

            self.scope.do_command('CH1:POSition 2') #Default position is CH1
            self.scope.do_command('CH3:POSition -2') #Default position is CH3

            time.sleep(2)
            self.scope.close()

        elif testype == "Line":
            self.setup("1E+6")

            self.scope = DPO4000_visa()
            self.scope.VISA_ADDRESS = self.VISA_ADDRESS
            self.scope.connect()
            self.scope.do_command('FPAnel:PRESS DEFaultsetup')
            self.scope.do_command('FPAnel:PRESS MENUOff')
        
            self.scope.do_command('CH3:PRObe:FORCEDRange 5')
            
            self.scope.do_command('DISplay:INTENSITy:WAVEform '+str(self.display_wavform))
            self.scope.do_command('DISplay:INTENSITy:GRAticule '+str(self.display_graticule))
            self.scope.do_command('HORizontal:RECOrdlength 10E+3')

            self.scope.do_command('AUTOSet EXECute')
            time.sleep(2)

            self.scope.close()

        print('Done!')
