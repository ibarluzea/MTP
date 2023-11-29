import time
import struct
import board
import os as sys
import subprocess
import glob
from digitalio import DigitalInOut
import chardet
from functions_pi import *
from lzw import decompress


def master(nrf, payload):  # count = 5 will only transmit 5 packets
    """Transmits an incrementing integer every second"""
    
    nrf.address_length = 3
    
    address = [b"snd", b"rcv"]
    nrf.open_tx_pipe(address[0])  # always uses pipe 0

    # set RX address of TX node into an RX pipe
    nrf.open_rx_pipe(1, address[1])  # using pipe 1
    nrf.listen = False  # ensures the nRF24L01 is in TX mode
    zero_timer = time.monotonic_ns()
    result = False
#   print(nrf.is_lna_enabled())
    count=len(payload)
    for i in range(count):
        # use struct.pack to structure your data
        # into a usable payload
        limit = 10
        #print(type(payload[i]))
        #print(payload[i])
        buffer = payload[i]
        # "<f" means a single little endian (4 byte) float value.
        start_timer = time.monotonic_ns()  # start timer
        
        result = nrf.send(buffer, False, 10)
        ii=1
        while not result and limit:
            
            ii+=1
            result = nrf.send(buffer, False, 0)
            time.sleep(0.5)
            limit -= 1
        end_timer = time.monotonic_ns()  # end timer
        
        if not result:
            print("send() failed or timed out")
#         else:
#             print(
#                 "Transmission successful! Time to Transmit:",
#                 "{} us. Sent: {}".format((end_timer - start_timer) / 1000, payload[i]),
#             )
    print('Fallo en la transmision'+str(ii))
    print("Transmission rate: ", (((len(payload)*42)*8)/((end_timer-zero_timer)/1e9)))
    print(nrf.print_details(False))
