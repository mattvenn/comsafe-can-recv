from pyusbtin.usbtin import USBtin
import re
import os
import struct
from pyusbtin.canmessage import CANMessage
import time
import threading

pressure_id = 512
flap_id = 520
pressure_fmt = '<H'
pressure = 0
flap = 0
status_id = 500
status_fmt = '<HH'

def log_data(msg):
    global pressure
    if msg.get_id() == pressure_id:
        raw = chr(msg.get_data()[0]) + chr(msg.get_data()[1])
        pressure, = struct.unpack(pressure_fmt, raw)
        print("pressure = %d" % pressure)

    if msg.get_id() == flap_id:
        print("flap",  msg.get_data())
        flap = 0

"""
print("starting can message listener")
usbtin = USBtin()
usbtin.connect("/dev/ttyACM0")
usbtin.add_message_listener(log_data)
usbtin.open_can_channel(500000, USBtin.ACTIVE)
"""

"""
everytime a read is made on the named pipe, write the current pressure value
"""
class PressureWriter(threading.Thread):

    def __init__(self):
        super(PressureWriter, self).__init__()
        self.named_pipe = '/tmp/pressure'
        try:
            os.mkfifo(self.named_pipe)
        except OSError: # file exists
            pass

    def run(self):
        print("starting pipe writer loop")
        while True:
            try:
                with open(self.named_pipe, 'w') as fh:
                    fh.write(str(pressure))
            except IOError: # if reader has closed before/during write then get a pipe error
                print("ioerror")
            time.sleep(0.01) # wait a bit to make sure that the reader has closed the pipe

""" 
monitor the alarm named pipe, and send can messages for status
"""
class AlarmReader(threading.Thread):

    def __init__(self):
        super(AlarmReader, self).__init__()
        self.named_pipe = '/tmp/alarm'
        try:
            os.mkfifo(self.named_pipe)
        except OSError: # file exists
            pass

    def run(self):
        print("starting alarm monitor")
        while True:
            try:
                with open(self.named_pipe, 'r') as fh:
                    for alarm_status in fh.readlines():
                        print(alarm_status)
                        m = re.search('alarm:(\d+) severity:(\d+)', alarm_status)
                        if m is not None:
                            alarm = int(m.group(1))
                            severity = int(m.group(2))
                            print(alarm, severity)
                            can_msg = struct.pack(status_fmt, alarm, severity)
                            usbtin.send(CANMessage(status_id, can_msg)
            except IOError: # if writer has closed before/during write then get a pipe error
                print("ioerror")

thread = PressureWriter()
thread.daemon = True
thread.start()
thread = AlarmReader()
thread.daemon = True
thread.start()

while True:
    time.sleep(1)
