from functions_pi import *
from functions_nrf24 import *
import spidev


led_yellow=setup_led(board.D12)
led_red=setup_led(board.D20)
led_green=setup_edl(board.D16)

sw_send = setup_switch(board.D5)
sw_txrx = setup_switch(board.D6)
sw_nm = setup_switch(board.D26)
sw_off = setup_switch(board.D23)

led_on(led_yellow, False)
led_on(led_yellow, True)

led_on(led_yellow, False)

# Test switches for 20 seconds
start_time = time.time()
while time.time() - start_time < 20:
    print(f"Send Switch: {sw_send.value}, TXRX Switch: {sw_txrx.value}, NM Switch: {sw_nm.value}, OFF Switch: {sw_off.value}")    
    time.sleep(1)  # Delay to make the output readable

payload_size = 32
pth = getUSBpath()
codc=check_codec(pth)
