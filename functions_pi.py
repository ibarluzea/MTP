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
        strF= file.read(30)
        
        result = chardet.detect(strF)
        encoding = result['encoding']

    except UnicodeDecodeError:
        print("Failed with encoding: {}".format(encoding))
        return 
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 
    return encoding
    
#  This following code is to check the functions without calling the
#	functions outside, to be sure they all work well.
# 	TO BE COMMENTED BEFORE FINISHING

# payload_size = 32
# pth = getUSBpath()
# codc=check_codec(pth)
# # 
# print(codc)


