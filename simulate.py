"""
depends on cansend from the can-utils package
"""

import subprocess
import struct
import binascii
import time

candevice = 'can0'
cansend = '/usr/local/bin/cansend'
pressurefmt = '<H'

pressure_id=200 #512
flap_id= 208 #520

def send_can(id, payload):
	canmessage = '%s#%s' % (id, payload)
	print(canmessage)
	subprocess.call([cansend, candevice, canmessage])


def send_pressure(amount):
	payload = struct.pack(pressurefmt, amount)
	payload = binascii.hexlify(payload)
	send_can(pressure_id, payload)


for i in range(0,16000,50):
	print(i)
	send_pressure(i)
	time.sleep(0.5)
	#send_can(flap_id, payload)
