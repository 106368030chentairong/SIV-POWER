import time
import logging
from urllib import response
import pyvisa as visa

from lib.logcolors import bcolors

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
            logging.info(self.VISA_ADDRESS + "- Connected ")
        except Exception:
            if self.break_num < 3:
                self.break_num +=1
                time.sleep(3)
                logging.error(self.VISA_ADDRESS + "- Reconnect Waiting 3s ...("+str(self.break_num)+"/3)")
                self.connect()
            else:
                logging.error(self.VISA_ADDRESS + " - Not Connected !")
                pass

    def do_command(self, command):
        try:
            self.KsInfiniiumScope.write("%s" % command)
            logging.info(command + " - Execute the Command Successfully ")
        except Exception: 
            logging.error(command + " - Execute the Command Faill !")
            pass
    
    def do_query(self, command):
        try:
            response = self.KsInfiniiumScope.query("%s" % command).strip()
            logging.info(command + " - Execute the Command Successfully ")
            return response
        except Exception: 
            logging.error(command + " - Execute the Command Faill !")
            pass

    def get_raw(self):
        try:
            self.do_command('CURVE?')
            logging.info("CURVE? - Execute the Command Successfully ")
            return self.KsInfiniiumScope.read_raw()
        except Exception: 
            logging.error("CURVE? - Execute the Command Faill !")
            pass
    
    def read_raw(self):
        try:
            return self.KsInfiniiumScope.read_raw()
        except Exception: 
            logging.error("read_raw() - Execute the Command Faill !")
            pass

    def close(self):
        try:
            self.KsInfiniiumScope.close()
            self.rm.close()
        except Exception as e:
            logging.error('Close error')
