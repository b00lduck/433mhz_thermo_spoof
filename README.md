# 433mhz_thermo_spoof

## Abstract

This python script spoofs wireless packets for some wireless Kedsum type temperature and humidity sensor working at 433MHz ISM band.

It uses a stripped down rfcat (copied from https://github.com/atlas0fd00m/rfcat) to send packets via a Yard Stick One.

To use it without root privileges, check out udev rules at rfcat/etc.

## Hardware used

  * Yard Stick One

## Dependencies

  * rfcat (bundled)
  * python-usb
  * libusb

## Usage

### Example: 20°C, 60% rH
./send_kedsum.py 20 60
