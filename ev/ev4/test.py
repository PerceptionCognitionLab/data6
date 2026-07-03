# -*- coding: utf-8 -*-
"""
Created on Tue May 19 15:32:11 2026

@author: exp
"""
import numpy as np
import pyxid2
import time

Device = pyxid2.get_xid_devices()
print(Device)
dev = Device[0]
print(dev)

dev.reset_timer() # reset the timer to 0 ms

start = time.time() #returns the current time in seconds 

while time.time() - start < 3:
    dev.poll_for_response() # check for responses  
    if dev.has_response(): # do we have responses in the queue
        response = dev.get_next_response() # returns a dictionary with response info
        if response['pressed']:
            print(f"Button {response['key']}  |  RT: {response['time']} ms")
            
# Clear queued responses
dev.clear_response_queue()

# Flush serial buffer if available
dev.con.flush()

# Close port
dev.con.close()