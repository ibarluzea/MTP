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



strF= openFile(pth)
payload = fragmentFile(strF,32)
count=len(payload)
print(count)

msg = []

for i in range(count):
    buffer=payload[i]
    if i < 2:
        print(buffer)
    
    msg+=buffer
print(type(msg))      
writeFile(pth,bytes(msg))
