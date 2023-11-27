from functions_pi import *
from functions_nrf24 import *
import spidev

pth = getUSBpath()
print(type(pth))


remove_result(pth)

codc=check_codec(pth) #now we use path for codec to read more quickly.
print("CODEC: "+codc)

with open(pth+"result.txt", "wb") as f:
        print("success")

remove_result(pth)

# writeFile(pth,msg)
