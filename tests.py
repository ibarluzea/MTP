from functions_pi import *
from functions_nrf24 import *
import spidev

pth = getUSBpath()
print("path: "+pth)

codc=check_codec(pth) #now we use path for codec to read more quickly.
print("CODEC: "+codc)


strF= openFile(pth)
payload = fragmentFile(strF,32)

msg = []

for i in payload:
    print(i)
    msg.append(i)

writeFile(pth,msg)
