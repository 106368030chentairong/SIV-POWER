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
        except Exception as e:
            if self.break_num < 3:
                self.break_num +=1
                time.sleep(3)
                logging.error(self.VISA_ADDRESS + "- Reconnect Waiting 3s ...("+str(self.break_num)+"/3)")
                self.connect()
            else:
                print(e)
                logging.error(self.VISA_ADDRESS + " - Not Connected !")
                

    def do_command(self, command):
        try:
            time.sleep(0.1)
            self.KsInfiniiumScope.write("%s" % command)
            logging.info(command + " - Execute the Command Successfully ")
        except Exception as e: 
            print(e)
            logging.error(command + " - Execute the Command Faill !")
    
    def do_query(self, command):
        try:
            time.sleep(0.1)
            logging.info(command + " - Execute the Command Successfully ")
            return self.KsInfiniiumScope.query("%s" % command).strip()
        except Exception as e: 
            print(e)
            logging.error(command + " - Execute the Command Faill !")

    def get_raw(self):
        try:
            time.sleep(0.1)
            self.do_command('CURVE?')
            logging.info("CURVE? - Execute the Command Successfully ")
            return self.KsInfiniiumScope.read_raw()
        except Exception as e: 
            print(e)
            logging.error("CURVE? - Execute the Command Faill !")

    
    def read_raw(self):
        try:
            time.sleep(0.1)
            return self.KsInfiniiumScope.read_raw()
        except Exception as e: 
            print(e)
            logging.error("read_raw() - Execute the Command Faill !")

    def close(self):
        try:
            time.sleep(0.1)
            self.KsInfiniiumScope.close()
            self.rm.close()
        except Exception as e: 
            print(e)
            logging.error('Close error')
