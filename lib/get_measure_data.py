import time
from lib.tektronix_4000 import DPO4000_visa

class get_measure_data():
    def __init__(self):
        self.VISA_ADDRESS = None
        self.scope = None

        self.channel_list = [1,1,1,1,2,2,3,3]
        self.MEASUrement_Type = ["MAXimum","MINImum","RMS","pk2pk","MAXimum","MINImum","MAXimum", "MINImum"]

    def add_measurement(self):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()

        for i in range(8):
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':STATE OFF')
        for i in range(len(self.MEASUrement_Type)):
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':SOURCE1 CH'+str(self.channel_list[i]))
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':TYPe '+ self.MEASUrement_Type[i])
            self.scope.do_command('MEASUrement:MEAS'+str(i+1)+':STATE ON')
        self.scope.close()
    
    def get_value(self):
        self.scope = DPO4000_visa()
        self.scope.VISA_ADDRESS = self.VISA_ADDRESS
        self.scope.connect()

        time.sleep(5)
        result_tmp = []
        for i in range(len(self.MEASUrement_Type[:4])):
            value = float(self.scope.do_query('MEASUrement:MEAS'+str(i+1)+':VALue?'))
            result_tmp.append(value)
        
        self.scope.close()
        return result_tmp
