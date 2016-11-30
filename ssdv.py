#!/usr/bin/env python3
import rf95
import sys
import os
import time

# check arguments
if len(sys.argv) < 2:
	print ("Need a SSDV binary file")
	exit(1)

# open SSDV file
ssdv_filename = sys.argv[1]
try:
    ssdv_file = open(ssdv_filename, "rb")
except IOError as e:
    print ("Could not open the file")
    print ("I/O error({0}): {1}".format(e.errno, e.strerror))
    exit(1)

if os.path.getsize(ssdv_filename)/256 != 0:
    print ("File does not look like a SSDV image")
    exit(1)

# ok, get number of packets to send
ssdv_packets = os.path.getsize(ssdv_filename)//256

# Create rf95 object with CS0 and external interrupt on pin 25
lora = rf95.RF95(0, 25)

if not lora.init(): # returns True if found
    print("RF95 not found")
    quit(1)
else:
    print("RF95 LoRa mode ok")

# set frequency, power and mode
lora.set_frequency(868.5)
lora.set_tx_power(5)

# Send ssdv packets
# We are ignoring the first sync byte of each packet
# as the rf95 packet payload size is just 255 bytes.
# We need to take this into account on the receive side.
for i in range(ssdv_packets):
	ssdv_file.seek((i*256)+1, 0)
	lora.send(lora.bytes_to_data(ssdv_file.read(255)))
	print("Sent packet" + str(i))
	time.sleep(0.5)                 # processing time
# Done
lora.set_mode_idle()
ssdv_file.close()

