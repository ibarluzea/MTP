from functions_pi import *
from functions_nrf24 import *
import spidev

sim_value=choose_simulation() #to use switches or showing in screen"
if not sim_value:
    led_yellow=setup_led(board.D12)
    led_red=setup_led(board.D20)
    led_green=setup_led(board.D16)

    sw_send = setup_switch(board.D5)
    sw_txrx = setup_switch(board.D6)
    sw_nm = setup_switch(board.D26)
    sw_off = setup_switch(board.D23)
else:
    led_yellow=("led yellow")
    led_red=("led_red")
    led_green=("led_green")
    sw_send=True
    sw_txrx=True
    sw_nm=True
    sw_off=True

led_on(led_yellow, sim_value)
led_on(led_red, sim_value)
led_on(led_green, sim_value)

led_blink(led_yellow, sim_value)
led_blink(led_red, sim_value)
led_blink(led_green, sim_value)



# Test switches for 20 seconds
start_time = time.time()
t1=5
while time.time() - start_time < t1:
    print(f"Send Switch: {sw_send.value}, TXRX Switch: {sw_txrx.value}, NM Switch: {sw_nm.value}, OFF Switch: {sw_off.value}")    
    time.sleep(1)  # Delay to make the output readable

payload_size = 32
pth = getUSBpath()
codc=check_codec(pth)

start_time = time.time()
t1=3
while time.time() - start_time < t1:
    t2=time.time() - start_time
    print(f"Press off in {int(round(t1-t2))}")
    if not sw_off.value:
        pi_shutdown()
    else:
        time.sleep(1)



# led_yellow=setup_led(board.D12)
# led_red=setup_led(board.D20)
# led_green=setup_led(board.D16)
# 
# sw_send = setup_switch(board.D5)
# sw_txrx = setup_switch(board.D6)
# sw_nm = setup_switch(board.D26)
# sw_off = setup_switch(board.D23)
