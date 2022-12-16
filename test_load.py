import os, sys, time

from lib.Auto_trig import Auto_trig
from lib.Auto_dc_loading import Auto_dc_loding
from lib.get_measure_data import get_measure_data

load_scope = Auto_dc_loding()
load_scope.PW_VISA_ADDRESS = "GPIB0::5::INSTR"
load_scope.LD_VISA_ADDRESS = "GPIB0::7::INSTR"
load_scope.Voltage   = 4.2
load_scope.CurrDynH  = 0.5
load_scope.CurrDynL  = 0.1
load_scope.start("Load")

# Auto trig
auto_scope = Auto_trig()
auto_scope.VISA_ADDRESS = "USB0::0x0699::0x0405::C022392::INSTR"
auto_scope.setup("10E+3")
auto_scope.Auto_cale(1, 3)
auto_scope.Auto_cale(2, 2) 
auto_scope.Auto_cale(3, 2) 
auto_scope.start("Load")


