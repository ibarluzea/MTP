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

global led_red, led_yellow, led_green, sw_send, sw_txrx, sw_nm, sw_off

    

def fragmentFile(string, length):
    return list(string[0+i: length+i] for i in range(0, len(string), length))

#def getUSBpath():
#    rpistr = "/media/mtp/"
#    proc = subprocess.Popen("ls "+rpistr,shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE)
#    line = proc.stdout.readline()
#    print(str(line.rstrip()))
#    path = rpistr + line.rstrip().decode("utf-8")+"/"
#    return path
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
def openFile(path):
    try:
        #try:
        #    codc=check_codec(path) #now we use path for codec to read more quickly.
        #    print("Chardet detected: "+codc)
        #except:
        #    print("Chardet failed")
        try:
            file = open(glob.glob(path+'*.txt')[0],"r", encoding='utf-32')
            strF= file.read()
            
            print("Tried utf-32")
            
        except:
            try:
                file = open(glob.glob(path+'*.txt')[0],"r", encoding='utf-16')
                strF= file.read()
                print("Tried utf-16")
                
            except:
                file = open(glob.glob(path+'*.txt')[0],"r", encoding='utf-8')
                strF= file.read()
                print("Tried utf-8")
    except:
        print("No file opened")
    return strF

def openFile_fromGit():
    try:
        try:
            file = open("test_utf8.txt","r", encoding='utf-32')
            strF= file.read()
        except:
            try:
                file = open("test_utf8.txt","r", encoding='utf-16')
                strF= file.read()
                
            except:
                file = open("test_utf8.txt","r", encoding='utf-8')
                strF= file.read()
    except:
        print("No file opened")
    return strF

def openFile_fromGit2():
    try:
        try:
            file = open("test_utf8.txt","rb")
            strF= file.read()
        except:
            try:
                file = open("test_utf8.txt","rb")
                strF= file.read()
                
            except:
                file = open("test_utf8.txt","rb")
                strF= file.read()
    except:
        print("No file opened")
    return strF

def writeFile(path, buff):
    file = open(path+"result.txt","w")
    file.write(buff)
    file.close()
    
def checkSwitch(pin):
    switch = DigitalInOut(board.GP20)
    switch.switch_to_input
    switch.pull
    return switch


    
def check_codec(path):
    try:
        file = open(glob.glob(path+'*.txt')[0],"rb")
        strF= file.read(64)
        
        result = chardet.detect(strF)
        encoding = result['encoding']

    except UnicodeDecodeError:
        print("Failed with encoding: {}".format(encoding))
        return 
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 
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
                
def blink_thread(e, t=0.3):
    """flash the specified led every second in threading"""
    while not e.isSet():
        signal_led.value=True
        event_is_set = e.wait(t)
        if event_is_set:
            signal_led.value=False
        else:
            signal_led.value=False
            e.wait(t)


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

def pi_shutdown():
    os.system("sudo poweroff")
    
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
        time.sleep(0.5)
    
    led_blink([led_yellow, led_green, led_red])
    led_off([led_yellow, led_green, led_red])
    return isTransmitter, NMode
    
    
led_yellow=setup_led(board.D12)
led_red=setup_led(board.D20)
led_green=setup_led(board.D16)

sw_send = setup_switch(board.D5)
sw_txrx = setup_switch(board.D6)
sw_nm = setup_switch(board.D26)
sw_off = setup_switch(board.D23)

#  This following code is to check the functions without calling the
#	functions outside, to be sure they all work well.
# 	TO BE COMMENTED BEFORE FINISHING

# payload_size = 32
# pth = getUSBpath()
# codc=check_codec(pth)
# # 
# print(codc)


