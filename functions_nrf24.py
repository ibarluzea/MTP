import time
import struct
import board
import os
import subprocess
import glob
from digitalio import DigitalInOut
import chardet
from functions_pi import *
#from lzw import *
import threading
import zlib
 

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
    
    led_yellow.value = True
    led_green.value = True
    while switch_send.value:
        pass    
    led_yellow.value = False
    led_green.value = False
    print("It begins to send")
    e_g = threading.Event()
    t_g = threading.Thread(name='non-block', target=blinkLed, args=(e_g, led_green))
    t_g.start()
    print(payload[0])
    sequence_id = 0  # Initialize sequence ID

    for i in range(count):
    
        # use struct.pack to structure your data
        # into a usable payload
        buffer = payload[i]
        # Add sequence ID before the buffer we will send
        buffer_with_id = bytes([sequence_id]) + buffer
		
        result = False
        while not result:
            result = nrf.send(buffer_with_id)
            if not result:
                led_red.value = True

        # Increment ID
        sequence_id = (sequence_id + 1) % 256
  
     
        led_red.value = False
        
        end_timer = time.monotonic_ns()  # end timer

    e_g.set()
    led_blink(led_yellow)
    print("Transmission rate: ", (((len(payload)*(32+1+3+1+2+9+3+2))*8)/((end_timer-zero_timer)/1e9)))
    print(nrf.print_details(True))
    
    
    
    
def slave(nrf, switch_send):
        
    e_y = threading.Event()
    t_y = threading.Thread(name='non-block', target=blinkLed, args=(e_y, led_yellow))
    e_g = threading.Event()
    t_g = threading.Thread(name='non-block', target=blinkLed, args=(e_g, led_green))
    
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
    print("It begins to receive information")
    
    #led_yellow.value = True
    #while switch_send.value:
    #    pass
    #led_yellow.value = False
    #time.sleep(0.5)
    
    last_sequence_id = None # Initialize sequence id we will receive
	
    t_g.start()
    while switch_send.value:
        if nrf.available():
            
            payload_size, pipe_number = (nrf.any(), nrf.pipe)
            buffer = nrf.read() 
            sequence_id = buffer[0] 
            data_chunk = buffer[1:]
            if sequence_id != last_sequence_id:
                msg += data_chunk
                last_sequence_id = sequence_id
            

            #msg += buffer
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
            
   
        
    print("Ha dejado de recibir cosas")
    e_g.set()
    # recommended behavior is to keep in TX mode while idle
    nrf.listen = False  # put the nRF24L01 is in TX mode
    #to optimize, now we open and close the file every 32 BYTES
    t_y.start()
    print("length of msg:")
    print(len(msg))
    print("msg type is:")
    print(type(msg))
    try:
        
        pth = None
        while pth is None:
            pth = getUSBpath()
            if pth is None:
                led_red.value = True
                print("USB not found, retrying...")
                time.sleep(0.3)  # Short delay to avoid excessive CPU usage
        led_red.value = False
    except:
        print("getusbpath failed")
        pass
    #writeFile(pth+"/",msg)
    try:
        print("going to decompress")
        msg_decompressed = zlib.decompress(msg)
        print("Correct decompression")
    except:
        led_red.value = True
        print("decompress failed")
        pass
    try:
        writeFile(pth+"/",msg_decompressed)
        print("hola")
    except Exception as e:
        print(e)
        e_y.set()
    e_y.set()
        


