import time
import struct
import board
import os
import subprocess
import glob
import digitalio
from digitalio import DigitalInOut
import chardet
import threading
import sys
import zlib

global led_red, led_yellow, led_green, sw_send, sw_txrx, sw_nm, sw_off

    
# this function was deprecated by the next one when zlib was the final compression method.
# def fragmentFile(string, length):
#     return list(string[0+i: length+i] for i in range(0, len(string), length))

def fragmentBlocks(block_data, block_number, payload_size=30):
    return [(block_number, block_data[i:i + payload_size]) for i in range(0, len(block_data), payload_size)]

def getUSBpath():
    rpistr = "/media/mtp/"
    try:
        # Listando todos los directorios en /media/mtp/
        directories = os.listdir(rpistr)
        print(directories)
        for directory in directories:
            path = os.path.join(rpistr, directory)
            
            # Verificar si el directorio es accesible
            if os.access(path, os.R_OK):
                print("Accesible: ", path)
                return path
            else:
                print("No accesible: ", path)

    except Exception as e:
        print("Error: ", str(e))

    return None

def openFile(path,f1,f2,f3):
    print(path)
    print(f3)
    try:
        file = open(path+f1,"rb")
        strF= file.read()
        return strF, True
    except:
        try:
            file = open(path+f2,"rb")
            strF= file.read()
            return strF, False
        except:
            try:
                file = open(path+f3,"rb")
                strF= file.read()
                return strF, False
            except:
                print("no file detected")


def writeFile(path, buff):
    file = open(path,"wb")
    file.write(buff)
    file.close()
    
def checkSwitch(pin):
    switch = DigitalInOut(board.GP20)
    switch.switch_to_input
    switch.pull
    return switch

# Deprecated : It checks the file to be able to know the UTF encoding
# def check_codec(path):
#     try:
#         file = open(glob.glob(path+'*.txt')[0],"rb")
#         strF= file.read(64)
#         
#         result = chardet.detect(strF)
#         encoding = result['encoding']
# 
#     except UnicodeDecodeError:
#         print("Failed with encoding: {}".format(encoding))
#         return 
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         return 
#     return encoding

def setup_switch(pin):
    # sw_send D5, sw_txrx D6, sw_nm D26, sw_off D23
    switch = digitalio.DigitalInOut(pin)
    switch.direction = digitalio.Direction.INPUT
    switch.pull = digitalio.Pull.UP  # Assuming a pull-up configuration
    return switch
    
def setup_led(pin):
    #yellow board.D12, #red board.D20, #green board.D16
    signal = digitalio.DigitalInOut(pin) #yellow LED for USB signalling 
    signal.direction = digitalio.Direction.OUTPUT
    return signal
 
# It can switch on several leds at once
def led_on(signal, t=1.5):
    if isinstance(signal, list) :
        for i in signal:
            i.value=True
        time.sleep(t)
        for i in signal:
            i.value=False
    else:
        signal.value=True
        time.sleep(t)
        signal.value=False

def led_off(signal):
    if isinstance(signal, list) :
        for i in signal:
            i.value=False
    else:
        signal.value=False
    
def led_blink(signal):
    c=4
    if isinstance(signal, list) :
        while c>0:
            for i in signal:
                i.value=True
            time.sleep(0.3)
            for i in signal:
                i.value=False
            time.sleep(0.3)
            c-=1
    else:
         while c>0:
            signal.value=True
            time.sleep(0.3)
            signal.value=False
            time.sleep(0.3)
            c-=1
        
def ledError():
    signal = digitalio.DigitalInOut(board.D20) 
    signal.direction = digitalio.Direction.OUTPUT
    led_on(signal)

def blinkError():
    signal = digitalio.DigitalInOut(board.D20) 
    signal.direction = digitalio.Direction.OUTPUT
    led_blink(signal)
        
def blinkLed(e, signal, t=0.3):
    """flash the specified led every second in threading"""
    while not e.isSet():
        signal.value=True
        event_is_set = e.wait(t)
        if event_is_set:
            signal.value=False
            time.sleep(t)
        else:
            signal.value=False
            time.sleep(t)
        
def wait_idle(sw_off):
    try:
        while True:
            if not sw_off.value:
                print("Powering off...")
                pi_shutdown()
            else:
                time.sleep(0.6)
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        led_off([led_green, led_yellow, led_red])
        e_g.set()
        nrf.power = False

def pi_shutdown():
    os.system("sudo poweroff")

# Initially we saved the received file under this name, so we had to remove it everytime
def remove_result(path):
    os.system("rm "+path+"result.txt")
      
def select_mode(switch_send, switch_tx, switch_nm, led_yellow, led_green, led_red):
    led_blink([led_yellow, led_green, led_red])
    led_off([led_yellow, led_green, led_red])
    while switch_send.value:
        if switch_tx.value:
            isTransmitter=True
            led_green.value=True
            led_yellow.value=False
        else:
            isTransmitter=False
            led_green.value=False
            led_yellow.value=True
        if switch_nm.value:
            NMode = True
            led_red.value=True
        else:
            NMode=False
            led_red.value=False
        time.sleep(0.3)
    
    led_blink([led_yellow, led_green, led_red])
    led_off([led_yellow, led_green, led_red])
    return isTransmitter, NMode

def compress_in_blocks(file_data, blocks=4):
    block_size = len(file_data) // blocks
    compressed_blocks = []

    for i in range(blocks):
        print(i)
        start = i * block_size
        end = start + block_size if i != blocks - 1 else len(file_data)
        block = file_data[start:end]
        compressed_block = zlib.compress(block)
        compressed_blocks.append(compressed_block)

    return compressed_blocks

# SETUP of leds and switches

led_yellow=setup_led(board.D12)
led_red=setup_led(board.D20)
led_green=setup_led(board.D16)

sw_send = setup_switch(board.D5)
sw_txrx = setup_switch(board.D6)
sw_nm = setup_switch(board.D26)
sw_off = setup_switch(board.D23)
