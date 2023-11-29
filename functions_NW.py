import time

def masterNW(nrf,timeout,payload,codec): 

  nrf.address_length = 3
  address = [b"BRD",b"0RC"] #Change the unicast address xRC for every group. --> 0 to 7

  discovery_timeout = 8e6 # with respect nanoseconds
  ack_timeout = 992e-6
  
  token =[[True, False],[False, False],[False, False],[False, False],[False, False],[False, False] ,[False, False] ,[False, False]]

  discovery_payload = address[0] + b'\x0A'
  data_payload = b'\x0C'
  token_payload = b'\x0D'

  # 1) Neighbor disc
  nrf.open_tx_pipe(address[0]) #uses pipe 0, address 0.
  nrf.open_rx_pipe(1, address[1]) 
  buffer_tx = discovery_payload 
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
  
  norf.close_rx_pipe(1)
  address_list = [int(char) for char in neighbors.decode() if char.isdigit()] # Get from a b"1RC5RC8RC" --> [1,5,8]
  my_address = [int(char) for char in address[1].decode() if char.isdigit()]
# 2) Unicast Transmisions

nrf.open_rx_pipe(2, address[1]) # També podria ser la pipe 1 a priori.
for i in address_list:
  dst_address = bytes(str(i, codec))+b"RC"
  nrf.open_tx_pipe(dst_address) 
  
  # INSERTAR EL VOSTRE CODI per TX UNICAST, LA CONFORMACiÓ de la PAYLOAD ha d'incloure l'identifier: b'\x0C'
  #count=len(payload) ---> Per saber quants frames s'hauran d'enviar
  
  #for i in range(count): --> Enviar frame a frame.
  # ...  
  #Al final del nested for: Enviem packet End Of Transmision.
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

