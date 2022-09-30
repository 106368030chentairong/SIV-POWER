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

def L2H():
    # setup Hight level
    load_scope.PW_setup(3.7)

    # Setup loading Curr
    load_scope.CurrDynH  = "100mA"
    load_scope.LD_setup(0)

    # Setup Trig level
    auto_scope.setup_trig("4" , "RISe") #  {RISe|FALL}

    # setup Low level
    time.sleep(2)
    load_scope.PW_setup(4.2)

def H2L():
    # setup Hight level
    load_scope.PW_setup(4.2)

    # Setup loading Curr
    load_scope.CurrDynH  = "100mA"
    load_scope.LD_setup(0)

    # Setup Trig level
    auto_scope.setup_trig("4" , "FALL") #  {RISe|FALL}

    # setup Low level
    time.sleep(2)
    load_scope.PW_setup(3.7)

if sys.argv[1] == "0":
    L2H()
elif sys.argv[1] == "1":
    H2L()