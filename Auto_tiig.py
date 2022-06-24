from decimal import MIN_EMIN
import time
from ctypes import addressof
from turtle import back
import pyvisa as visa
import numpy as np
from struct import unpack
import pylab

import matplotlib.pyplot as plt

import calendar

def get_RAW(address, channel, scale):
    rm = visa.ResourceManager()
    scope = rm.get_instrument(address)
    scope.timeout = 10000

    scope.write('HORizontal:RECOrdlength '+RECOrdlength )
    scope.write('HORIZONTAL:SCALE '+str(scale))

    scope.write('TRIGger:A:EDGE:SOUrce CH1')
    scope.write('TRIGger:A:LEVel 0')
    scope.write('TRIGger:A:TYPe EDGe')
    scope.write('TRIGger:A:MODe NORMal')
    scope.write('TRIGger:A:EDGE:SLOpe FALL')

    scope.write('DATA:SOU CH'+str(channel))
    scope.write('DATA:WIDTH 1')
    scope.write('DATA:ENC RPB')

    scope.write('acquire:state ON')
    time.sleep(scale*10*1.2)
    scope.write('acquire:state OFF')

    #scope.write('acquire:state 0')
    #scope.write('acquire:stopafter SEQUENCE') 
    #scope.write('acquire:state 1')

    ymult = float(scope.query('WFMPRE:YMULT?'))
    yzero = float(scope.query('WFMPRE:YZERO?'))
    yoff = float(scope.query('WFMPRE:YOFF?'))
    xincr = float(scope.query('WFMPRE:XINCR?'))

    scope.write('CURVE?')
    data_ch1 = scope.read_raw()
    headerlen = 2 + int(data_ch1[1])
    header = data_ch1[:headerlen]
    ADC_wave_ch1 = data_ch1[headerlen:-1]

    ADC_wave_ch1 = np.array(unpack('%sB' % len(ADC_wave_ch1),ADC_wave_ch1))

    Volts = (ADC_wave_ch1 - yoff) * ymult  + yzero

    Time = np.arange(0, xincr * len(Volts), xincr)

    rm.close()
    scope.close()
    save_np([Volts, Time])
    return Volts, Time

def find_timedif(Rawdata, Time, scale):
    delta = 1
    avg = sum(Rawdata)/len(Rawdata)
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
            if (abs(time_dif)) >= scale*0.5:
                #print(time_dif)
                pk2pk_time.append([time_dif, [val[0], val[1]], [tmp[index+1][0], tmp[index+1][1]]])
                avg_dif_time.append(time_dif)
    
    if avg_dif_time != []:
        avg_time = sum(avg_dif_time)/len(avg_dif_time)
    else:
        avg_time = 0
    return pk2pk_time, avg_time

def save_np(data):
    current_GMT = time.gmtime()

    # ts stores timestamp
    ts = calendar.timegm(current_GMT)
    print("Current timestamp:", ts)
    
    with open('np_tmp/'+str(ts)+'.npy', 'wb') as f:
        np.save(f, np.array(data))

if __name__ == '__main__':
    address = "USB0::0x0699::0x0405::C022392::INSTR"
    RECOrdlength = "1E6"
    scale = 1
    min_scale = 0.00001
    Volts, Time = get_RAW(address, 1, scale)
    pk2pk_time = []
    pk2pk_time, avg_time = find_timedif(Volts, Time, scale)
    print(len(pk2pk_time), avg_time, avg_time/scale)

    while (avg_time/scale) < 0.5 or len(pk2pk_time) == 0:
        if len(pk2pk_time) != 0:
            scale = avg_time/1
        else:
            scale = scale/2

        Volts, Time = get_RAW(address, 1, scale)
        pk2pk_time = []
        pk2pk_time, avg_time = find_timedif(Volts, Time, scale)
        print(len(pk2pk_time), avg_time, avg_time/scale)

        if scale <= min_scale:
            break
        
    print('Done!')

'''
for pk2pk_val in pk2pk_time:
    plt.scatter(pk2pk_val[1][0], pk2pk_val[1][1])
    plt.scatter(pk2pk_val[2][0], pk2pk_val[2][1])
'''
#plt.plot(Volts)
#plt.show()