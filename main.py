from functions_pi import *
from functions_nrf24 import *
from lzw import *
import spidev
import os as sys

from circuitpython_nrf24l01.rf24 import RF24
# invalid default values for scoping
SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)

try:  # on Linux
    SPI_BUS = spidev.SpiDev()  # for a faster interface on linux
    CSN_PIN = DigitalInOut(board.D17) # use CE0 on default bus (even faster than using any pin)
    CE_PIN = DigitalInOut(board.D22)  # using pin gpio22 (BCM numbering)

except ImportError:  # on CircuitPython only
    # using board.SPI() automatically selects the MCU's
    # available SPI pins, board.SCK, board.MOSI, board.MISO
    SPI_BUS = board.SPI()  # init spi bus object

    # change these (digital output) pins accordingly
    CE_PIN = DigitalInOut(board.D4)
    CSN_PIN = DigitalInOut(board.D5)


# initialize the nRF24L01 on the spi bus object
# nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
nrf = None
attempt = 0
retry_attempts = 5

while attempt < retry_attempts:
    try:
        nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
        print("RF24 initialized on attempt", attempt + 1)
        break  # Assume success and exit the loop

    except Exception as e:
        print("Tried to connect")
        time.sleep(1)
        attempt += 1


if nrf is None:
    print("Failed to initialize RF24 after", retry_attempts, "attempts.")
    sys.exit(1)


nrf.pa_level = -18
nrf.data_rate = 2

payload_size = 32

# Set timeout
timeout = 10

try:

    pth = getUSBpath()
    path_destino = "/home/mtp/MTP/"
    
    strF= openFile(pth)
    codc=check_codec(pth) #now we use path for codec to read more quickly.
    print("CODEC: "+codc)
except OSError:
    print("No usb detected")
except:
    print(f"An unexpected error occurred")

try:
    payload = fragmentFile(strF,payload_size)
except:
    payload = None
    print(f"Not file found to fragment")



print("    nRF24L01 Simple test")

if __name__ == "__main__":
    try:
        led_yellow=setup_led(board.D12)
        led_red=setup_led(board.D20)
        led_green=setup_led(board.D16)

        sw_send = setup_switch(board.D5)
        sw_txrx = setup_switch(board.D6)
        sw_nm = setup_switch(board.D26)
        sw_off = setup_switch(board.D23)
        print("success in LED and switch setup")
        led_on(led_green)
        
    except:
        print("failure in LED setup")
        led_on(led_red)
            
    try:       
        while set_role(nrf,payload, timeout, codc):
            pass  # continue example until 'Q' is entered
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")


