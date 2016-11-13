#!/usr/bin/env python3

# (C) 2016 David Pello Gonzalez for ASHAB
# Based on code from the RadioHead Library:
# http://www.airspayce.com/mikem/arduino/RadioHead/
#
# This program is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  
# If not, see <http://www.gnu.org/licenses/>.

import time
import sys
import spidev
import RPi.GPIO as GPIO

FXOSC=32000000
FSTEP = FXOSC / 524288

# Register names (LoRa Mode, from table 85)
REG_00_FIFO=0x00
REG_01_OP_MODE=0x01
REG_02_RESERVED=0x02
REG_03_RESERVED=0x03
REG_04_RESERVED=0x04
REG_05_RESERVED=0x05
REG_06_FRF_MSB=0x06
REG_07_FRF_MID=0x07
REG_08_FRF_LSB=0x08
REG_09_PA_CONFIG=0x09
REG_0A_PA_RAMP=0x0a
REG_0B_OCP=0x0b
REG_0C_LNA=0x0c
REG_0D_FIFO_ADDR_PTR=0x0d
REG_0E_FIFO_TX_BASE_ADDR=0x0e
REG_0F_FIFO_RX_BASE_ADDR=0x0f
REG_10_FIFO_RX_CURRENT_ADDR=0x10
REG_11_IRQ_FLAGS_MASK=0x11
REG_12_IRQ_FLAGS=0x12
REG_13_RX_NB_BYTES=0x13
REG_14_RX_HEADER_CNT_VALUE_MSB=0x14
REG_15_RX_HEADER_CNT_VALUE_LSB=0x15
REG_16_RX_PACKET_CNT_VALUE_MSB=0x16
REG_17_RX_PACKET_CNT_VALUE_LSB=0x17
REG_18_MODEM_STAT=0x18
REG_19_PKT_SNR_VALUE=0x19
REG_1A_PKT_RSSI_VALUE=0x1a
REG_1B_RSSI_VALUE=0x1b
REG_1C_HOP_CHANNEL=0x1c
REG_1D_MODEM_CONFIG1=0x1d
REG_1E_MODEM_CONFIG2=0x1e
REG_1F_SYMB_TIMEOUT_LSB=0x1f
REG_20_PREAMBLE_MSB=0x20
REG_21_PREAMBLE_LSB=0x21
REG_22_PAYLOAD_LENGTH=0x22
REG_23_MAX_PAYLOAD_LENGTH=0x23
REG_24_HOP_PERIOD=0x24
REG_25_FIFO_RX_BYTE_ADDR=0x25
REG_26_MODEM_CONFIG3=0x26
REG_28_FREQ_ERROR=0x28
REG_31_DETECT_OPT=0x31
REG_37_DETECTION_THRESHOLD=0x37

REG_40_DIO_MAPPING1=0x40
REG_41_DIO_MAPPING2=0x41
REG_42_VERSION=0x42

REG_4B_TCXO=0x4b
REG_4D_PA_DAC=0x4d
REG_5B_FORMER_TEMP=0x5b
REG_61_AGC_REF=0x61
REG_62_AGC_THRESH1=0x62
REG_63_AGC_THRESH2=0x63
REG_64_AGC_THRESH3=0x64

# REG_01_OP_MODE                             0x01
LONG_RANGE_MODE=0x80
ACCESS_SHARED_REG=0x40
MODE=0x07
MODE_SLEEP=0x00
MODE_STDBY=0x01
MODE_FSTX=0x02
MODE_TX=0x03
MODE_FSRX=0x04
MODE_RXCONTINUOUS=0x05
MODE_RXSINGLE=0x06
MODE_CAD=0x07

# REG_09_PA_CONFIG                           0x09
PA_SELECT=0x80
MAX_POWER=0x70
OUTPUT_POWER=0x0f

# REG_0A_PA_RAMP                             0x0a
LOW_PN_TX_PLL_OFF=0x10
PA_RAMP=0x0f
PA_RAMP_3_4MS=0x00
PA_RAMP_2MS=0x01
PA_RAMP_1MS=0x02
PA_RAMP_500US=0x03
PA_RAMP_250US=0x0
PA_RAMP_125US=0x05
PA_RAMP_100US=0x06
PA_RAMP_62US=0x07
PA_RAMP_50US=0x08
PA_RAMP_40US=0x09
PA_RAMP_31US=0x0a
PA_RAMP_25US=0x0b
PA_RAMP_20US=0x0c
PA_RAMP_15US=0x0d
PA_RAMP_12US=0x0e
PA_RAMP_10US=0x0f

# REG_0B_OCP                                 0x0b
OCP_ON=0x20
OCP_TRIM=0x1f

# REG_0C_LNA                                 0x0c
LNA_GAIN=0xe0
LNA_BOOST=0x03
LNA_BOOST_DEFAULT=0x00
LNA_BOOST_150PC=0x11

# REG_11_IRQ_FLAGS_MASK                      0x11
RX_TIMEOUT_MASK=0x80
RX_DONE_MASK=0x40
PAYLOAD_CRC_ERROR_MASK=0x20
VALID_HEADER_MASK=0x10
TX_DONE_MASK=0x08
CAD_DONE_MASK=0x04
FHSS_CHANGE_CHANNEL_MASK=0x02
CAD_DETECTED_MASK=0x01

# REG_12_IRQ_FLAGS                           0x12
RX_TIMEOUT=0x80
RX_DONE=0x40
PAYLOAD_CRC_ERROR=0x20
VALID_HEADER=0x10
TX_DONE=0x08
CAD_DONE=0x04
FHSS_CHANGE_CHANNEL=0x02
CAD_DETECTED=0x01

# REG_18_MODEM_STAT                          0x18
RX_CODING_RATE=0xe0
MODEM_STATUS_CLEAR=0x10
MODEM_STATUS_HEADER_INFO_VALID=0x08
MODEM_STATUS_RX_ONGOING=0x04
MODEM_STATUS_SIGNAL_SYNCHRONIZED=0x02
MODEM_STATUS_SIGNAL_DETECTED=0x01

# REG_1C_HOP_CHANNEL                         0x1c
PLL_TIMEOUT=0x80
RX_PAYLOAD_CRC_IS_ON=0x40
FHSS_PRESENT_CHANNEL=0x3f

# REG_1D_MODEM_CONFIG1                       0x1d
BW=0xc0
BW_125KHZ=0x00
BW_250KHZ=0x40
BW_500KHZ=0x80
BW_RESERVED=0xc0
CODING_RATE=0x38
CODING_RATE_4_5=0x00
CODING_RATE_4_6=0x08
CODING_RATE_4_7=0x10
CODING_RATE_4_8=0x18
IMPLICIT_HEADER_MODE_ON=0x04
RX_PAYLOAD_CRC_ON=0x02
LOW_DATA_RATE_OPTIMIZE=0x01

# REG_1E_MODEM_CONFIG2                       0x1e
SPREADING_FACTOR=0xf0
SPREADING_FACTOR_64CPS=0x60
SPREADING_FACTOR_128CPS=0x70
SPREADING_FACTOR_256CPS=0x80
SPREADING_FACTOR_512CPS=0x90
SPREADING_FACTOR_1024CPS=0xa0
SPREADING_FACTOR_2048CPS=0xb0
SPREADING_FACTOR_4096CPS=0xc0
TX_CONTINUOUS_MOE=0x08
AGC_AUTO_ON=0x04
SYM_TIMEOUT_MSB=0x03

# REG_4D_PA_DAC                              0x4d
PA_DAC_DISABLE=0x04
PA_DAC_ENABLE=0x07

MAX_MESSAGE_LEN=255

# default params
Bw125Cr45Sf128 = (0x72,   0x74,    0x00)
Bw500Cr45Sf128 = (0x92,   0x74,    0x00)
Bw31_25Cr48Sf512 = (0x48,   0x94,    0x00)
Bw125Cr48Sf4096 = (0x78,   0xc4,    0x00)

# SPI
SPI_WRITE_MASK=0x80

# Modes
RHModeInitialising=0
RHModeSleep=1
RHModeIdle=2
RHModeTx=3
RHModeRx=4
RHModeCad=5

class RF95:
	def __init__(self, cs=0, int_pin=25):
		# init class
		self.spi = spidev.SpiDev()
		self.cs = cs
		self.int_pin = int_pin
		self.mode = RHModeInitialising
		self.buf=[] 		# RX Buffer for interrupts
		self.buflen=0 		# RX Buffer length
		self.last_rssi=-99 	# last packet RSSI
		self.rx_bad = 0 	# rx error count
		self.tx_good = 0 	# tx packets sent
	
	def init(self):
		# open SPI and initialize RF95
		self.spi.open(0,self.cs)
		self.spi.max_speed_hz = 488000
		self.spi.close()

		# set interrupt pin
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.int_pin, GPIO.IN)
		GPIO.add_event_detect(self.int_pin, GPIO.RISING, callback=self.handle_interrupt)

		# set sleep mode and LoRa mode
		self.spi_write(REG_01_OP_MODE, MODE_SLEEP | LONG_RANGE_MODE)
		
		time.sleep(0.01)		
		# check if we are set
		if self.spi_read(REG_01_OP_MODE) != (MODE_SLEEP | LONG_RANGE_MODE):
			return False

		# set up FIFO
		self.spi_write(REG_0E_FIFO_TX_BASE_ADDR, 0)
		self.spi_write(REG_0F_FIFO_RX_BASE_ADDR, 0)

		# default mode
		self.set_mode_idle()

		self.set_modem_config(Bw125Cr45Sf128)
		self.set_preamble_length(8)
		
		return True

	def handle_interrupt(self, channel):
		# Read the interrupt register
		irq_flags = self.spi_read(REG_12_IRQ_FLAGS)

		if self.mode == RHModeRx and irq_flags & (RX_TIMEOUT | PAYLOAD_CRC_ERROR):
			self.rx_bad = self.rx_bad + 1
		elif self.mode == RHModeRx and irq_flags & RX_DONE:
			# packet received
			length = self.spi_read(REG_13_RX_NB_BYTES)
			# Reset the fifo read ptr to the beginning of the packet
			self.spi_write(REG_0D_FIFO_ADDR_PTR, self.spi_read(REG_10_FIFO_RX_CURRENT_ADDR))
			self.buf = self.spi_read_data(REG_00_FIFO, lenght)
			self.buflen = lenght
			# clear IRQ flags
			self.spi_write(REG_12_IRQ_FLAGS, 0xff)

			# save RSSI
			self.last_rssi = self.spi_read(REG_1A_PKT_RSSI_VALUE) - 137
			# We have received a message
			self.set_mode_idle()

		elif self.mode == RHModeTx and irq_flags & TX_DONE:
			self.tx_good = self.tx_good + 1
			self.set_mode_idle()
		elif self.mode == RHModeCad and irq_flags & CAD_DONE:
			self.cad = irq_flags & CAD_DETECTED
			self.set_mode_idle()
    
		self.spi_write(REG_12_IRQ_FLAGS, 0xff) # Clear all IRQ flags



	def spi_write(self, reg, data):
		self.spi.open(0,self.cs)
		# transfer one byte
		self.spi.xfer2([reg | SPI_WRITE_MASK, data])
		self.spi.close()

	def spi_read(self, reg):
		self.spi.open(0,self.cs)
		data = self.spi.xfer2([reg & ~SPI_WRITE_MASK, 0])
		self.spi.close()
		return data[1]

	def spi_write_data(self, reg, data):
		self.spi.open(0, self.cs)
		# transfer byte list
		self.spi.xfer2([reg | SPI_WRITE_MASK])
		self.spi.xfer2(data)
		self.spi.close()

	def spi_read_data(self, reg, length):
		data = []
		self.spi.open(0, self.cs)
		# start address
		self.spi.xfer2([reg & ~SPI_WRITE_MASK])
		while lenght:
			data = data + self.spi.xfer2([0])
			length = length - 1
		self.spi.close()
		return data

	def set_frequency(self, freq):
		freq_value = int((freq * 1000000.0) / FSTEP)
		
		self.spi_write(REG_06_FRF_MSB, (freq_value>>16)&0xff)
		self.spi_write(REG_07_FRF_MID, (freq_value>>8)&0xff)
		self.spi_write(REG_08_FRF_LSB, (freq_value)&0xff)
	
	def set_mode_idle(self):
		if self.mode != RHModeIdle:
			self.spi_write(REG_01_OP_MODE, MODE_STDBY)
			self.mode = RHModeIdle

	def sleep(self):
		if self.mode != RHModeSleep:
			self.spi_write(REG_01_OP_MODE, MODE_SLEEP)
			self.mode = RHModeSleep
		return True

	def set_mode_rx(self):
		if self.mode != RHModeRx:
			self.spi_write(REG_01_OP_MODE, MODE_RXCONTINUOUS)
			self.spi_write(REG_40_DIO_MAPPING1, 0x00)
			self.mode = RHModeRx

	def set_mode_tx(self):
		if self.mode != RHModeTx:
			self.spi_write(REG_01_OP_MODE, MODE_TX)
			self.spi_write(REG_40_DIO_MAPPING1, 0x40)
			self.mode = RHModeTx	
		return True


	def set_tx_power(self, power):
		if power>23:
			power=23
		if power<5:
			power=5
		# A_DAC_ENABLE actually adds about 3dBm to all 
		# power levels. We will us it for 21, 22 and 23dBm

		if power>20:
			self.spi_write(REG_4D_PA_DAC, PA_DAC_ENABLE)
			power = power -3
		else:
			self.spi_write(REG_4D_PA_DAC, PA_DAC_DISABLE)

		self.spi_write(REG_09_PA_CONFIG, PA_SELECT | (power-5))

	# set a default mode
	def set_modem_config(self, config):
		self.spi_write(REG_1D_MODEM_CONFIG1, config[0])
		self.spi_write(REG_1E_MODEM_CONFIG2, config[1])
		self.spi_write(REG_26_MODEM_CONFIG3, config[2])
		
	def set_preamble_length(self, length):
		self.spi_write(REG_20_PREAMBLE_MSB, length >> 8)
		self.spi_write(REG_21_PREAMBLE_LSB, length & 0xff)


	# send data list
	def send(self, data):
		if len(data) > MAX_MESSAGE_LEN:
			return False
		
		self.set_mode_idle()
		# beggining of FIFO
		self.spi_write(REG_0D_FIFO_ADDR_PTR, 0)

		# write data
		self.spi_write_data(REG_00_FIFO, data)
		self.spi_write(REG_22_PAYLOAD_LENGTH, len(data)-4)

		self.set_mode_tx()
		return True

	# helper method to send strings
	def str_to_data(self, string):
		data = []
		for i in string:
			data.append(ord(i))
		return data

	
if __name__ == "__main__":
	rf95 = RF95(0, 25)
	if not rf95.init():
		print("RF95 not found")
		quit(1)
	else:
		print("RF95 LoRa mode ok")

	rf95.set_frequency(868.5)
	rf95.set_tx_power(5)
	#rf95.set_modem_config(Bw31_25Cr48Sf512)

	rf95.send(rf95.str_to_data("$TELEMETRY TEST"))
	time.sleep(2)
	rf95.set_mode_idle()


