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
 

def master(nrf, payload, switch_send, address):  # count = 5 will only transmit 5 packets
    """Transmits an incrementing integer every second"""
    print("ENTRA EN MASTER, press send again")

    print(address[0])
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
    
    #It creates a thread to allowd the green led to asyncrounsly blinks while it is transmitting.
    e_g = threading.Event()
    t_g = threading.Thread(name='non-block', target=blinkLed, args=(e_g, led_green))
    t_g.start()
    print(payload[0])
    sequence_id = 0  # Initialize sequence ID

    for block_number, data_chunk in payload:
        # Construct the payload with block number and sequence ID
        buffer_with_ids = bytes([block_number, sequence_id]) + data_chunk

        result = False
        while not result:
            result = nrf.send(buffer_with_ids)
            if not result:
                led_red.value = True

        # Increment ID
        sequence_id = (sequence_id + 1) % 256
  
     
        led_red.value = False
        
        end_timer = time.monotonic_ns()  # end timer

    e_g.set()
    led_blink(led_yellow)
    #print("Transmission rate: ", (((len(payload)*(32+1+3+1+2+9+3+2))*8)/((end_timer-zero_timer)/1e9)))
    print(nrf.print_details(True))
    
    
def slave(nrf, switch_send):
        
    e_y = threading.Event()
    t_y = threading.Thread(name='non-block', target=blinkLed, args=(e_y, led_yellow))
    e_g = threading.Event()
    t_g = threading.Thread(name='non-block', target=blinkLed, args=(e_g, led_green))
    

    address = [b"sri",b"mrm",b"rcv"]
    # set TX address of RX node into the TX pipe
    print(address[1])
    nrf.open_rx_pipe(0, address[0])  # Addresses for SRI or MRM
    nrf.open_rx_pipe(1, address[1])
    nrf.open_tx_pipe(address[2]) # Envio a rcv
 
    nrf.listen = True  # put radio into RX mode and power up
    msg = b""
    i=0
    
    print("It begins to receive information")
    
    
    last_sequence_id = -1 # Initialize sequence id
    current_block_number = 0
    blocks_data = []
    t_g.start()
 
    while switch_send.value:
        if nrf.available():
            print("Enters nrf.available()")
            payload_size, pipe_number = (nrf.any(), nrf.pipe)
            print(pipe_number)
            if pipe_number == 0:  
                print("SRM")
                buffer = nrf.read() 
                if buffer:
                    print(f"Buffer: {buffer}")
                block_number = buffer[0]
                sequence_id = buffer[1]
                data_chunk = buffer[2:]
                filename = "/MTP-F23-SRI-A-RX"
                if sequence_id != last_sequence_id:  # Check sequence ID first
                    last_sequence_id = sequence_id
                    if block_number != current_block_number:  # Then check block number
                        if msg:  # If there's accumulated data, save it
                            blocks_data.append(msg)
                            msg = b""
                        current_block_number = block_number

                    msg += data_chunk
            if pipe_number == 1: 
                print("MRM")
                buffer = nrf.read() 
                print(f"Buffer: {buffer}")
                block_number = buffer[0]
                sequence_id = buffer[1]
                data_chunk = buffer[2:]
                filename = "/MTP-F23-MRM-A-RX"
                if sequence_id != last_sequence_id:  # Check sequence ID first
                    last_sequence_id = sequence_id
                    if block_number != current_block_number:  # Then check block number
                        if msg:  # If there's accumulated data, save it
                            blocks_data.append(msg)
                            msg = b""
                        current_block_number = block_number

                    msg += data_chunk
    
            
   
    if msg:  # Save the last accumulated block
        blocks_data.append(msg)        
    print("Ha dejado de recibir cosas")
    e_g.set()
    # recommended behavior is to keep in TX mode while idle
    nrf.listen = False  # put the nRF24L01 is in TX mode
    
    t_y.start() # Yellow leds blinks when decompressing and file managing.
    print("length of msg:")
    print(len(msg))
    print("msg type is:")
    print(type(msg))
    try:
        
        pth = None
        while pth is None:
            pth = getUSBpath()
            # It ensures the file is written on the correct path (the USB drive)
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
        decompressed_blocks = []
        for block in blocks_data:
            try:
                decompressed_block = zlib.decompress(block)
                decompressed_blocks.append(decompressed_block)
                print(f"Block {len(decompressed_blocks)} decompressed successfully.")
            except zlib.error as e:
                print(f"Decompression error for a block: {e}")
                break

    # Final reassembly
        reassembled_data = b''.join(decompressed_blocks)
        print("Correct decompression")
    except:
        led_red.value = True
        print("decompress failed")
        pass
    try:
        writeFile(pth+filename,reassembled_data)
        print("success in writing")
    except Exception as e:
        print(e)
        e_y.set()
    e_y.set()
        


