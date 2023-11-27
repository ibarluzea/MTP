from functions_pi import *
from functions_nrf24 import *
from lzw import *
import spidev
import os as sys

from circuitpython_nrf24l01.rf24 import RF24
# invalid default values for scoping
SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)

try:
    led_yellow=setup_led(board.D12)
    led_red=setup_led(board.D20)
    led_green=setup_led(board.D16)

    sw_send = setup_switch(board.D5)
    sw_txrx = setup_switch(board.D6)
    sw_nm = setup_switch(board.D26)
    sw_off = setup_switch(board.D23)
    print("success in LED and switch setup")
    led_on([led_green, led_yellow, led_red])
except:
    print("failure in LED setup")
    led_on(led_red)
    

#if __name__ == "__main__":
try:  # on Linux
    SPI_BUS = spidev.SpiDev()
    CSN_PIN = DigitalInOut(board.D17)
    CE_PIN = DigitalInOut(board.D22)  

except ImportError:  # on CircuitPython only
    SPI_BUS = board.SPI()  # init spi bus object
    CE_PIN = DigitalInOut(board.D4)
    CSN_PIN = DigitalInOut(board.D5)

nrf = None
attempt = 0
retry_attempts = 5
while attempt < retry_attempts:
    try:
        nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
        print("RF24 initialized on attempt", attempt + 1)
        led_blink(led_green)
        
        break  # Assume success and exit the loop

    except Exception as e:
        print("Tried to connect")
        time.sleep(1)
        attempt += 1


if nrf is None:
    print("Failed to initialize RF24 after", retry_attempts, "attempts.")
    blinkError()
    sys.exit(1)


nrf.pa_level = -18
nrf.data_rate = 2
payload_size = 32

timeout = 10 # Set timeout

try:
    pth = getUSBpath()
    codc=check_codec(pth) #now we use path for codec to read more quickly.
    print("CODEC: "+codc)
except OSError:
    print("No usb detected")
    ledError()
except:
    print(f"An unexpected error occurred")
    ledError()

print("going to choose mode")
isTransmitter, NMode = select_mode(sw_send, sw_txrx, sw_nm, led_yellow, led_green, led_red)
print("Chosen, is TX: {}, is NM: {}".format(isTransmitter, NMode))
if not NMode:
    if isTransmitter:
        try:
            strF= openFile(pth)
            payload = fragmentFile(strF,payload_size)
            master(nrf, payload)
        except:
            payload = None
            print(f"Not file found to fragment")
            ledError()
    else:
        slave(nrf, timeout, codc)



# 
#     try:       
#         while set_role(nrf,payload, timeout, codc):
#             pass  # continue example until 'Q' is entered
#     except KeyboardInterrupt:
#         print(" Keyboard Interrupt detected. Powering down radio...")
#         nrf.power = False
# else:
#     print("    Run slave() on receiver\n    Run master() on transmitter")
# 
# 
# 