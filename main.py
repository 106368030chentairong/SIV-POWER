import os, sys, time
import pickle
import numpy as np
from Visa_Source_lib import *
import pyvisa as visa

import matplotlib.pyplot as plt

RECOrdlength = "5E6"

def setup(visa_address, scale=(0.5) ): #str(0.5/396000)):
    rm = visa.ResourceManager()
    scope = rm.open_resource(visa_address)
    scope.timeout = 10000
    scope.write('*cls') # clear ESR
    scope.write('FPAnel:PRESS DEFaultsetup')
    scope.write('FPAnel:PRESS MENUOff')
    scope.write('SELECT:CH3 1')
    scope.write('SELECT:CH2 1')

    #scope.write('autoset EXECUTE')
    scope.write('HORizontal:RECOrdlength '+RECOrdlength )
    scope.write('DISPLAY:INTEnsITY:WAVEFORM 100')

    scope.write('TRIGger:A:EDGE:SOUrce CH1')
    scope.write('TRIGger:A:LEVel 1')
    scope.write('TRIGger:A:TYPe EDGe')
    scope.write('TRIGger:A:MODe NORMal')
    scope.write('TRIGger:A:EDGE:SLOpe FALL')

    #scope.write('CURSor:FUNCtion SCREEN')
    
    #scope.write('acquire:state 0')
    #scope.write('acquire:stopafter SEQUENCE') 
    #scope.write('acquire:state 1')
    scope.write('HORizontal:RECOrdlength '+RECOrdlength )
    scope.write('HORIZONTAL:DELay:TIME '+str(scale*4))

    scope.write('HORIZONTAL:SCALE '+str(scale))

    scope.write('CH1:POSition 0.5')
    scope.write('CH3:POSition -2.5')
    
    scope.close()
    rm.close()

def get_rawdata_2(channel, visa_address ,SCALE=(0.05)):
    rm = visa.ResourceManager()
    scope = rm.open_resource(visa_address)
    scope.timeout = 10000 # ms
    scope.encoding = 'latin_1'
    scope.read_termination = '\n'
    scope.write_termination = None

    #scope.write('*rst') # reset
    #t1 = time.perf_counter()
    #r = scope.query('*opc?') # sync
    #t2 = time.perf_counter()
    #print('reset time: {}'.format(t2 - t1))

    #scope.write('autoset EXECUTE') # autoset
    t3 = time.perf_counter()
    r = scope.query('*opc?') # sync
    t4 = time.perf_counter()
    #print('autoset time: {} s'.format(t4 - t3))

    scope.write('HORizontal:RECOrdlength '+ RECOrdlength )
    scope.write('HORizontal:SAMPLERate 100e5')
    scope.write('HORIZONTAL:SCALE '+str(SCALE))

    scope.write('header 0')
    scope.write('data:encdg SRIBINARY')
    scope.write('data:source '+channel) 
    scope.write('data:start 1')
    record = int(scope.query('horizontal:recordlength?'))
    scope.write('data:stop {}'.format(record)) 
    scope.write('wfmoutpre:byt_n 1') 

    #scope.write('acquire:state 0')
    #scope.write('acquire:stopafter SEQUENCE') 
    #scope.write('acquire:state 1')

    #t5 = time.perf_counter()
    #r = scope.query('*opc?') # sync
    #t6 = time.perf_counter()
    #print('acquire time: {} s'.format(t6 - t5))

    # data query
    t7 = time.perf_counter()
    bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array, chunk_size = 1024*50)
    #bin_wave = scope.query_binary_values('DATa?', datatype='b', container=np.array)
    t8 = time.perf_counter()
    print('transfer time: {} s'.format(t8 - t7))

    # retrieve scaling factors
    tscale = float(scope.query('wfmoutpre:xincr?'))
    tstart = float(scope.query('wfmoutpre:xzero?'))
    vscale = float(scope.query('wfmoutpre:ymult?')) # volts / level
    voff = float(scope.query('wfmoutpre:yzero?')) # reference voltage
    vpos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)

    # error checking
    r = int(scope.query('*esr?'))
    print('event status register: 0b{:08b}'.format(r))
    r = scope.query('allev?').strip()
    print('all event messages: {}'.format(r))

    scope.close()
    rm.close()

    # create scaled vectors
    # horizontal (time)
    total_time = tscale * record
    tstop = tstart + total_time
    scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
    # vertical (voltage)
    unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
    CLK_scaled_wave = (unscaled_wave - vpos) * vscale + voff
    #CLK_filename = [(idx, item) for idx,item in enumerate(CLK_scaled_wave, start=1)]

    with open("ch"+channel+".txt", "wb") as fp:   #Pickling
        pickle.dump(CLK_scaled_wave, fp)

    return CLK_scaled_wave, scaled_time

#rm = visa.ResourceManager()
#scope = rm.open_resource("USB0::0x0699::0x0405::C022392::INSTR", send_end=True)
#scope.timeout = 25000 # ms

#scope.write('HORIZONTAL:SCALE 1')
#scope.write('TRIGger:A:LEVel:CH1 0.2')
'''
print("-"*5+"DC Power supply INFO"+"-"*5)
dc_power_supply  = Visa_Source_lib()
dc_power_supply.VISA_ADDRESS = "GPIB0::5::INSTR"
dc_power_supply.connect()
IDN_INFO = dc_power_supply.do_query_string("*IDN?").replace('\n', '') 
print("DC Power supply Name : "+IDN_INFO)
cmd_list = ["VOLTage 1"]
for cmd in cmd_list :
    dc_power_supply.do_command(cmd)

VOTAG = dc_power_supply.do_query_string("VOLTage?").replace('\n', '') 
#ACDC = dc_power_supply.do_query_string("VOLTage:ACDC?").replace('\n', '') 
print("DC Power supply Voltage : "+ VOTAG +"V")
#print("DC Power supply ACDC : "+ ACDC )

'''
'''
print("-"*5+"Dc Electronic loads INFO"+"-"*5)
dc_electronic_loads  = Visa_Source_lib()
dc_electronic_loads.VISA_ADDRESS = "GPIB0::7::INSTR"
dc_electronic_loads.connect()
IDN_INFO = dc_electronic_loads.do_query_string("*IDN?").replace('\n', '') 
print("Dc Electronic loads Name : "+IDN_INFO)

if sys.argv[1] == "0":
    dc_electronic_loads.do_command("SHOW L")
    cmd_list = ["*RST" , "MODE CCH", "CURR:STAT:L1 1" ]

elif sys.argv[1] == "1":
    dc_electronic_loads.do_command("SHOW L")
    cmd_list = ["*RST", "MODE CCDH",
                "CURR:DYN:L1 1", "CURR:DYN:L2 0.01",
                "CURR:DYN:RISE 0.25", "CURR:DYN:FALL 0.25",
                "CURR:DYN:T1 0.5", "CURR:DYN:T2 0.5"]

for cmd in cmd_list :
    dc_electronic_loads.do_command(cmd)

#scope.write("acquire:state 1")
#time.sleep(1)
#dc_power_supply.do_command("OUTP ON")
time.sleep(1)
dc_electronic_loads.do_command("LOAD ON")

load_Mode = dc_electronic_loads.do_query_string("MODE?").replace('\n', '') 
print("Dc Electronic loads Modle : "+load_Mode)
CURR_STATL1 = dc_electronic_loads.do_query_string("CURR:STAT:L1?").replace('\n', '') 
print("Dc Electronic loads CURR_STATL1 : "+CURR_STATL1)
MEAS_VoLT = dc_electronic_loads.do_query_string("MEAS:VoLT?").replace('\n', '') 
print("Dc Electronic loads MEAS V : "+MEAS_VoLT+" V")
MEAS_CURR= dc_electronic_loads.do_query_string("MEASure:CURRent?").replace('\n', '') 
print("Dc Electronic loads MEAS A : "+MEAS_CURR+" A")
MEAS_POW= dc_electronic_loads.do_query_string("MEAS:POW?").replace('\n', '') 
print("Dc Electronic loads MEAS P : "+MEAS_CURR+" W")

time.sleep(4)

#dc_power_supply.do_command("OUTP OFF")
#dc_electronic_loads.do_command("LOAD OFF")
'''
'''
time.sleep(1)
scope.write("acquire:state 0")

try:
    dc_power_supply.close()
    dc_electronic_loads.close()
    scope.close()
    rm.close()
except Exception:
    pass

#setup("USB0::0x0699::0x0405::C022392::INSTR")
'''
'''
CLK_scaled_wave, scaled_time = get_rawdata_2("1", "USB0::0x0699::0x0405::C022392::INSTR")
print(CLK_scaled_wave)
plt.plot(CLK_scaled_wave)
plt.show()
'''
channel = "2"
with open("ch"+channel+".txt", "rb") as fp:   #Pickling
    CLK_scaled_wave = pickle.load(fp)
print(CLK_scaled_wave)
plt.plot(CLK_scaled_wave)
plt.show()
'''
CLK_scaled_wave, scaled_time = get_rawdata_2("3", "USB0::0x0699::0x0405::C022392::INSTR")
print(CLK_scaled_wave)
plt.plot(CLK_scaled_wave)-
plt.show()


rm = visa.ResourceManager()
GPIB = rm.open_resource("GPIB1::7::INSTR")
GPIB.write("LOAD OFF")
#GPIB.write("MODE CCDL static")

GPIB.write("SHOW L")
GPIB.write("CURR:STAT:L1 0.1")
GPIB.write("CURR:STAT:L2 0.5")

GPIB.write("SHOW R")
GPIB.write("CURR:STAT:L1 0.2")
GPIB.write("CURR:STAT:L2 0.6")

rm.close()
GPIB.close()


rm = visa.ResourceManager()
GPIB = rm.open_resource("GPIB1::5::INSTR")
GPIB.write("VOLT 2.5")
'''
