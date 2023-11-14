import time
import struct
import board
import os as sys
import subprocess
import glob
import digitalio
import chardet



def getUSBpath():
    rpistr = "/media/mtp/"
    proc = subprocess.Popen("ls "+rpistr,shell=True, preexec_fn=sys.setsid, stdout=subprocess.PIPE)
    line = proc.stdout.readline()
    print(str(line.rstrip()))
    path = rpistr + line.rstrip().decode("utf-8")+"/"
    return path

pth = getUSBpath()


# Function to setup a switch
def setup_switch(pin):
    switch = digitalio.DigitalInOut(pin)
    switch.direction = digitalio.Direction.INPUT
    switch.pull = digitalio.Pull.UP  # Assuming a pull-up configuration
    return switch

# Setup LEDs
led_yellow = digitalio.DigitalInOut(board.D12)
led_yellow.direction = digitalio.Direction.OUTPUT
led_red = digitalio.DigitalInOut(board.D20)
led_red.direction = digitalio.Direction.OUTPUT
led_green = digitalio.DigitalInOut(board.D16)
led_green.direction = digitalio.Direction.OUTPUT

# Setup switches
sw_send = setup_switch(board.D5)
sw_txrx = setup_switch(board.D6)
sw_nm = setup_switch(board.D26)
sw_off = setup_switch(board.D23)

# Turn on LEDs
led_yellow.value = True
led_red.value = True
led_green.value = True

# Test switches for 20 seconds
start_time = time.time()
while time.time() - start_time < 20:
    print(f"Send Switch: {sw_send.value}, TXRX Switch: {sw_txrx.value}, NM Switch: {sw_nm.value}, OFF Switch: {sw_off.value}")    
    time.sleep(1)  # Delay to make the output readable

if sw_nm.value:
    pi_shutdown()
# Turn off LEDs
led_yellow.value = False
led_red.value = False
led_green.value = False


