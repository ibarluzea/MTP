from functions_pi import *
from functions_nrf24 import *
import spidev


sw_send = setup_switch(board.D5)
sw_txrx = setup_switch(board.D6)
sw_nm = setup_switch(board.D26)
sw_off = setup_switch(board.D23)
led_yellow=setup_led(board.D12)
led_red=setup_led(board.D20)
led_green=setup_led(board.D16)


led_off([led_yellow,led_red, led_green ])
# led_blink(led_yellow)
# led_blink(led_green)
# led_blink(led_red)

led_blink([led_yellow,led_red, led_green])

# print("going to choose mode")
# isTransmitter, NMode = select_mode(sw_send, sw_txrx, sw_nm, led_yellow, led_green, led_red)
# print("Chosen, is TX: {}, is NM: {}".format(isTransmitter, NMode))
# #ledError()
# blinkError()
# 

# 
# 
# led_on(led_yellow)
# led_on(led_red)
# led_on(led_green)
# 
# led_blink(led_yellow)
# led_blink(led_red)
# led_blink(led_green)
# 
# 
# # Test switches for 20 seconds
# start_time = time.time()
# t1=20
# while time.time() - start_time < t1:
#     print(f"Send Switch: {sw_send.value}, TXRX Switch: {sw_txrx.value}, NM Switch: {sw_nm.value}, OFF Switch: {sw_off.value}")    
#     time.sleep(1)  # Delay to make the output readable
# 
# payload_size = 32
# pth = getUSBpath()
# codc=check_codec(pth)
# 
# start_time = time.time()
# t1=4
# while time.time() - start_time < t1:
#     t2=time.time() - start_time
#     print(f"Press off in {int(round(t1-t2))}")
#     if not sw_off.value:
#         pi_shutdown()
#     else:
#         time.sleep(1)



# led_yellow=setup_led(board.D12)
# led_red=setup_led(board.D20)
# led_green=setup_led(board.D16)
# 
# sw_send = setup_switch(board.D5)
# sw_txrx = setup_switch(board.D6)
# sw_nm = setup_switch(board.D26)
# sw_off = setup_switch(board.D23)
