# -*- coding: utf-8 -*-
"""
Created on Tue May 19 15:36:41 2026

@author: exp
"""

import serial

port = serial.Serial("COM4", baudrate=115200, timeout=1)

print("opened")

port.write(b"\r")
print(port.read(50))

port.close()