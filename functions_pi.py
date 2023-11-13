import time
import struct
import board
import os as sys
import subprocess
import glob
from digitalio import DigitalInOut
import chardet


def fragmentFile(string, length):
    return list(string[0+i: length+i] for i in range(0, len(string), length))

def getUSBpath():
    rpistr = "/media/mtp/"
    proc = subprocess.Popen("ls "+rpistr,shell=True, preexec_fn=sys.setsid, stdout=subprocess.PIPE)
    line = proc.stdout.readline()
    print(str(line.rstrip()))
    path = rpistr + line.rstrip().decode("utf-8")+"/"
    return path

def openFile(path):
    try:
        try:
            file = open(glob.glob(path+'*.txt')[0],"r", encoding='utf-32')
            strF= file.read()
        except:
            try:
                file = open(glob.glob(path+'*.txt')[0],"r", encoding='utf-16')
                strF= file.read()
                
            except:
                file = open(glob.glob(path+'*.txt')[0],"r", encoding='utf-8')
                strF= file.read()
    except:
        print("No file opened")
    return strF

def writeFile(path, buff):
    file = open(path+"result.txt","w", 'utf-8')
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
        strF= file.read(30)
        
        result = chardet.detect(strF)
        encoding = result['encoding']

    except UnicodeDecodeError:
        print("Failed with encoding: {}".format(encoding))
        encoding = None 
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        encoding = None 
    return encoding
    
def setup_inout():
    led_yellow = DigitalInOut(board.D12) #yellow LED for USB signalling 
    led_yellow.direction = digitalio.Direction.OUTPUT

    led_red = DigitalInOut(board.D20) #red LED
    led_red.direction = digitalio.Direction.OUTPUT

    led_green = DigitalInOut(board.D16) #green LED for sending finished 
    led_green.direction = digitalio.Direction.OUTPUT

    sw_send = DigitalInOut(board.D5)
    sw_send.switch_to_input
    sw_send.pull

    sw_txrx = DigitalInOut(board.D6)
    sw_txrx.switch_to_input
    sw_txrx.pull

    sw_nm = DigitalInOut(board.D26)
    sw_nm.switch_to_input
    sw_nm.pull

    sw_off = DigitalInOut(board.D23)
    sw_off.switch_to_input
    sw_off.pull
    
def led_on(signal, sim=False):
    if sim:
        print("led "+signal+" is ON")
    else
        signal.value=True
        time.sleep(1.5)
        signal.value=False

def led_blink(signal, sim=False):
    if sim:
        print("led "+signal+" is blinking")
        time.sleep(1)
        print("led "+signal+" is blinking")
    else
        c=3
        while c>0
            signal.value=True
            time.sleep(0.4)
            signal.value=False
            time.sleep(0.4)
            c-=1
            
def choose_simulation():
    user_input = (
        input(
            "*** Enter 'P' to use physical LEDs and switches.\n"
            "*** Enter 'S' to simulate swiches with keyboard.\n"
        )
    )
    user_input = user_input.split()
    if user_input[0].upper().startswith("P"):
        sim_value=False
    if ser_input[0].upper().startswith("S"):
        sim_value=True
    return sim_value
    

        
#  This following code is to check the functions without calling the
#	functions outside, to be sure they all work well.
# 	TO BE COMMENTED BEFORE FINISHING

# led_yellow, led_red, led_green, sw_send, sw_txrx, sw_nm, sw_off = setup_inout()
# led_on(led_yellow, sim=True)

# payload_size = 32
# pth = getUSBpath()
# codc=check_codec(pth)
# # 
# print(codc)


