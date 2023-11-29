import time
import struct
import board
from digitalio import DigitalInOut
import os, glob, getpass, math
from subprocess import check_output
from circuitpython_nrf24l01.rf24 import RF24
import spidev


def node_NW(nrf,strF,isTransmitter):
  has_token = isTransmitter
  has_file = isTransmitter
  address = [b"BRD",b"0RC"] #Change the unicast address xRC for every group. --> 0 to 7
  my_address = [int(char) for char in address[1].decode() if char.isdigit()]
  token =[[False, False],[False, False],[False, False],[False, False],[False, False],[False, False] ,[False, False] ,[False, False]]

  discovery_timeout = 8e6 # with respect nanoseconds
  ack_timeout = 992e-6
  backoff = 1/1000 # One per group
  
  discovery_payload = b'\x0A'
  data_payload = b'\x0C'
  token_payload = b'\x0D'
  ef_payload = b'\x0E'

  #nrf.open_rx_pipe(0, address[0])  # using RX pipe 0 for broadcast
  nrf.open_rx_pipe(1, address[1])

  while True:
    if has_token: # Es Master
      address_list = neighbor_discovery(discovery_payload, address[1], address[0])
      tx_Success = unicast_tx(strF,data_payload,ef_payload,address[1], address_list)
      token,has_token = token_handover(token, address_list)
    else: # Es Slave
      nrf.open_rx_pipe(0, address[0])

def neighbor_discovery(discovery_payload,my_address,dst_address):
  no_received = True
  nrf.open_tx_pipe(dst_address) #uses pipe 0, address 0.
  buffer_tx = discovery_payload + my_address 
  no_received = True
  neighbors = b""
  while no_received:
    nrf.listen = False
    nrf.send(buffer_tx, True) #send the broadcast, True = No ACK.
    nrf.listen = True
    
    start_time = time.time_ns()
    while (time.time_ns() - start_time) < discovery_timeout: #wait for responses
      if nrf.available():
        buffer_rx = nrf.read()
     
    if buffer_rx is not empty:
      neighbors = b"".join([neighbors,buffer_rx]) 
      nrf.listen = False
      no_received = False
  
  address_list = [int(char) for char in neighbors.decode() if char.isdigit()] # Get from a b"1RC5RC8RC" --> [1,5,8]
  return address_list

def unicast_tx(file,data_payload,ef_payload,my_address,address_list):
  payload = fragmentFile(strF,31)
  count=len(payload)
  
  for i in address_list:
    dst_address = bytes(str(i, codec))+b"RC"
    nrf.open_tx_pipe(dst_address)
    result = False
    for j in range(count):
      limit = 10
      buffer = data_payload + payload[j]
      outer_re = 1 # Reintents fora dels intents del ack. + Resiliencia.
      while not result and limit:      
        outer_re+=1
        result = nrf.send(buffer, False, 0)
        time.sleep(0.5)
        limit -= 1
  nrf.listen = False
  buffer_tx = ef_payload
  Tx_Success = nrf.send(buffer_tx, False)
  # Afegir resiliencia?

def token_handover(token,token_payload,address_list,dst_address):
  priority = []
  token[int(my_address[0])][:] = [True,True] # I have the file and token.
  for i in address_list:
    if (token[i][1]) == False # Never had the token. (If true, it must have the file)
      token[i][0] == True # Has the file.
      priority.append(i)

  token_sent = False
  priority.extend(address_list)

  for i in priority:
    dst_address = bytes(str(i, codec))+b"RC"
    nrf.open_tx_pipe(dst_address)
    token_bytes = bytes(sum(map(lambda x: [int(y) for y in x], token, [])) # ChatGpt llista de llistes --> Byte format.
    buffer_tx = token_payload+token_bytes
    nrf.send(buffer_tx, False)
  return token, False
