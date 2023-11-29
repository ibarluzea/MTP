from functions_pi import *
from functions_nrf24 import *
from lzw import *
import spidev

from circuitpython_nrf24l01.rf24 import RF24
# invalid default values for scoping
SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)

try:  # on Linux
    SPI_BUS = spidev.SpiDev()  # for a faster interface on linux
    SPI_BUS.open(0,0)
    SPI_BUS.max_speed_hz = 5000000 # Set SPI speed to 5MHz
    
    CSN_PIN = DigitalInOut(board.D17) # use CE0 on default bus (even faster than using any pin)
    CE_PIN = DigitalInOut(board.D22)  # using pin gpio22 (BCM numbering)

except ImportError:  # on CircuitPython only
    # using board.SPI() automatically selects the MCU's
    # available SPI pins, board.SCK, board.MOSI, board.MISO
    SPI_BUS = board.SPI()  # init spi bus object

    # change these (digital output) pins accordingly
    CE_PIN = DigitalInOut(board.D4)
    CSN_PIN = DigitalInOut(board.D5)
    
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

# initialize the nRF24L01 on the spi bus object
# nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
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
    sys.exit(1)

# Parameters RF nrf
####################
nrf.pa_level = -6
nrf.data_rate = 2
nrf.channel = 90
nrf.ack = False
####################

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
    
    strF= openFile(pth)
    #strF_2= openFile_fromGit()
    codc=check_codec(pth) #now we use path for codec to read more quickly.
    print("CODEC "+codc)
except:
    codc = None
    print("No usb detected")


try:
    strF_compressed = compress(strF)
    payload_compressed = fragmentFile(strF_compressed,payload_size)
except:
    payload_compressed = None
    print("No payload")

# master(nrf, payload)
# slave(nrf, timeout, codec)


print("going to choose mode")
isTransmitter, NMode = select_mode(sw_send, sw_txrx, sw_nm, led_yellow, led_green, led_red)
print("Chosen, is TX: {}, is NM: {}".format(isTransmitter, NMode))
if not NMode:
    if isTransmitter:
        try:
            strF= openFile(pth)
            payload = fragmentFile(strF,payload_size)
            master(nrf, payload)
        except Exception as e:
            payload = None
            print(f"Not file found to fragment")
            print(e)
            ledError()
    else:
        slave(nrf, timeout)
        
print("Transmision finalizada")

print("    nRF24L01 Simple test")

if __name__ == "__main__":
    try:
        while set_role(nrf,payload_compressed, timeout, codc):
            pass  # continue example until 'Q' is entered
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")


