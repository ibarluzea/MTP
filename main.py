
from functions_pi import *
from functions_nrf24 import *
from lzw import *
import spidev

from circuitpython_nrf24l01.rf24 import RF24
# invalid default values for scoping

if __name__ == "__main__":

    SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)
    try: 
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
        
        try:
            led_on([led_green, led_yellow, led_red])
            led_off([led_green, led_yellow, led_red])
            print("success in LED and switch setup")
        except:
            print("failure in LED setup")
            
            
        
    # initialize the nRF24L01 on the spi bus object
    # nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
        nrf = None
        attempt = 0
        retry_attempts = 20

        while attempt < retry_attempts:
            try:
                nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
                print("RF24 initialized on attempt", attempt + 1)
                led_blink(led_green)
                break  # Assume success and exit the loop

            except Exception as e:
                print("Tried to connect")
                time.sleep(0.5)
                attempt += 1


        if nrf is None:
            print("Failed to initialize RF24 after", retry_attempts, "attempts.")
            ledError()
            os.exit(1)

        # Parameters RF nrf
        ####################
        nrf.pa_level = -6
        nrf.data_rate = 2
        nrf.channel = 90
        nrf.ack = False
        nrf.address_length = 3
        ####################

        # Set timeout
        timeout = 10
        pth = getUSBpath()



        print("Choosing mode")
        
        isTransmitter, NMode = select_mode(sw_send, sw_txrx, sw_nm, led_yellow, led_green, led_red)
        print("Chosen, is TX: {}, is NM: {}".format(isTransmitter, NMode))
        if not NMode:
            if isTransmitter:
                try:
                    payload_size = 32
                    [strF, encoding]= openFile(pth)
                except Exception as e:
                    payload = None
                    print(f"Not file found to fragment")
                    print(e)
                    ledError()
                try:
                    strF_compressed = compress(strF)
                    print("el tipo despues del compress es: ")
                    print(type(strF_compressed))
                    payload_compressed = fragmentFile(strF_compressed,payload_size)
                    print("el tipo despues del fragmentFile es: ")
                    print(type(strF_compressed))
                except Exception as e:
                    print("Compression failed")
                    print(e)
                led_blink(led_green)
                master(nrf, payload_compressed, sw_send, encoding)
            else:
                slave(nrf, sw_send)
    #else:
    #    if isTransmitter:
    #        try:
    #            strF= openFile(pth)
    #            node_NW(nrf,strF,isTransmitter):
    #        except Exception as e:
    #            ledError()
    #    else:
    #        node_NW(nrf,None,isTransmitter):
        
        led_off([led_yellow, led_green, led_red])
        print("Transmision finalizada")

        #wait_idle(sw_off)
    
    
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
        led_off([led_green, led_yellow, led_red])
        e_g.set()

