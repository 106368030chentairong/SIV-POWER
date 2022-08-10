from lib.tektronix_4000 import DPO4000_visa

class get_info():
    def __init__(self):
        self.TK_VISA_ADDRESS = None
        self.PW_VISA_ADDRESS = None
        self.LD_VISA_ADDRESS = None

        self.TK_device_name = None
        self.PW_device_name = None
        self.LD_device_name = None
    
    def run(self):
        try:
            self.scope_TK = DPO4000_visa()
            self.scope_TK.VISA_ADDRESS = self.TK_VISA_ADDRESS
            self.scope_TK.connect()
            self.TK_device_name = self.scope_TK.do_query("*IDN?")
            if self.TK_device_name != None:
                self.scope_TK.close()

            self.scope_PW = DPO4000_visa()
            self.scope_PW.VISA_ADDRESS = self.PW_VISA_ADDRESS
            self.scope_PW.connect()
            self.PW_device_name = self.scope_PW.do_query("*IDN?")
            if self.PW_device_name != None:
                self.scope_PW.close()
            
            self.scope_LD = DPO4000_visa()
            self.scope_LD.VISA_ADDRESS = self.LD_VISA_ADDRESS
            self.scope_LD.connect()
            self.LD_device_name = self.scope_LD.do_query("*IDN?")
            if self.LD_device_name != None:
                self.scope_LD.close()

            return [self.TK_device_name,self.PW_device_name, self.LD_device_name]

        except Exception:
            return [self.TK_device_name,self.PW_device_name, self.LD_device_name]
