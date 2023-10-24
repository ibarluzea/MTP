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
    file = open(glob.glob(path+'*.txt')[0],"rb")
    strF= file.read()
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

def fileName(path):
    file = glob.glob(path+'*.txt')[0]
    return file
    
def check_codec(strF):
    try:
        result = chardet.detect(strF)
        encoding = result['encoding']

    except UnicodeDecodeError:
        print(f"Failed with encoding: {encoding}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return encoding
    
#  This following code is to check the functions without calling the
#	functions outside, to be sure they all work well.
# 	TO BE COMMENTED BEFORE FINISHING

payload_size = 32
pth = getUSBpath()
strF= openFile(pth)
codc=check_codec(strF)

print(codec)


