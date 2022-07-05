from audioop import add
from decimal import MIN_EMIN
import time
from ctypes import addressof
from tkinter.messagebox import NO
from turtle import back
import pyvisa as visa
import numpy as np
from struct import unpack
import pylab

import matplotlib.pyplot as plt

import calendar

from lib.tektronix_4000 import DPO4000_visa

class Auto_trig():
    def __init__(self):
        self.VISA_ADDRESS = None
        self.scope = None
        #self.record_length = None
        self.normal_scale = "1E-3" 
        self.pk2pk = 0
        self.stack_p2p = []
    
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

        state = self.scope.do_query('ACQUIRE:STATE?')
        print(state)
        if state == '1':
            time.sleep(0.1)
            self.check_single_state()
        elif state == '0':
            time.sleep(1)
            return "STOP"
    
    def setup(self, record_length):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()
        self.scope.do_command('FPAnel:PRESS DEFaultsetup')
        self.scope.do_command('DISplay:INTENSITy:WAVEform 100')
        self.scope.do_command('DISplay:INTENSITy:GRAticule 50')
        self.scope.do_command('HORizontal:RECOrdlength '+ str(record_length))
        self.scope.do_command('FPAnel:PRESS MENUOff')
    
    def set_scale(self, scale):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()
        self.scope.do_command('HORIZONTAL:SCALE '+str(scale))
        self.scope.do_command('acquire:state ON')
        self.check_single_state() # check while loop
        self.scope.close()

    def get_rawdata(self, channel, scale):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()
        
        self.scope.do_command('CH'+str(channel)+':BANdwidth 20E+6')
        self.scope.do_command('HORIZONTAL:SCALE '+str(scale))

        self.scope.do_command('TRIGger:A:EDGE:SOUrce CH'+str(channel))
        self.scope.do_command('TRIGger:A:LEVel '+str(self.pk2pk/2))
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

        raw_data = self.scope.get_raw()
        headerlen = 2 + int(raw_data[1])
        header = raw_data[:headerlen]
        ADC_wave_ch1 = raw_data[headerlen:-1]

        ADC_wave_ch1 = np.array(unpack('%sB' % len(ADC_wave_ch1),ADC_wave_ch1))

        Volts = (ADC_wave_ch1 - yoff) * ymult  + yzero

        max_volume = max(Volts)
        min_volume = min(Volts)
        print(max_volume, min_volume)
        self.pk2pk = abs(max_volume - min_volume)
        self.stack_p2p.append(abs(max_volume - min_volume))
        print("PK-2-PK : "+ str( self.pk2pk ))

        Time = np.arange(0, xincr * len(Volts), xincr)
        self.scope.close()

        self.save_np([Volts, Time])
        return Volts, Time

    def find_timedif(self, Rawdata, Time, scale):
        delta = 1
        raw_max = max(Rawdata)
        raw_min = min(Rawdata)
        pk2pk = abs(raw_max - raw_min)/2
        avg = pk2pk
        #avg = 0.04
        #print((avg)*delta)

        tmp = []
        for index, val in enumerate(Rawdata):
            if val >= (avg)*delta:
                tmp.append([index, val])

        pk2pk_time = []
        avg_dif_time = []
        for index, val in enumerate(tmp):
            if index < len(tmp)-1:
                #print(tmp[index+1][0] - val[0])
                time_dif = Time[tmp[index+1][0] ]- Time[val[0]]
                if (abs(time_dif)) >= scale*1:
                    #print(time_dif)
                    pk2pk_time.append([time_dif, [val[0], val[1]], [tmp[index+1][0], tmp[index+1][1]]])
                    avg_dif_time.append(time_dif)

        if avg_dif_time != []:
            avg_time = sum(avg_dif_time)/len(avg_dif_time)
        else:
            avg_time = 0
            pk2pk_time = 0
        
        return pk2pk_time, avg_time

    def save_np(self, data):
        current_GMT = time.gmtime()

        # ts stores timestamp
        ts = calendar.timegm(current_GMT)
        print("Current timestamp:", ts)
        
        with open('np_tmp/'+str(ts)+'.npy', 'wb') as f:
            np.save(f, np.array(data))
    
    def start(self):
        
        scale_list = ["400E-3", "40E-3", "400E-6", "1E-3"]
        self.VISA_ADDRESS = "USB0::0x0699::0x0405::C022392::INSTR"

        self.setup( "1E+6")
        
        for scale in scale_list:
            scale = float(scale)
            Volts, Time = self.get_rawdata( 1,scale)
            pk2pk_time = []
            pk2pk_time, avg_time = self.find_timedif(Volts, Time, scale)

        print(self.stack_p2p)
        #print(pk2pk_time, avg_time, avg_time/scale)
        print(avg_time)
        if avg_time <=1 or avg_time == 0:
            self.set_scale(self.normal_scale)

        #if scale <= float(min_scale):
        #    break
            
        print('Done!')

if __name__ == '__main__':
    Auto_trig().start()

