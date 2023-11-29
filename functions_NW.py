import time
import struct
import board
from digitalio import DigitalInOut
import os, glob, getpass, math
from subprocess import check_output
from circuitpython_nrf24l01.rf24 import RF24
import spidev
# Migrar imports en el main.


def masterNW(nrf,timeout,payload,codec): 

  has_token = True
  nrf.address_length = 3
  address = [b"BRD",b"0RC"] #Change the unicast address xRC for every group. --> 0 to 7

  discovery_timeout = 8e6 # with respect nanoseconds
  ack_timeout = 992e-6
  
  token =[[False, False],[False, False],[False, False],[False, False],[False, False],[False, False] ,[False, False] ,[False, False]]

  discovery_payload = b'\x0A'
  data_payload = b'\x0C'
  token_payload = b'\x0D'

  # 1) Neighbor disc
  nrf.open_tx_pipe(address[0]) #uses pipe 0, address 0.
  nrf.open_rx_pipe(1, address[1]) 
  buffer_tx = discovery_payload + address[1]  
  no_received = True
  neighbors = b""
  
  while no_received:
    
    nrf.listen = False
    neighbor_discovery = nrf.send(buffer_tx, True) #send the broadcast, True = No ACK.
    nrf.listen = True
    
    start_time = time.time_ns()
    while (time.time_ns() - start_time) < discovery_timeout: #wait for responses
      buffer_rx = nrf.read()
      #Add sleep(x ns)?
      
    if buffer_rx is not empty:
      neighbors = b"".join([neighbors,buffer_rx]) 
      nrf.listen = False
      no_received = False
    end
  
  nrf.close_rx_pipe(1)
  address_list = [int(char) for char in neighbors.decode() if char.isdigit()] # Get from a b"1RC5RC8RC" --> [1,5,8]
  my_address = [int(char) for char in address[1].decode() if char.isdigit()]

# 2) Unicast Transmisions

nrf.open_rx_pipe(2, address[1]) # També podria ser la pipe 1 a priori.
for i in address_list:
  dst_address = bytes(str(i, codec))+b"RC"
  nrf.open_tx_pipe(dst_address) 

  

  nrf.listen = False
  buffer_tx = b"EOT"
  neighbor_discovery = nrf.send(buffer_tx, False) # AutoAck Enabled.
# Això es farà per cada i == address que haguem rebut.

# 3) Token handover.
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
  token_sent = nrf.send(buffer_tx, False)


def slaveNW(nrf):
    has_token = False
    has_file = False
    keep_listening = True

    nrf.address_length = 3
    # addresses needs to be in a buffer protocol object (bytearray)
    address = [b"BRD", b"1RC"]
    my_address = [int(char) for char in address[1].decode() if char.isdigit()]


    backoff = 1/1000 # Diferent per a cada nodo

    nrf.open_rx_pipe(0, address[0])  # using RX pipe 0 for broadcast
    nrf.open_rx_pipe(1, address[1])  # using RX pipe 1 for unicast

    while keep_listening:
        nrf.listen = True  # put radio into RX mode and power up
    
        # 1) Escoltar i mirar a quina pipe has rebut info
        if nrf.available():
            # grab information about the received payload
            payload_size, pipe_number = (nrf.any(), nrf.pipe)
            rx = nrf.read() #Clears flags & empties RX FIFO, saves bytes in rx

            # 2) Enviar resposta al neighbour discovery
            if pipe_number == 0: # S'ha rebut a la pipe de broadcast -> Neighbour Discovery
                address_received = rx[1:address_length + 1] 

                nrf.open_tx_pipe(address_received)
                time.sleep(backoff)
                send_address()

            # 3) Rebo algo unicast, mirar quin tipo de paquet arriba
            if pipe_number == 1: # S'ha rebut a la pipe de unicast -> O fitxer o Token
                type_byte = rx[0] # Agafar el primer byte que indica tipus de paquet
                if type_byte == b'\x0E': # Token
                    has_token = True
                    token = interpretarToken(rx[1:]) # FUNCIO QUE LLEGEIXI EL PAQUET DEL TOKEN I EL POSI EN FORMAT LLISTA
                    token[int(my_address[0])][:] = [True,True] # actualitzo token
                    keep_listening = False
                elif type_byte == b'\x0D': # End of Transmission
                    has_file = True

                    # PROCESSAR TEXT, ESCRIURE, ETC
                    # Un cop s'ha rebut tot el fitxer, escriure els bytes al USB, cadascu amb la seva funcio d'escriure al USB
                    # Codi d'encendre led VERD

                elif type_byte == b'\x0C':
                    data_fragment = rx[1:]

                    # INSERTAR EL VOSTRE CODI per RX UNICAST
                    #count=len(payload) ---> Per saber quants frames s'hauran d'enviar

    # recommended behavior is to keep in TX mode while idle
    nrf.listen = False  # put the nRF24L01 is in TX mode

def send_address():
    data_to_send = b'\x0B' + address[1]    
    if has_file and has_token:
        data_to_send += b'\x03'
    elif has_file and not has_token:
        data_to_send += b'\x02'
    elif not has_file and has_token:
        data_to_send += b'\x01'
    elif not has_file and not has_token:
        data_to_send += b'\x00'

    nrf.listen = False  # ensures the nRF24L01 is in TX 

    result = nrf.send(data_to_send, True) # Enviem adreça i control byte, i posem True el no ack
    nrf.listen = True

    return result

def interpretarToken(data_token): # Chat GPT
    # Convierte los bytes a una lista de enteros
    received_int_list = list(data_token)

    # Agrupa la lista de enteros en sublistas de tamaño 2
    received_token = [received_int_list[i:i+2] for i in range(0, len(received_int_list), 2)]

    # Convierte la lista de enteros en una lista de listas de booleanos
    token = [[bool(x) for x in sublist] for sublist in received_token]

    return token    
