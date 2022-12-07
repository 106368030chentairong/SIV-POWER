from lib.Thread_line_trigger import line_trigger

model = line_trigger()
model.VISA_ADDRESS = "USB0::0x0699::0x0405::C022392::INSTR"
model.main()