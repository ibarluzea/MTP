from functions_pi import *
from functions_nrf24 import *
import spidev

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
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)

nrf.pa_level = -18
nrf.data_rate = 1


# radio_number = bool(
#     int(input("Which radio is this? Enter '0' or '1'. Defaults to '0' ") or 0)
# )
# 
# # set TX address of RX node into the TX pipe
# nrf.open_tx_pipe(address[radio_number])  # always uses pipe 0
# 
# # set RX address of TX node into an RX pipe
# nrf.open_rx_pipe(1, address[not radio_number])  # using pipe 1


payload_size = 32

# Set timeout
timeout = 10

try:
    pth = getUSBpath()
    path_destino = "/home/mtp/MTP/"
    #This make it very slow, we are reading 1MB,  TOCHECK
    strF= openFile(pth)
    codc=check_codec(pth) #now we use path for codec to read more quickly.
    print("CODEC "+codc)

    payload = fragmentFile(strF,payload_size)
except:
    codc = None
    payload = None
    print("No usb detected")


# master(nrf, payload)
# slave(nrf, timeout, codec)




print("    nRF24L01 Simple test")

if __name__ == "__main__":
    try:
        while set_role(nrf,payload, timeout, codc):
            pass  # continue example until 'Q' is entered
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")


