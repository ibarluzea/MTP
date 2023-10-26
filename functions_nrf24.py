import time
import struct
import board
import os as sys
import subprocess
import glob
from digitalio import DigitalInOut
import chardet
from functions_pi import *


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
        limit = 100
        print(type(payload[i]))
        print(payload[i])
        buffer = payload[i]
        # "<f" means a single little endian (4 byte) float value.
        start_timer = time.monotonic_ns()  # start timer
        result = nrf.send(buffer, False, 10)
        
        while not result and limit: 
            result = nrf.send(buffer, False, 10)
            time.sleep(0.5)
            limit -= 1
        end_timer = time.monotonic_ns()  # end timer
        
        if not result:
            print("send() failed or timed out")
        else:
            print(
                "Transmission successful! Time to Transmit:",
                "{} us. Sent: {}".format((end_timer - start_timer) / 1000, payload[i]),
            )
    print("Transmission rate: ", (((len(payload)*32)*8)/((end_timer-zero_timer)/1e9)))
    print(nrf.print_details(False))
    
    
    
def slave(nrf, timeout, codec):
    """Polls the radio and prints the received value. This method expires
    after 6 seconds of no received transmission"""
    address = [b"snd", b"rcv"]
    # set TX address of RX node into the TX pipe
    nrf.open_tx_pipe(address[1])  # always uses pipe 0

    # set RX address of TX node into an RX pipe
    nrf.open_rx_pipe(1, address[0])  # using pipe 1
    nrf.listen = True  # put radio into RX mode and power up
    msg = b""
    start = time.monotonic()
    while (time.monotonic() - start) < timeout:
        if nrf.available():
            # grab information about the received payload
            payload_size, pipe_number = (nrf.any(), nrf.pipe)
            # fetch 1 payload from RX FIFO
            buffer = nrf.read()  # also clears nrf.irq_dr status flag
            # expecting a little endian float, thus the format string "<f"
            # buffer[:4] truncates padded 0s if dynamic payloads are disabled
            
           # Here there is another option
            msg += buffer#.decode("utf-8")
            #msg.extend(buffer)
            # print details about the received packet
            print(
                "Received {} bytes on pipe {}: {}".format(
                    payload_size, pipe_number, msg
                )
            )
            start = time.monotonic()

    # recommended behavior is to keep in TX mode while idle
    nrf.listen = False  # put the nRF24L01 is in TX mode
    writeFile("/home/mtp/MTP/",msg)
        
def set_role(nrf, payload, timeout, codec):
    """Set the role using stdin stream. Timeout arg for slave() can be
    specified using a space delimiter (e.g. 'R 10' calls `slave(10)`)
    """
    user_input = (
        input(
            "*** Enter 'R' for receiver role.\n"
            "*** Enter 'T' for transmitter role.\n"
            "*** Enter 'Q' to quit example.\n"
        )
        or "?"
    )
    user_input = user_input.split()
    if user_input[0].upper().startswith("R"):
        slave(nrf, timeout, codec)
        
        return True
    if user_input[0].upper().startswith("T"):
        master(nrf, payload)
        return True
    if user_input[0].upper().startswith("Q"):
        nrf.power = False
        return False
    print(user_input[0], "is an unrecognized input. Please try again.")
    return set_role(nrf, payload, timeout, codec)

