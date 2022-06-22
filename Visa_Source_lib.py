# @ Agilent Technologies Model 66319B/D
# @ Mobile Communications Dc Source lib
# Using visa contact information from the database



import time
import os

import pyvisa as visa

class Visa_Source_lib():
    def __init__(self):
        self.KsInfiniiumScope = None
        self.VISA_ADDRESS = None
        self.GLOBAL_TOUT = 10000
        self.ts = None
        self.timestamp = None
        self.FReq = None
        self.break_num = 0

    def do_command(self, command):
        try:
            time.sleep(0.1)
            self.KsInfiniiumScope.write("%s" % command)
        except Exception: 
            print(command + " - Write Command Error !")
            #print(command + " - Write Command Error !")
            pass
    
    def do_query_string(self, command):
        try:
            return self.KsInfiniiumScope.query("%s" % command)
        except Exception: 
            print(command + " - Query Command Error !")
            #print(command + " - Query Command Error !")
            pass

    def do_query_ieee_block(self,command):
        try:
            return self.KsInfiniiumScope.query_binary_values("%s" % command, datatype='s', container=bytes)
        except Exception: 
            print(command + " - RAW Data Download Error !")
            #print(command + " - RAW Data Download Error !")
            pass

    def connect(self):
        try:
            self.rm = visa.ResourceManager()
            self.KsInfiniiumScope = self.rm.open_resource(self.VISA_ADDRESS)
            self.KsInfiniiumScope.timeout = self.GLOBAL_TOUT
            self.KsInfiniiumScope.clear()
            self.break_num = 0
        except Exception:
            if self.break_num <= 2:
                self.break_num +=1
                time.sleep(5)
                print("Reconnect Waiting 5s ... ("+str(self.break_num)+"/3)")
                self.connect()
            else:
                print(self.VISA_ADDRESS + " - Connect Error !")
            pass