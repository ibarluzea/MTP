
from functions_pi import * # ALL FUNCTIONS THAT ARE NOT RELATED TO RF TRANSMISSIONS. (usb path, reading, writing, use leds)
from functions_nrf24 import * # TX RX FUNCTIONS
from node_nw import * # NM FUNCTIONS
#from lzw import * # INITIAL CUSTOM COMPRESSION FUNCTIONS
import spidev # python module for interfacing with SPI devices
import zlib # Optimized compression module
from circuitpython_nrf24l01.rf24 import RF24 # NRF24 module library

if __name__ == "__main__":

    SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)
    try: 
        # Here we configure the pins that work with the NRF24 board.
        SPI_BUS = spidev.SpiDev()  # for a faster interface on linux
        CSN_PIN = DigitalInOut(board.D17) 
        CE_PIN = DigitalInOut(board.D22)  # using pin gpio22

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
        # Connection to the board. It normally used to fail once, so this part ensure the correct setup.
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
        
        fileSRI="/MTP-F23-SRI-A-TX.txt"
        fileNW="/MTP-F23-NM-TX.txt"
        fileMRM="/MTP-F23-MRM-A-TX.txt"

        print("Choosing mode")
    
        isTransmitter, NMode = select_mode(sw_send, sw_txrx, sw_nm, led_yellow, led_green, led_red) # This helps to choose mode and TX/RX
        
        print("Chosen, is TX: {}, is NM: {}".format(isTransmitter, NMode))
        if not NMode:
            if isTransmitter:
                print("Vamos a buscar path usb")
            
                pth = None
                while pth is None:
                    pth = getUSBpath()
                    if pth is None:
                        led_red.value = True
                        print("USB not found, retrying...")
                        time.sleep(0.3)  # Short delay to avoid excessive CPU usage
                led_red.value = False
                try:
                    print("USB path is:", pth)
                    payload_size = 30
                    strF, isSRI= openFile(pth,fileSRI,fileNW,fileMRM)
                except Exception as e:
                    payload = None
                    print(f"Not file found to fragment")
                    print(e)
                    ledError()
                try:
                    if isSRI:
                        address = [b"sri", b"rcv"]
                    else:
                        address = [b"mrm", b"rcv"]
                    compressed_blocks = compress_in_blocks(strF, blocks=4)
                    print("compress_in_blocks worked")
                    fragmented_payloads = []
                    for block_number, compressed_block in enumerate(compressed_blocks):
                        fragments = fragmentBlocks(compressed_block, block_number, payload_size=30)
                        fragmented_payloads.extend(fragments)
                    print(fragmented_payloads)

                except Exception as e:
                    print("Compression failed")
                    print(e)
                led_blink(led_green)
                master(nrf, fragmented_payloads, sw_send,address)
            else:
                slave(nrf, sw_send)
        else:
            if isTransmitter:
                try:
                    pth = None
                    while pth is None:
                        pth = getUSBpath()
                        if pth is None:
                            led_red.value = True
                            print("USB not found, retrying...")
                            time.sleep(0.3)  # Short delay to avoid excessive CPU usage
                    led_red.value = False
                    strF, aa= openFile(pth,fileSRI,fileNW,fileMRM)
                    node_NW(nrf,strF,isTransmitter)
                except Exception as e:
                    ledError()
            else:
                node_NW(nrf,None,isTransmitter)
        
        led_off([led_yellow, led_green, led_red])
        print("Transmision finalizada")

        wait_idle(sw_off) # It is ready to safely power off the board.
    
    
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
        led_off([led_green, led_yellow, led_red])
        e_g.set()
