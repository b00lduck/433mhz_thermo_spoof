#!/usr/bin/env python

import sys
import time
from rflib import *
from struct import *
import rflib
import bitstring
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('temperature', type=float, help='temperature in °C')
parser.add_argument('humidity', type=int, help='humidity in %rH')

args = parser.parse_args()

temp = args.temperature
hum = args.humidity
id = 156
batt = 2
ch = 0

print("About to send: {}°C at {} %rH (Batt:{}, CH:{})".format(temp,hum,batt,ch))

def crc4(msg):
  remainder = 0
  poly = 0x3 << 4
  bit = 0

  for x in range(4):
      remainder ^= msg[x]
      for bit in range(8):
          if remainder & 0x80:
              remainder = (remainder << 1) ^ poly
          else:
              remainder = (remainder << 1)
  return remainder >> 4 & 0x0f

def tx(msg):
  d=RfCat()
  d.setModeIDLE()
  while (d.getMARCSTATE()[1] not in (MARC_STATE_IDLE,)):
    pass

  d.setFreq(433920000)
  d.setMdmModulation(MOD_ASK_OOK)
  d.setMdmDRate(2600)
  d.setMdmChanBW(250000)
  d.setMdmSyncMode(SYNCM_NONE)

  # Split into 256 byte chunks
  for i in [rf_data[i:i+255] for i in range(0, len(rf_data), 255)]:
    print("Sending chunk with len {}".format(len(i)))
    d.RFxmit(i)

temp_f = (temp * 9/5) + 32
temp_raw = int(temp_f * 10 + 900)
tl = temp_raw & 0x0f
tm = (temp_raw & 0xf0) >> 4
th = (temp_raw & 0xf00) >> 8
hl = hum & 0x0f
hh = (hum & 0xf0) >> 4
flags = '1000'

data = '{:08b}{:02b}{:02b}{:04b}{:04b}{:04b}{:04b}{:04b}{:4}'.format(id, batt, ch, tl, tm, th, hl, hh, flags)

# create "raw data" byte array to calculate checksum
crc_data = bitstring.BitArray(bin=data).tobytes()
crc = crc4(crc_data) ^(crc_data[4] >> 4)
data_w_crc = "{:2}{:36}{:04b}".format("00", data, crc)

# Convert the data to a PWM
pwm_data = ''.join(['10000000000' if b == '1' else '100000' for b in data_w_crc])

# Assemble the final bit stream
preamble = '100000000000000000000'
final_data = (preamble * 15)
final_data += ((pwm_data + preamble + preamble) * 5)
final_data += pwm_data

# Convert the final bit stream to bytes
rf_data = bitstring.BitArray(bin=final_data).tobytes()
tx(rf_data)
