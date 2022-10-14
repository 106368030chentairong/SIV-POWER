import time
import pyvisa as visa
import numpy as np
from struct import unpack
import pylab

horizontal_scale = 4E-3

class auto_FFT_test:
    def __init__(self) -> None:
        self.poin_list = []
        self.data = []

    def clear_tmp(self):
        self.poin_list = []
        self.data = []

    def auto_DPO4054(self, horizontal_scale):

        rm = visa.ResourceManager()
        scope = rm.open_resource('USB0::0x0699::0x0401::C020251::INSTR')
        scope.timeout = 10000

        scope.write('FPAnel:PRESS DEFaultsetup')
        scope.write('FPAnel:PRESS MENUOff')
        scope.write('HORizontal:RECOrdlength 10E+3')

        time.sleep(2)
        scope.write('AUTOSet EXECute')
        time.sleep(2)

        for i in range(8):
            scope.write('MEASUrement:MEAS'+str(i+1)+':STATE OFF')

        scope.write('MEASUrement:MEAS1:SOURCE1 CH1')
        scope.write('MEASUrement:MEAS1:TYPe MEAN')
        scope.write('MEASUrement:MEAS1:STATE ON')
        scope.write('MEASUrement:MEAS2:SOURCE1 CH1')
        scope.write('MEASUrement:MEAS2:TYPe PK2pk')
        scope.write('MEASUrement:MEAS2:STATE ON')

        for index in range(2):
            time.sleep(5)
            scope.write('ACQuire:STOPAfter SEQuence')
            scope.write('acquire:state ON')

            CH1_MEAN_VALue = scope.query('MEASUrement:MEAS1:VALue?')
            CH1_AMPlitude_VALue = scope.query('MEASUrement:MEAS2:VALue?')
            print("CH1_MEAN_VALue : ", CH1_MEAN_VALue)
            scope.write('CH1:BANdwidth 20E+6')
            scope.write('CH1:OFFSet '+str(CH1_MEAN_VALue))
            scope.write('CH1:SCAle '+str(float(CH1_AMPlitude_VALue)/3))

            scope.write('TRIGger:A:EDGE:SOUrce CH1')
            scope.write('TRIGger:A SETLevel')
            scope.write('TRIGger:A:MODe AUTO')

        scope.write('SELECT:MATH ON')
        scope.write("MATH:TYPE FFT")

        scope.write('CH1:POSition 1')
        scope.write('HORIZONTAL:SCALE '+str(horizontal_scale))
        scope.write('ACQuire:STOPAfter SEQuence')
        scope.write('acquire:state ON')

        time.sleep(3+horizontal_scale*20)
        scope.write('DATA:SOU MATH')
        scope.write('DATA:WIDTH 1')
        scope.write('DATA:ENC RPB')

        ymult = float(scope.query('WFMPRE:YMULT?'))
        yzero = float(scope.query('WFMPRE:YZERO?'))
        yoff = float(scope.query('WFMPRE:YOFF?'))
        xincr = float(scope.query('WFMPRE:XINCR?'))

        print(ymult, yzero, yoff, xincr)

        scope.write('CURVE?')
        data_ch1 = scope.read_raw()
        headerlen = 1 + int(data_ch1[1])
        header = data_ch1[:headerlen]
        ADC_wave_ch1 = data_ch1[headerlen:-1]

        ADC_wave_ch1 = np.array(unpack('%sB' % len(ADC_wave_ch1),ADC_wave_ch1))
        Volts_ch1 = (ADC_wave_ch1 - yoff) * ymult  + yzero
        Time = np.arange(0, xincr * len(Volts_ch1), xincr)
        peakY = np.max(Volts_ch1)
        locY = np.argmax(Volts_ch1)
        frqY = Time[locY]
        print(peakY, locY,frqY)
        self.data.append([Volts_ch1, Time])
        self.poin_list.append([frqY, peakY])
        rm.close()
        scope.close()
    
    def auto_33250A(self,FUN_SHAPe, FRE, VOLTage):
        rm = visa.ResourceManager()
        scope = rm.open_resource('GPIB0::10::INSTR')
        scope.timeout = 10000
        
        #FUNCtion:SHAPe {SINusoid|SQUare|RAMP|PULSe|NOISe|DC|USER} 
        scope.write('FUNCtion:SHAPe '+FUN_SHAPe)
        scope.write('FREQ '+str(FRE))
        scope.write('VOLTage:UNIT VPP')
        scope.write('VOLTage '+VOLTage)
        scope.write('VOLTage:OFFSet 0')

        rm.close()
        scope.close()
    
    def plot_FFT(self,savename):
        pylab.figure(figsize=(9, 4), dpi=1200)
        pylab.title('Oscilloscope Math FFT')
        pylab.ylabel('Voltage (dBV)')

        for Poin in self.poin_list:
            if Poin[1] >= -50:
                pylab.plot(Poin[0], Poin[1], 'r.', markersize=12)
                pylab.annotate(str(int(Poin[0]))+" Hz",(Poin[0], Poin[1]), rotation=60)

        pylab.xlabel('Time')
        for tmp_data in self.data:
            pylab.plot(tmp_data[1], tmp_data[0])
        #pylab.plot(Time, data_3)
        #pylab.plot(Volts_ch1)
        pylab.grid('on')
        pylab.savefig(savename + '.png')

FUN_SHAPe = ["SINusoid","SQUare","RAMP"]
VOLTage_list = ["10E-3","120E-3"]
test_list = [[1E+6, 20E-6],[500E+3, 20E-6],[1E+3, 4E-3]]

for VOLTage in VOLTage_list:
    for shape in FUN_SHAPe:
        autotest_model = auto_FFT_test()
        autotest_model.clear_tmp()
        for test_item in test_list:
            autotest_model.auto_33250A(shape,test_item[0],VOLTage)
            autotest_model.auto_DPO4054(test_item[1])
        autotest_model.plot_FFT("test_image/{}_{}_1M-500K".format(shape,shape))