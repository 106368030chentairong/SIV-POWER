import os, sys, time

from lib.Auto_trig import Auto_trig
from lib.Auto_dc_loading import Auto_dc_loding
from lib.get_measure_data import get_measure_data



load_scope = Auto_dc_loding()
load_scope.PW_VISA_ADDRESS = "GPIB0::5::INSTR"
load_scope.LD_VISA_ADDRESS = "GPIB0::7::INSTR"

Voltage_1 = 4.75
Voltage_2 = 5.25
CurrDynH = "0.5"
def L2H():
    # setup Hight level
    load_scope.PW_setup(Voltage_1)

    # Setup loading Curr
    load_scope.CurrDynH  = CurrDynH
    load_scope.LD_setup(0)


    # Auto trig
    auto_scope = Auto_trig()
    auto_scope.VISA_ADDRESS = "USB0::0x0699::0x0405::C022392::INSTR"
    auto_scope.start("Line")
    auto_scope.Auto_cale(1, 1.5)
    auto_scope.Auto_cale(3, 1)

    # Setup Trig level
    auto_scope.setup_trig(Voltage_1 , Voltage_2) #  {RISe|FALL}

    # setup Low level
    time.sleep(2)
    load_scope.PW_setup(Voltage_2)

def H2L():
    # setup Hight level
    load_scope.PW_setup(Voltage_2)

    # Setup loading Curr
    load_scope.CurrDynH  = CurrDynH
    load_scope.LD_setup(0)

    # Auto trig
    auto_scope = Auto_trig()
    auto_scope.VISA_ADDRESS = "USB0::0x0699::0x0405::C022392::INSTR"
    auto_scope.start("Line")
    auto_scope.Auto_cale(1, 1)
    auto_scope.Auto_cale(3, 0.1)

    # Setup Trig level
    auto_scope.setup_trig(Voltage_2 , Voltage_1) #  {RISe|FALL}

    # setup Low level
    time.sleep(2)
    load_scope.PW_setup(Voltage_1)

if sys.argv[1] == "0":
    L2H()
elif sys.argv[1] == "1":
    H2L()