import time
import struct
import board
import os as sys
import subprocess
import glob
import digitalio
from digitalio import DigitalInOut
import chardet
import threading


def fragmentFile(string, length):
    return list(string[0+i: length+i] for i in range(0, len(string), length))

def getUSBpath():
    rpistr = "/media/mtp/"
    proc = subprocess.Popen("ls "+rpistr,shell=True, preexec_fn=sys.setsid, stdout=subprocess.PIPE)
    line = proc.stdout.readline()
    print(str(line.rstrip()))
    path = rpistr + line.rstrip().decode("utf-8")+"/"
    return path

def openFileCompress(path):
    try:
        try:
            file = open(glob.glob(path+'*.txt')[0],"rb", encoding='utf-32')
            strF= file.read()
        except:
            try:
                file = open(glob.glob(path+'*.txt')[0],"rb", encoding='utf-16')
                strF= file.read()
                
            except:
                file = open(glob.glob(path+'*.txt')[0],"rb", encoding='utf-8')
                strF= file.read()
    except:
        print("No file opened")

    return strF

def openFile(path):
    try:
        file = open(glob.glob(path+'*.txt')[0],"rb")
        strF= file.read()
    except:
        print("No file opened")
    return strF

def writeFile(path, buff):
    file = open(path+"result.txt","w", 'utf-8')
    file.write(buff)
    file.close()

    
def check_codec(path):
    try:
        file = open(glob.glob(path+'*.txt')[0],"rb")
        strF= file.read(32)
    
        result = chardet.detect(strF)
        encoding = result['encoding']

    except UnicodeDecodeError:
        print("Failed with encoding: {}".format(encoding))
        encoding = None 
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        encoding = None 
    return encoding


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
    
def led_on(signal, t=1.5):
    for i in signal:
        i.value=True
    time.sleep(t)
    for i in signal:
        i.value=False
    

def led_blink(signal):
    c=5
    while c>0:
        for i in signal:
            i.value=True
        time.sleep(0.3)
        for i in signal:
            i.value=False   
        c-=1
        
def ledError():
    signal = digitalio.DigitalInOut(board.D20) 
    signal.direction = digitalio.Direction.OUTPUT
    led_on(signal)

def blinkError():
    signal = digitalio.DigitalInOut(board.D20) 
    signal.direction = digitalio.Direction.OUTPUT
    led_blink(signal)
        
def blinkLed(e, t):
    """flash the specified led every second in threading"""
    while not e.isSet():
        time.sleep(0.3)
        event_is_set = e.wait(t)
        if event_is_set:
            print('stop led from flashing')
        else:
            print('leds off')
            time.sleep(0.3)

def wait_idle(sw_off):
    try:
        while True:
            if not sw_off.value:
                print("Powering off...")
                pi_shutdown()
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False

def pi_shutdown():
    sys.system("sudo poweroff")
    
    
def select_mode(switch_send, switch_tx, switch_nm, led_yellow, led_green, led_red):
    led_blink([led_yellow, led_green, led_red])
    while switch_send:
        if switch_tx:
            isTransmitter=True
            led_green.value=True
        else:
            isTransmitter=False
        if switch_nm:
            NMode = True
            led_yellow.value=True
        else:
            NMode=False
    
    led_blink(led_green)
    led_yellow.value=False
    return isTransmitter, NMode


# 	TO BE COMMENTED BEFORE FINISHING

#  This following code is to check the functions without calling the
#	functions outside, to be sure they all work well.


