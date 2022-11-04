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
        self.check_trig_num = 0
        self.scope = None
        self.scope_33250 = None

    def clear_tmp(self):
        self.poin_list = []
        self.data = []
    
    # Visa call back function
    def do_query(self, command):
        # The is call function in the Visa lib 
        try:
            return self.scope.query("%s" % command).strip()
        except Exception as error_msg: 
            print(error_msg)
            pass
        
    # Visa call back function
    def do_command(self, command):
        try:
            self.scope.write("%s" % command)
        except Exception as error_msg: 
            print(error_msg)
            pass
    
    def check_single_state(self):
        self.check_trig_num += 1
        state = self.do_query('ACQUIRE:STATE?')
        #print(state)
        if state == '1':
            if self.check_trig_num >= 20:
                time.sleep(1)
                self.do_command('FPAnel:PRESS FORCetrig')
                time.sleep(1)
                self.check_single_state()

            time.sleep(0.1)
            self.check_single_state()
        elif state == '0':
            time.sleep(1)
            return "STOP"
    
    def auto_Scale(self):
        self.rm = visa.ResourceManager()
        self.scope = self.rm.open_resource('USB0::0x0699::0x0405::C022392::INSTR')
        self.scope.timeout = 10000

        # Reset the oscilloscope
        self.do_command('FPAnel:PRESS DEFaultsetup')
        self.do_command('FPAnel:PRESS MENUOff')
        self.do_command('HORizontal:RECOrdlength 10E+3')

        time.sleep(2)
        self.do_command('AUTOSet EXECute')
        time.sleep(2)

        # Default Triger setup
        self.do_command('CH1:BANdwidth 20E+6')
        self.do_command('TRIGger:A:EDGE:SOUrce CH1')
        self.do_command('TRIGger:A:TYPe EDGe')
        self.do_command('TRIGger:A:MODe AUTO')
        self.do_command('TRIGger:A:EDGE:COUPling DC')
        self.do_command('TRIGger:A:EDGE:SLOpe FALL')

        for i in range(8):
            self.do_command('MEASUrement:MEAS'+str(i+1)+':STATE OFF')

        channel_list = [1,1,1,1,1]
        MEASUrement_Type = ["MAXimum","MINImum","MEAN","FREQuency","pk2pk"]

        for i in range(8):
            self.do_command('MEASUrement:MEAS'+str(i+1)+':STATE OFF')
        for i in range(len(MEASUrement_Type)):
            self.do_command('MEASUrement:MEAS'+str(i+1)+':SOURCE1 CH'+str(channel_list[i]))
            self.do_command('MEASUrement:MEAS'+str(i+1)+':TYPe '+ MEASUrement_Type[i])
            self.do_command('MEASUrement:MEAS'+str(i+1)+':STATE ON')

        for index in range(3):
            print("{}{}{}".format("-"*50,index,"-"*50))
            time.sleep(1)
            self.do_command('ACQuire:STOPAfter SEQuence')
            self.do_command('acquire:state ON')
            self.check_single_state()
            
            CH1_MAX_VALue = float(self.do_query('MEASUrement:MEAS1:VALue?'))
            CH1_MINI_VALue = float(self.do_query('MEASUrement:MEAS2:VALue?'))
            CH1_MEAN_VALue = float(self.do_query('MEASUrement:MEAS3:VALue?'))
            CH1_AMPlitude_VALue = float(self.do_query('MEASUrement:MEAS5:VALue?'))
            offset_value = ((CH1_MAX_VALue-CH1_MINI_VALue)/2)+CH1_MINI_VALue
            Scale_value = CH1_AMPlitude_VALue/2
            self.do_command('CH1:BANdwidth 20E+6')
            self.do_command('CH1:OFFSet {}'.format(offset_value))
            self.do_command('CH1:SCAle {}'.format(Scale_value))

            print("OffSet：{}, Scale：{}".format(offset_value, Scale_value))

            self.do_command('TRIGger:A:EDGE:SOUrce CH1')
            self.do_command('TRIGger:A SETLevel {}'.format(offset_value))
            self.do_command('TRIGger:A:MODe AUTO')

            self.do_command('ACQuire:STOPAfter SEQuence')
            self.do_command('acquire:state ON')
            self.do_command('SELECT:MATH ON')
            self.do_command("MATH:TYPE FFT")
            self.check_single_state()

        self.rm.close()
        self.scope.close()

    def auto_DPO4054(self, horizontal_scale):

        self.rm = visa.ResourceManager()
        self.scope = self.rm.open_resource('USB0::0x0699::0x0405::C022392::INSTR')
        self.scope.timeout = 10000

        time.sleep(1)
        self.do_command('SELECT:MATH ON')
        self.do_command("MATH:TYPE FFT")
        self.do_command("MATH:VERTical:POSition 3")
        #scope.write("MATH:HORizontal:POSition {}".format(frqY/(xincr * len(Volts_ch1))*99))
        #scope.write("MATH:HORizontal:SCAle {}".format(frqY/20))
        time.sleep(10)

        self.do_command('CH1:POSition 1')
        self.do_command('HORIZONTAL:SCALE '+str(horizontal_scale))
        self.do_command('ACQuire:STOPAfter SEQuence')
        self.do_command('acquire:state ON')
        time.sleep(3+float(horizontal_scale)*10)
        
        self.check_trig_num = 0
        self.check_single_state()
    
        self.do_command('DATA:SOU MATH')
        self.do_command('DATA:WIDTH 1')
        self.do_command('DATA:ENC RPB')

        ymult = float(self.do_query('WFMPRE:YMULT?'))
        yzero = float(self.do_query('WFMPRE:YZERO?'))
        yoff = float(self.do_query('WFMPRE:YOFF?'))
        xincr = float(self.do_query('WFMPRE:XINCR?'))

        print("ymult：{}, yzero：{}, yoff：{}, xincr：{}".format(ymult, yzero, yoff, xincr))

        self.do_command('CURVE?')
        data_ch1 = self.scope.read_raw()
        headerlen = 8
        #header = data_ch1[:headerlen]
        #ADC_wave_ch1 = data_ch1[headerlen:]
        ADC_wave_ch1 = data_ch1

        ADC_wave_ch1 = np.array(unpack('%sB' % len(ADC_wave_ch1),ADC_wave_ch1))
        Volts_ch1 = (ADC_wave_ch1 - yoff) * ymult  + yzero
        Time = np.arange(0, xincr * len(Volts_ch1), xincr)

        Volts_ch1 = Volts_ch1[100:]
        Time = Time[100:]

        peakY = np.max(Volts_ch1)
        locY = np.argmax(Volts_ch1)
        frqY = Time[locY]
        print("peakY：{}, locY：{}, frqY：{}".format(peakY, locY, frqY))
        self.data.append([Volts_ch1, Time])
        self.poin_list.append([frqY, peakY])
        self.rm.close()
        self.scope.close()
    
    def auto_33250A(self,FUN_SHAPe, FRE, VOLTage):
        self.rm_33250 = visa.ResourceManager()
        self.scope_33250 = self.rm_33250.open_resource('GPIB0::10::INSTR')
        self.scope_33250.timeout = 10000
        
        #FUNCtion:SHAPe {SINusoid|SQUare|RAMP|PULSe|NOISe|DC|USER} 
        self.scope_33250.write('FUNCtion:SHAPe '+FUN_SHAPe)
        self.scope_33250.write('FREQ '+str(FRE))
        self.scope_33250.write('VOLTage:UNIT VPP')
        self.scope_33250.write('VOLTage '+VOLTage)
        self.scope_33250.write('VOLTage:OFFSet 0')
        self.scope_33250.write('output:state on')

        self.rm_33250.close()
        self.scope_33250.close()
    
    def plot_FFT(self,savename, shape, VOLTage, Sacle_list, Freq_list ):
        pylab.cla()
        pylab.figure(figsize=(18, 8), dpi=1200)
        pylab.title('Oscilloscope FFT - Shape:{} , Freq:{}'.format(shape, Freq_list[0]))#, y=-0.01)
        pylab.ylabel('Voltage (dBV)')

        for Poin in self.poin_list:
            if Poin[1] >= -60:
                pylab.plot(Poin[0], Poin[1], 'r.', markersize=6)
                pylab.annotate("%.1fdBV , %.1gHz" %(Poin[1], Poin[0]),(Poin[0], Poin[1]), rotation=80)

        pylab.xlabel('Time')
        legend_list = []
        for index, tmp_data in enumerate(self.data):
            pylab.plot(tmp_data[1][:], tmp_data[0][:],linewidth = 0.8,alpha = 0.8, label="%sV, %s/div, %.1fdBV , %.1gHz" %(VOLTage,Sacle_list[index],self.poin_list[index][1], self.poin_list[index][0]))
            #legend_list.append(data)
        pylab.legend(loc ="lower right")
        #pylab.plot(Time, data_3)
        #pylab.plot(Volts_ch1)
        pylab.grid('on')
        pylab.savefig(savename + '.png')
        pylab.cla()


nowTime = int(time.time())
struct_time = time.localtime(nowTime)
timeString = time.strftime("%Y%m%d%I%M%S", struct_time)
print(timeString)

FUN_SHAPe = ["RAMP"]
VOLTage_list = ["10E-3"] #,"20E-3","30E-3","40E-3","50E-3","70E-3","90E-3","110E-3","130E-3"]
# [Freq, Scale]
Freq_list = [48E+3]
Sacle_list = [400E-3, 200E-3, 40E-3, 10E-3, 1E-3, 400E-6]

for shape in FUN_SHAPe:
    for VOLTage in VOLTage_list:
        for freq_item in Freq_list:
            autotest_model = auto_FFT_test()
            autotest_model.clear_tmp()
            autotest_model.auto_Scale()
            for Sacle_item in Sacle_list:
                #autotest_model.auto_33250A(shape,freq_item,VOLTage)
                autotest_model.auto_DPO4054(Sacle_item)
                autotest_model.plot_FFT("test_image/{}_{}_1M-0.5K_{}".format(shape,VOLTage,timeString), shape, VOLTage, Sacle_list, Freq_list )
                if Sacle_item >= 200E-3:
                    autotest_model.plot_FFT("test_image/{}_{}_0-5K_{}".format(shape,VOLTage,timeString), shape, VOLTage, Sacle_list, Freq_list)