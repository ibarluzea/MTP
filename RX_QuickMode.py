import RF24
import time
import struct
import digitalio as dio
import board

# RECIBIR DATOS

pipes = [ 0x52, 0x78, 0x41, 0x41, 0x41 ] #TODO: Definir Pipes
pipesbytes = bytearray(pipes)
payloadSize= 32; #bytes
ce = dio.DigitalInOut(board.D22)
csn = dio.DigitalInOut(board.D08)
radio = RF24.RF24()
radio.begin(ce, csn)
radio.setPALevel(RF24.RF24_PA_MAX)
radio.setDataRate(RF24.RF24_250KBPS)
radio.setChannel(0x4c) #TODO: canviar channel al que ens assignin
radio.openReadingPipe(1, pipesbytes) #openReadingPipe (uint8_t number, uint64_t address)
radio.startListening()

while True:
  pipe = [1]
  while not radio.available():
    time.sleep(0.30)
    
  recv_buffer = bytearray([])
  recv_buffer = radio.read(payloadSize)
  print(recv_buffer)