import time
import struct
import board
import os as sys
import subprocess
import glob
from digitalio import DigitalInOut

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