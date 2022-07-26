import os, sys, time

from lib.Auto_trig import Auto_trig
from lib.Auto_dc_loading import Auto_dc_loding
from lib.get_measure_data import get_measure_data

# Auto trig
auto_scope = Auto_trig()
auto_scope.start("Line")
auto_scope.VISA_ADDRESS = "USB0::0x0699::0x0405::C022392::INSTR"

load_scope = Auto_dc_loding()
load_scope.PW_VISA_ADDRESS = "GPIB0::5::INSTR"
load_scope.LD_VISA_ADDRESS = "GPIB0::7::INSTR"

# setup Hight level
load_scope.PW_setup(3.7)

# Setup loading Curr
load_scope.CurrDynH  = "1000mA"
load_scope.LD_setup(0)

time.sleep(1)
load_scope.get_Eff()