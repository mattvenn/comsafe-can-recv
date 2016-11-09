from pyusbtin.usbtin import USBtin
import struct
from pyusbtin.canmessage import CANMessage
from time import sleep

pressure_id = 512
flap_id = 520
pressure_fmt = '<H'
pressure = 0
flap = 0

def log_data(msg):
    global pressure
    if msg.get_id() == pressure_id:
        raw = chr(msg.get_data()[0]) + chr(msg.get_data()[1])
        pressure, = struct.unpack(pressure_fmt, raw)
        print("pressure = %d" % pressure)

    if msg.get_id() == flap_id:
        print("flap",  msg.get_data())
        flap = 0

print("starting can message listener")
usbtin = USBtin()
usbtin.connect("/dev/ttyACM1")
usbtin.add_message_listener(log_data)
usbtin.open_can_channel(500000, USBtin.ACTIVE)

print("starting pipe writer loop")
while True:
    try:
        with open('pressure', 'w') as fh:
            fh.write(str(pressure))
    except IOError: # if reader has closed before/during write then get a pipe error
        print("ioerror")
    sleep(0.01) # wait a bit to make sure that the reader has closed the pipe

