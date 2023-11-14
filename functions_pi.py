import time
import struct
import board
import os as sys
import subprocess
import glob
import digitalio
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


def setup_switch(pin):
    # sw_send D5
    # sw_txrx D6
    # sw_nm D26
    # sw_off D23
    switch = digitalio.DigitalInOut(pin)
    switch.direction = digitalio.Direction.INPUT
    switch.pull = digitalio.Pull.UP  # Assuming a pull-up configuration
    return switch
    
def setup_led(pin, sim=False):
    #yellow board.D12
    #red board.D20
    #green board.D16
    if sim:
        signal=pin
    else:
        signal = digitalio.DigitalInOut(pin) #yellow LED for USB signalling 
        signal.direction = digitalio.Direction.OUTPUT
    return signal
    
def led_on(signal, sim=False):
    print("yellow board.D12, red board.D20, green board.D16")
    if sim:
        print(f"led {signal} is ON")
        time.sleep(0.5)
        print(f"led {signal} is OFF")
    else:
        signal.value=True
        time.sleep(1.5)
        signal.value=False

def led_blink(signal, sim=False):
    print("yellow board.D12, red board.D20, green board.D16")
    if sim:
        print(f"led {signal} is blinking")
        time.sleep(1)
        print(f"led {signal} is blinking")
        time.sleep(1)

    else:
        c=3
        while c>0:
            signal.value=True
            time.sleep(0.4)
            signal.value=False
            time.sleep(0.4)
            c-=1
            
def choose_simulation():
    user_input = (
        input(
            "*** Enter 'P' to use physical LEDs and switches.\n"
            "*** Enter 'S' to simulate switches with keyboard.\n"
        )
    )
    user_input = user_input.split()
    if user_input[0].upper().startswith("P"):
        sim_value=False
    if user_input[0].upper().startswith("S"):
        sim_value=True
    return sim_value
    
def pi_shutdown():
    sys.system("sudo poweroff")

        
#  This following code is to check the functions without calling the
#	functions outside, to be sure they all work well.
# 	TO BE COMMENTED BEFORE FINISHING

#led_yellow=setup_led(board.D12)
#led_on(led_yellow, False)

# payload_size = 32
# pth = getUSBpath()
# codc=check_codec(pth)
# # 
# print(codc)




