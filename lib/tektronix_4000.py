import time
import pyvisa as visa

class DPO4000_visa():
    def __init__(self):
        self.KsInfiniiumScope = None
        self.VISA_ADDRESS = None
        self.break_num = 0
        self.GLOBAL_TOUT = 10000

    def connect(self):
        try:
            self.rm = visa.ResourceManager()
            self.KsInfiniiumScope = self.rm.open_resource(self.VISA_ADDRESS)
            self.KsInfiniiumScope.timeout = self.GLOBAL_TOUT
            #self.KsInfiniiumScope.clear()
            self.break_num = 0
        except Exception:
            if self.break_num <= 3:
                self.break_num +=1
                time.sleep(5)
                #logging.info("Reconnect Waiting 5s ...")
                print("Reconnect Waiting 5s ...")
                self.connect()
            else:
                #logging.error(self.VISA_ADDRESS + " - Oscilloscope Connect Error !")
                print(self.VISA_ADDRESS + " - Oscilloscope Connect Error !")
                pass

    def do_command(self, command):
        try:
            self.KsInfiniiumScope.write("%s" % command)
        except Exception: 
            print(command + " - Write Command Error !")
            pass
    
    def do_query(self, command):
        try:
            return self.KsInfiniiumScope.query("%s" % command).strip()
        except Exception: 
            try:
                print(command + " - Query Command Error !")
            except NameError:
                print(command + " - Query Command Error !")
            pass

    def get_raw(self):
        try:
            self.do_command('CURVE?')
            return self.KsInfiniiumScope.read_raw()
        except Exception: 
            pass
    
    def read_raw(self):
        try:
            return self.KsInfiniiumScope.read_raw()
        except Exception: 
            pass

    def close(self):
        try:
            self.KsInfiniiumScope.close()
            self.rm.close()
        except Exception as e:
            print(e)