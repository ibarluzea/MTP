import RF24
import time
import struct
import digitalio as dio
import board

# TRANSMITIR DATOS

pipes = [ 0x52, 0x78, 0x41, 0x41, 0x41 ] #TODO: Definir Pipes
pipesbytes = bytearray(pipes)
payloadSize= 32; #bytes
ce = dio.DigitalInOut(board.D22)
csn = dio.DigitalInOut(board.D08)
radio = RF24.RF24()
radio.begin(ce, csn)
radio.setPALevel(RF24.RF24_PA_MAX)
radio.setDataRate(RF24.RF24_250KBPS)
radio.setRetries(3,5) # TODO: Falta definir setRetries (uint8_t delay, uint8_t count) Set the number and delay of retries upon failed submit. (Delay is the num*250us)
radio.setChannel(0x4c) #TODO: canviar channel al que ens assignin
radio.openWritingPipe(1, pipesbytes) #openWritingPipe (uint8_t number, uint64_t address)
radio.powerUp() #Leave low-power mode - making radio more responsive.
radio.printDetails()

while True:
  print(radio.write("Hola"))
  time.sleep(1)