import time
import struct
import board
import os
import subprocess
import glob
from digitalio import DigitalInOut
import chardet
from functions_pi import *
from lzw import *
import threading

led_red=setup_led(board.D20)
led_green=setup_led(board.D16)
led_yellow=setup_led(board.D12)


e_g = threading.Event()
e_r = threading.Event()
e_y= threading.Event()

t_r = threading.Thread(name='non-block', target=blinkLed, args=(e_r, led_red))
t_g = threading.Thread(name='non-block', target=blinkLed, args=(e_g, led_green))
t_y = threading.Thread(name='non-block', target=blinkLed, args=(e_y, led_yellow))

def master(nrf, payload, switch_send):  # count = 5 will only transmit 5 packets
    """Transmits an incrementing integer every second"""
    print("ENTRA EN MASTER, press send again")

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
    
    t_g.start()
    while switch_send.value:
        pass    
    print("It begins to send")
        
    
    e_r.set()
    t_r.start()
    for i in range(count):
        # use struct.pack to structure your data
        # into a usable payload
        buffer = payload[i]
        start_timer = time.monotonic_ns()  # start timer
        
        result = nrf.send(buffer, False, 10)
        while not result:
            e_r.clear()
            e_g.set()
            result = nrf.send(buffer, False, 0)
            time.sleep(0.5)
        end_timer = time.monotonic_ns()  # end timer

        e_r.set()
        e_g.clear()
        
        #if not result:
            #print("send() failed or timed out") 
            #print('Fallo en la transmision'+str(ii))
#         else:
#             print(
#                 "Transmission successful! Time to Transmit:",
#                 "{} us. Sent: {}".format((end_timer - start_timer) / 1000, payload[i]),
#             )
    led_blink(led_yellow)
    print("Transmission rate: ", (((len(payload)*(32+1+3+1+2+9+3+2))*8)/((end_timer-zero_timer)/1e9)))
    print(nrf.print_details(True))
    e_g.set()
    
    
    
def slave(nrf, switch_send):
    nrf.address_length = 3
    address = [b"snd", b"rcv"]
    # set TX address of RX node into the TX pipe
    nrf.open_tx_pipe(address[1])  # always uses pipe 0

    # set RX address of TX node into an RX pipe
    nrf.open_rx_pipe(1, address[0])  # using pipe 1
    nrf.listen = True  # put radio into RX mode and power up
    msg = b""
    start = time.monotonic()
    i=0
    t_g.start()
    print("grab information about the received payload")
    while switch_send.value:
        if nrf.available():
            
            payload_size, pipe_number = (nrf.any(), nrf.pipe)
            # fetch 1 payload from RX FIFO
            buffer = nrf.read()  # also clears nrf.irq_dr status flag
            # expecting a little endian float, thus the format string "<f"
            # buffer[:4] truncates padded 0s if dynamic payloads are disabled
            
           # Here there is another option
            if i == 2:
                print(buffer)
            msg = b"".join([msg,buffer])
            #.decode("utf-8")
            #msg.extend(buffer)
            # print details about the received packet
            #print(
             #   "Received {} bytes on pipe {}: {}".format(
              #      payload_size, pipe_number, msg
               # )
            #)
            start = time.monotonic()
            i +=1
        e_g.set()
    # recommended behavior is to keep in TX mode while idle
    nrf.listen = False  # put the nRF24L01 is in TX mode
    #to optimize, now we open and close the file every 32 BYTES
    print("going to decompress")
    msg = decompress(msg)
    pth = getUSBpath()
    t_y.start()
    try:
        writeFile(pth,msg)
    except Exception as e:
        print(e)
        e_y.set()
    e_y.set()
        
def set_role(nrf, payload):
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

