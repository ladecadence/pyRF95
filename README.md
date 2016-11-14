# pyRF95

HopeRF RF95 (and similar LoRa modules) python library

Based in RadioHead library code: http://www.airspayce.com/mikem/arduino/RadioHead/

## Installation

Just import rf95 module in your python project

## Use

When creating the RF95 object, you need to pass the CS channel (On Raspberry Pi you have spidev 0 and 1 devices) and the external interrupt pin (Broadcom GPIO).

Then you can set channel, TX Power, and predefined modes of operation:

* Bw125Cr45Sf128 : Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on. Default medium range.
* Bw500Cr45Sf128 : Bw = 500 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on. Fast+short range.
* Bw31_25Cr48Sf512 : Bw = 31.25 kHz, Cr = 4/8, Sf = 512chips/symbol, CRC on. Slow+long range.
* Bw125Cr48Sf4096 : Bw = 125 kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on. Slow+long range. 

### Example

```python
import rf95

# Create rf95 object with CS0 and external interrupt on pin 25
rf95 = RF95(0, 25)

if not rf95.init(): # returns True if found
	print("RF95 not found")
	quit(1)
else:
	print("RF95 LoRa mode ok")

# set frequency, power and mode
rf95.set_frequency(868.5)
rf95.set_tx_power(5)
rf95.set_modem_config(Bw31_25Cr48Sf512)

# Send some data
rf95.send([0x00, 0x01, 0x02, 0x03])
rf95.wait_packet_sent()
# Send a string
rf95.send(rf95.str_to_data("$TELEMETRY TEST"))
rf95.wait_packet_sent()

# Wait until data is available 
while not rf95.available():
	pass
# Receive
data = rf95.recv()
print (data)
for i in data:
	print(chr(i), end="")
print()
rf95.set_mode_idle()
```

