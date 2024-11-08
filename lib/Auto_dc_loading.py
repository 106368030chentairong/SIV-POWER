from lib.tektronix_4000 import DPO4000_visa
import logging

class Auto_dc_loding():
    def __init__(self):
        # Visa function settings
        self.PW_VISA_ADDRESS = None
        self.LD_VISA_ADDRESS = None
        self.scope = None

        # Measurement values settings 
        self.Voltage = None
        self.CurrDynH = None
        self.CurrDynL = None

    def PW_setup(self, voltage):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.PW_VISA_ADDRESS
        self.scope.connect()
        
        info = self.scope.do_query("*IDN?")
        logging.info("DC Power supply Name : " + info)
        
        self.scope.do_command("VOLTage " + str(voltage))
        
        self.scope.do_command("OUTP ON")
        self.scope.close()

    def LD_setup(self, mode):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.LD_VISA_ADDRESS
        self.scope.connect()

        info = self.scope.do_query("*IDN?")
        logging.info("DC Electronic loads Name : " + info)

        if str(mode) == "0":
            cmd_list = ["*RST", "SHOW L" , "MODE CCH", "CURR:STAT:L1 "+str(self.CurrDynH) ]

        elif str(mode) == "1":
            cmd_list = ["*RST" , "SHOW L", "MODE CCDL",
                "CURR:DYN:L1 "+str(self.CurrDynH), "CURR:DYN:L2 "+str(self.CurrDynL),
                "CURR:DYN:RISE 0.25", "CURR:DYN:FALL 0.25",
                "CURR:DYN:T1 0.5E-3", "CURR:DYN:T2 0.5E-3"]
                
        # CCDL RISE:250mA/us FALL 250mA/us T1:0.5ms T2:0.5ms
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
        logging.info("Power supply Voltage : "+ str(pw_votg) +"V") #MEAS:CURR?
        pw_CURRent = self.scope.do_query("MEAS:CURR?")
        logging.info("Power supply CURRent : "+ str(pw_CURRent) +"A")
        self.scope.close()

        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.LD_VISA_ADDRESS
        self.scope.connect()

        load_votg = self.scope.do_query("MEAS:VoLT?")
        logging.info("Electronic loads Voltage : "+ str(load_votg) +"V")
        load_CURRent = self.scope.do_query("MEAS:CURRent?")
        logging.info("Electronic loads CURRent : "+ str(load_CURRent) +"A")
        self.scope.close()

        pw = (float(load_votg)*float(load_CURRent))/(float(pw_votg)*float(pw_CURRent))*100
        pw = ("%.2f" % pw)
        logging.info("Power Efficiency : " + pw)
        result_tmp = [float(pw_votg), float(pw_CURRent), float(load_votg), float(load_CURRent), pw]
        return result_tmp

    def start(self, model):
        if model == "Regulation":
            switch = 0
        elif model == "Load":
            switch = 1

        self.PW_setup(self.Voltage)
        self.LD_setup(switch)



