import time
import struct
import board
from digitalio import DigitalInOut
import os, glob, getpass, math
from subprocess import check_output
from circuitpython_nrf24l01.rf24 import RF24
import spidev

# Al main definir la length de la address.

def node_NW(nrf,strF,isTransmitter): # FOR EACH GROUP MAIN: strF is the text file to transmit. It's the outcome of the openFile with rb such as: b'\x00\x01\x02...'

  has_token = isTransmitter # FOR EACH GROUP: isTransmiter is a boolean that is true if and only if: I have usb + file.
  had_token = isTransmitter
  has_file = isTransmitter

  # Broadcast b"BRD" for either TX or RX, and b"0RC" for RX pipes (for the first node)
  address = [b"BRD",b"0RC"] # FOR EACH GROUP: Change the unicast address xRC. --> 0 to 7
  my_address = [int(char) for char in address[1].decode() if char.isdigit()] # Extract the numeric digit from the address -> '0'

  # Token list initialization
  token =[[False, False],[False, False],
          [False, False],[False, False],
          [False, False],[False, False],
          [False, False],[False, False]]


  # Time variables
  discovery_timeout = 24e6 # with respect nanoseconds
  backoff = 3/1000 * my_address
  
  # Packet identifiers (corresponding to their first Byte)
  discovery_payload = b'\x0A'
  data_payload = b'\x0C'
  token_payload = b'\x0D'
  ef_payload = b'\x0E'

  nrf.open_rx_pipe(1, address[1]) # Open the RX pipe 1 to receive packets to unicast b"0RC" RX address

  # "Main loop" of the program
  while True: # Fotre timeout voluntari
    if has_token: # Es Master
      had_token = True
      address_list,backup_list,not_priority_list,token = neighbor_discovery(discovery_payload, address[1], address[0],token) 
      success_nodes = unicast_tx(strF,data_payload,ef_payload,address[1], address_list)
      token,has_token = token_handover(token, success_nodes, backup_list, not_priority_list, token_payload)
    else: # Es Slave
      nrf.open_rx_pipe(0, address[0])  # using RX pipe 0 for broadcast
      has_file, has_token, token, strF = receive(address[1], backoff, has_file, had_token)
      nrf.close_rx_pipe(0, address[0])

#### Master #####


def neighbor_discovery(discovery_payload,my_address,dst_address,token):
  
  # This function does the neighbor discovery process and returns a list with the numerical "IDs"
  #  of the responders (1,2,...)

  nrf.open_tx_pipe(dst_address) # MUST use pipe 0 and address[0] (i.e. TX using b"BRD" address)
  buffer_tx = discovery_payload + my_address # Concatenate the b'\x0A' with our address to send the buffer
  neighbors = []
  address_list = []
  backup_list = []
  not_priority_list = []
  
  # While we not receive any responses from adjacent nodes:
  no_received = True
  while no_received:
    nrf.listen = False # Stop listening to became a transmitter
    nrf.send(buffer_tx, True) # Send the broadcast neighbor advertise; True = No ACK expected
    nrf.listen = True # Limpiar Pipe?
    
    # Start the timer to check if its expired before having responses 
    start_time = time.time_ns()
    while (time.time_ns() - start_time) < discovery_timeout: # Wait for responses
      if nrf.available():
        neighbors.append(nrf.read()) # Read any available data we are receiving
     
    # If we received something, we add the received address of the responding nodes
    if neighbors: 
      for i in neighbors:
        address_n = i[0:3]
        info_byte = i[-1]
        num_address_n = [int(char) for char in address_n.decode() if char.isdigit()][0] 
        if info_byte == 0:
          address_list.append(num_address_n) # Store the addresses of the neighbor responses with numerical IDs 
        elif: info_byte == 1:
          token[num_address_n][:] = [True, False]
          backup_list.append(num_address_n)
        else:
          token[num_address_n][:] = [True, True]
          not_priority_list.append(num_address_n)

      nrf.listen = False 
      no_received = False # Stop the neighbor discovery process 
  
  return address_list, backup_list, not_priority_list, token

#### Unicast transmission function ####
def unicast_tx(strF,data_payload,ef_payload,my_address,address_list):

  # This function performs a unicast transmission of the file in chunks of 31 or less bits

  payload = fragmentFile(strF,31) # Fragment the whole file in chunks of 31 bytes (already implemented function? strF is File argument?)
  count=len(payload) # Compute how many frames have to be sent

  success_nodes = []
  
  # Send the file to every neighbor responder in a sequential manner with unicast transmission 
  for i in address_list:
    dst_address = bytes(str(i))+b"RC"
    nrf.open_tx_pipe(dst_address) # Open the TX towards the target neighbor
    result = False

    for j in range(count):
      limitRetransmitions = 10
      buffer = data_payload + payload[j]
      result = nrf.send(buffer)
      while not result and limitRetransmitions:      
        result = nrf.send(buffer)
        limitRetransmitions -= 1
      if limitRetransmitions == 0:
        break
    
    if limitRetransmitions == 0:
      continue
      
    # nrf.listen = False
    buffer_ef = ef_payload # Once the file has been sent, "End of File" (b'\x0E') ID is also sent
    limitRetransmitions = 10
    result = nrf.send(buffer_ef)
    while not result and limitRetransmitions:      
      result = nrf.send(buffer_ef)
      limitRetransmitions -= 1

    
    if limitRetransmitions > 0:
      success_nodes.append(i)
      
  return success_nodes


# This function does the token handshake and returns a token in a list format
def token_handover(token, address_list, backup_list, not_priority_list, token_payload):
  priority = []
  token[int(my_address[0])][:] = [True,True] # I have the file and token.
  for i in address_list:
    # NOTA: Falta acabar de fer les condicions
    if (token[i][1]) == False # Never had the token. (If true, it must have the file)
      priority.append(i)

  priority.extend(backup_list)
  priority.extend(not_priority_list)

  for i in priority:
    dst_address = bytes(str(i))+b"RC"
    nrf.open_tx_pipe(dst_address)
    flat_list = [item for sublist in token for item in sublist]
    int_list = [int(x) for x in flat_list]
    token_bytes = bytes(int_list)
    buffer_tx = token_payload+token_bytes
    result = nrf.send(buffer_tx, False, 5)
    if result:
      break
  return token, not result

#### Slave ####

def receive(my_address, backoff, has_file, had_token):
  keep_listening = True
  has_token = False
  msg = b""
  while keep_listening:
    nrf.listen = True  # put radio into RX mode and power up
    if nrf.available():
      # grab information about the received payload
      payload_size, pipe_number = (nrf.any(), nrf.pipe)
      buffer_rx = nrf.read() #Clears flags & empties RX FIFO, saves bytes in rx
      if pipe_number == 0: # S'ha rebut a la pipe de broadcast -> Neighbour Discovery
        msg = b""
        address_received = buffer_rx[1:4] 
        nrf.open_tx_pipe(address_received)
        time.sleep(backoff)
        send_address(my_address, has_file, had_token)
        # 3) Rebo algo unicast, mirar quin tipo de paquet arriba
      if pipe_number == 1: # S'ha rebut a la pipe de unicast -> O fitxer o Token
        type_byte = buffer_rx[0] # Agafar el primer byte que indica tipus de paquet
        if type_byte == b'\x0D': # Token
          has_token = True
          keep_listening = False
          token = interpretarToken(buffer_rx[1:])
          
        elif type_byte == b'\x0E': # End of Transmission
                    # PROCESSAR TEXT, ESCRIURE, ETC
                    # Un cop s'ha rebut tot el fitxer, escriure els bytes al USB, cadascu amb la seva funcio d'escriure al USB
                    # Codi d'encendre led VERD
                    # Actualitzar el token NOMES es fa al master.
          WriteFile2USB(msg) # Quadrar cada grup la seva funció.
          strF = msg
          msg = b""
          has_file = True
        elif type_byte == b'\x0C':
          msg += buffer_rx[1:] # Què és aqui "rx"?
        
  return has_file, has_token, token, strF
                    
def send_address(address, has_file, had_token):
  data_to_send = address    
  if has_file and had_token: # has token és si és master o no, s'ha d'usar una altra var
    data_to_send += b'\x02'
  elif has_file and not had_token:
    data_to_send += b'\x01'
  else:
    data_to_send += b'\x00'

  nrf.listen = False  # ensures the nRF24L01 is in TX 
  result = nrf.send(data_to_send, True) # Enviem adreça i control byte, i posem True el no ack
  nrf.listen = True 
    
def interpretarToken(data_token): # Chat GPT
    # Convierte los bytes a una lista de enteros
    received_int_list = list(data_token)

    # Agrupa la lista de enteros en sublistas de tamaño 2
    received_token = [received_int_list[i:i+2] for i in range(0, len(received_int_list), 2)]

    # Convierte la lista de enteros en una lista de listas de booleanos
    token = [[bool(x) for x in sublist] for sublist in received_token]

    return token
