from ast import While
from msilib.schema import TextStyle
from re import S
import time
import numpy as np
from struct import unpack

import matplotlib.pyplot as plt

import calendar

from lib.tektronix_4000 import DPO4000_visa

class Auto_trig():
    def __init__(self):
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
        self.scope.do_command('DISplay:INTENSITy:WAVEform 100')
        self.scope.do_command('DISplay:INTENSITy:GRAticule 50')
        self.scope.do_command('HORizontal:RECOrdlength '+ str(record_length))
        self.scope.do_command('FPAnel:PRESS MENUOff')
        self.scope.do_command('SELECT:CH1 ON')
        self.scope.do_command('SELECT:CH2 OFF')
        self.scope.do_command('SELECT:CH3 ON')
        self.scope.do_command('SELECT:CH3 ON')
        self.scope.do_command('CH1:POSition 0')
        self.scope.do_command('CH3:POSition -2')
        self.scope.do_command('CH1:OFFSet 1')
        self.scope.do_command('CH1:SCAle 5')
        self.scope.do_command('CH3:SCALe 1')
        self.scope.close()
    
    def set_scale(self, scale):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()
        self.scope.do_command('HORIZONTAL:SCALE '+str(scale))
        self.scope.do_command('acquire:state ON')
        self.check_single_state() # check while loop
        self.scope.close()

    def set_measurement(self):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()

        channel_list = [1,1,1,1,1]
        MEASUrement_Type = ["MAXimum","MINImum","MAXimum","MINImum","FREQuency"]

        for i in range(8):
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':STATE OFF')
        for i in range(len(MEASUrement_Type)):
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':SOURCE1 CH'+str(channel_list[i]))
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':TYPe '+ MEASUrement_Type[i])
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':STATE ON')

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
    
    def get_rawdata(self, channel, scale):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()
        
        self.scope.do_command('CH'+str(channel)+':BANdwidth 20E+6')
        self.scope.do_command('CH1:OFFSet 0.8')
        self.scope.do_command('CH1:SCAle 0.05')
        self.scope.do_command('HORIZONTAL:SCALE '+str(scale))

        self.scope.do_command('TRIGger:A:EDGE:SOUrce CH'+str(channel))
        self.scope.do_command('TRIGger:A:LEVel '+str(self.trig_level))
        self.scope.do_command('TRIGger:A:EDGE:SOUrce CH1')
        #self.scope.do_command('TRIGger:A:LEVel '+str(0))
        self.scope.do_command('TRIGger:A:TYPe EDGe')
        self.scope.do_command('TRIGger:A:MODe auto')
        self.scope.do_command('TRIGger:A:EDGE:SLOpe FALL')

        self.scope.do_command('DATA:SOU CH'+str(channel))
        self.scope.do_command('DATA:WIDTH 1')
        self.scope.do_command('DATA:ENC RPB')
        
        self.scope.do_command('ACQuire:STOPAfter SEQuence')
        self.scope.do_command('acquire:state ON')
        self.check_single_state() # check while loop

        ymult = float(self.scope.do_query('WFMPRE:YMULT?'))
        yzero = float(self.scope.do_query('WFMPRE:YZERO?'))
        yoff = float(self.scope.do_query('WFMPRE:YOFF?'))
        xincr = float(self.scope.do_query('WFMPRE:XINCR?'))
        
        self.check_frq_num = 0
        self.frequency = self.get_frequency()
            
        raw_data = self.scope.get_raw()
        headerlen = 2 + int(raw_data[1])
        header = raw_data[:headerlen]
        ADC_wave_ch1 = raw_data[headerlen:-1]

        ADC_wave_ch1 = np.array(unpack('%sB' % len(ADC_wave_ch1),ADC_wave_ch1))

        Volts = (ADC_wave_ch1 - yoff) * ymult  + yzero

        max_volume = max(Volts)
        min_volume = min(Volts)
        self.trig_level = ((max_volume-min_volume)/2) +min_volume
        self.pk2pk = abs(max_volume - min_volume)
        self.stack_p2p.append(abs(max_volume - min_volume))

        self.scope.do_command('CH1:OFFSet '+str(self.trig_level))
        self.scope.do_command('CH1:SCAle '+str(self.pk2pk*0.2))
        self.scope.do_command('ACQuire:STOPAfter SEQuence')
        self.scope.do_command('acquire:state ON')
        self.check_single_state() # check while loop
        
        print("PK2PK : "+ str( self.pk2pk ))
        print("satck PK2PK :"+str( self.stack_p2p ))
        print("frequency : "+str(self.frequency))
        print("-"*10)
        Time = np.arange(0, xincr * len(Volts), xincr)

        self.scope.close()

        #self.save_np([Volts, Time])
        return Volts, Time

    def find_timedif(self, Rawdata, Time, scale):
        delta = 1
        #avg = 0.04
        #print((avg)*delta)

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
                if (abs(time_dif)) >= scale*0.1:
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
    
    def setup_trig(self, A_level, SLOpe):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()

        #self.scope.do_command('FPAnel:PRESS DEFaultsetup')
        self.scope.do_command('DISplay:INTENSITy:WAVEform 100')
        self.scope.do_command('DISplay:INTENSITy:GRAticule 50')
        self.scope.do_command('HORizontal:RECOrdlength 1E+6')
        self.scope.do_command('FPAnel:PRESS MENUOff')
        self.scope.do_command('SELECT:CH1 ON')
        self.scope.do_command('SELECT:CH2 ON')
        self.scope.do_command('SELECT:CH3 ON')
        self.scope.do_command('SELECT:CH3 ON')
        self.scope.do_command('CH1:POSition 2')
        self.scope.do_command('CH2:POSition 0')
        self.scope.do_command('CH3:POSition -3')
        self.scope.do_command('CH1:OFFSet 0.8')
        self.scope.do_command('CH1:SCAle 0.05')
        self.scope.do_command('CH2:OFFSet 4')
        self.scope.do_command('CH2:SCAle 0.4')
        self.scope.do_command('HORIZONTAL:SCALE 1E-3')
        
        #self.scope.do_command('acquire:state ON')
        self.scope.do_command('TRIGger:A:LEVel '+str(A_level))
        self.scope.do_command('TRIGger:A:MODe AUTO')
        self.scope.do_command('TRIGger:A:EDGE:SLOpe '+str(SLOpe))
        self.scope.do_command('TRIGger:A:EDGE:SOUrce CH2')
        self.scope.do_command('FPAnel:PRESS SINGleseq')
        #self.check_single_state() # check while loop
        self.scope.close()
    
    def start(self, testype):
        if testype == "Regulation" :
            #scale_list = ["400E-3", "40E-3", "400E-6", "40E-6"]
            scale_list = ["400E-3", "40E-6"]
            self.VISA_ADDRESS = "USB0::0x0699::0x0405::C022392::INSTR"

            self.setup( "1E+6")
            self.set_measurement()
            
            for scale in scale_list:
                scale = float(scale)
                Volts, Time = self.get_rawdata( 1,scale)
                pk2pk_time = []
                pk2pk_time, avg_time = self.find_timedif(Volts, Time, scale)

            msg = "pk2pk time len: {0} \n, avg time : {1}".format(pk2pk_time, avg_time)
            print(msg)
            if pk2pk_time != None:
                print("avg_time/scale :" + str(avg_time/scale))
                if (avg_time/scale) < 1 :
                    self.set_scale(self.normal_scale)
                if (avg_time/scale) > 1 :
                    self.set_scale(2/self.frequency)
                    print(2/self.frequency)
            else:
                self.cl_dif(self.stack_p2p)
                self.set_scale(self.normal_scale)

        elif testype == "Load":
            self.VISA_ADDRESS = "USB0::0x0699::0x0405::C022392::INSTR"
            #self.scope.do_command('ACQuire:STOPAfter SEQuence')
            #self.scope.do_command('acquire:state ON')
            self.setup("1E+6")
            self.set_measurement()
            Volts, Time = self.get_rawdata( 1, "0.5")
            #self.scope.do_command('HORIZONTAL:SCALE 0.5')
            #self.scope.do_command('acquire:state ON')
            #self.check_single_state() # check while loop
        
        elif testype == "Line":
            self.VISA_ADDRESS = "USB0::0x0699::0x0405::C022392::INSTR"
            self.setup("1E+6")

            #self.set_measurement()
            #self.set_scale(self.normal_scale)
            #self.scope.do_command('CH1:OFFSet 2.5')
            #self.scope.do_command('CH1:SCAle 0.5')

        print('Done!')