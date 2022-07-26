from lib.tektronix_4000 import DPO4000_visa

class Auto_dc_loding():
    def __init__(self):
        self.PW_VISA_ADDRESS = None
        self.LD_VISA_ADDRESS = None
        self.scope = None

        self.Voltage = None

        self.Imax = None
        self.CurrDynH = None
        self.CurrDynL = None

    def PW_setup(self, voltage):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.PW_VISA_ADDRESS
        self.scope.connect()
        
        info = self.scope.do_query("*IDN?")
        print("DC Power supply Name : " + info)
        
        self.scope.do_command("VOLTage " + str(voltage))
        
        self.scope.do_command("OUTP ON")
        self.scope.close()

    def LD_setup(self, mode):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.LD_VISA_ADDRESS
        self.scope.connect()

        info = self.scope.do_query("*IDN?")
        print("DC Electronic loads Name : " + info)

        if str(mode) == "0":
            cmd_list = ["*RST", "SHOW L" , "MODE CCH", "CURR:STAT:L1 "+str(self.CurrDynH) ]

        elif str(mode) == "1":
            cmd_list = ["*RST" , "SHOW L", "MODE CCDH",
                "CURR:DYN:L1 "+str(self.CurrDynH), "CURR:DYN:L2 "+str(self.CurrDynL),
                "CURR:DYN:RISE 0.25", "CURR:DYN:FALL 0.25",
                "CURR:DYN:T1 0.5", "CURR:DYN:T2 0.5"]

        for cmd in cmd_list :
            self.scope.do_command(cmd)
    
        self.scope.do_command("LOAD ON")
        self.scope.close()
    
    def get_Eff(self):
        result_tmp = []
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.PW_VISA_ADDRESS
        self.scope.connect()

        pw_votg = self.scope.do_query("MEAS:VOLT?") #MEAS:VOLT?
        print("Power supply Voltage : "+ str(pw_votg) +"V") #MEAS:CURR?
        pw_CURRent = self.scope.do_query("MEAS:CURR?")
        print("Power supply CURRent : "+ str(pw_CURRent) +"A")
        self.scope.close()

        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.LD_VISA_ADDRESS
        self.scope.connect()

        load_votg = self.scope.do_query("MEAS:VoLT?")
        print("Electronic loads Voltage : "+ str(load_votg) +"V")
        load_CURRent = self.scope.do_query("MEAS:CURRent?")
        print("Electronic loads CURRent : "+ str(load_CURRent) +"A")
        self.scope.close()

        pw = (float(load_votg)*float(load_CURRent))/(float(pw_votg)*float(pw_CURRent))
        pw = str(pw*100)+"%"
        print("Power Efficiency : " + pw)
        result_tmp = [float(pw_votg), float(pw_CURRent), float(load_votg), float(load_CURRent), pw]
        return result_tmp

    def start(self, model):
        if model == "Regulation":
            switch = 0
        elif model == "Load":
            switch = 1

        self.PW_setup(self.Voltage)
        self.LD_setup(switch)



