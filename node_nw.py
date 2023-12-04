import time
import struct
import board
from digitalio import DigitalInOut
import os, glob, getpass, math
from functions_pi import *
# Al main definir la length de la address.

def node_NW(nrf,strF,isTransmitter): # FOR EACH GROUP MAIN: strF is the text file to transmit. It's the outcome of the openFile with rb such as: b'\x00\x01\x02...'
    print("NW 1")
    has_token = isTransmitter # FOR EACH GROUP: isTransmiter is a boolean that is true if and only if: I have usb + file.
    had_token = isTransmitter
    has_file = isTransmitter

    # Broadcast b"BRD" for either TX or RX, and b"0RC" for RX pipes (for the first node)
    address = [b"BRD",b"1RC"] # FOR EACH GROUP: Change the unicast address xRC. --> 0 to 7
    print("my address", address)
    my_address = [int(char) for char in address[1].decode() if char.isdigit()][0] # Extract the numeric digit from the address -> '0'

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
    print("NW starts")
    # "Main loop" of the program
    while True: # Fotre timeout voluntari
        if has_token: # Es Master
            had_token = True
            timestamp = time.time()
            print(f"I'm MASTER, timestamp: {timestamp}")
            address_list,backup_list,not_priority_list,token = neighbor_discovery(nrf, discovery_payload, address[1], address[0],token, discovery_timeout) 
            success_nodes, success = unicast_tx(nrf, strF,data_payload,ef_payload,address[1], address_list)
            print(f"Unicast TX: {success}")
            token,has_token = token_handover(nrf, token, success_nodes, backup_list, not_priority_list, token_payload, my_address)
        else: # Es Slave
            nrf.open_rx_pipe(0, address[0])  # using RX pipe 0 for broadcast
            timestamp = time.time()
            print(f"I'm SLAVE, timestamp: {timestamp}")
            has_file, has_token, token, tmp_strF = receive(nrf, address[1], backoff, has_file, had_token)
            strF = tmp_strF if tmp_strF is not None else strF
            nrf.close_rx_pipe(0)

#### Master #####


def neighbor_discovery(nrf, discovery_payload,my_address,dst_address,token, discovery_timeout):
    
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
    print("Sending Neighbour Discovery...")
    while no_received:
        nrf.listen = False # Stop listening to became a transmitter
        nrf.send(buffer_tx, True) # Send the broadcast neighbor advertise; True = No ACK expected
        nrf.listen = True # Limpiar Pipe?
        
        # Start the timer to check if its expired before having responses 
        start_time = time.time_ns()
        while (time.time_ns() - start_time) < discovery_timeout: # Wait for responses
            if nrf.available():
                neighbors.append(nrf.read()) # Read any available data we are receiving
        print("Discovery: ",neighbors)
        # If we received something, we add the received address of the responding nodes
        if neighbors: 
            for i in neighbors:
                address_n = i[0:3]
                info_byte = i[-1]
                num_address_n = [int(char) for char in address_n.decode() if char.isdigit()][0] 
                if info_byte == 0:
                    address_list.append(num_address_n) # Store the addresses of the neighbor responses with numerical IDs 
                elif info_byte == 1:
                    token[num_address_n][:] = [True, False]
                    backup_list.append(num_address_n)
                else:
                    token[num_address_n][:] = [True, True]
                    not_priority_list.append(num_address_n)

            nrf.listen = False 
            no_received = False # Stop the neighbor discovery process 
        print("Discovery address:", address_list, backup_list, not_priority_list)
    return address_list, backup_list, not_priority_list, token

    #### Unicast transmission function ####

def unicast_tx(nrf, strF,data_payload,ef_payload,my_address,address_list):

    # This function performs a unicast transmission of the file in chunks of 31 or less bits

    payload = fragmentFile(strF,31) # Fragment the whole file in chunks of 31 bytes (already implemented function? strF is File argument?)
    count=len(payload) # Compute how many frames have to be sent

    success_nodes = []

    success = False
    
    # Send the file to every neighbor responder in a sequential manner with unicast transmission 
    print(f"Address list is {address_list}")
    
    for i in address_list:
        dst_address = bytes(str(i), 'utf-8')+b"RC"
        print(f"Sending file to node {i} with address {dst_address}")
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
        
        print(f"File sent successfully to node {i}. Sending EOF...")
        # nrf.listen = False
        buffer_ef = ef_payload # Once the file has been sent, "End of File" (b'\x0E') ID is also sent
        limitRetransmitions = 10
        result = nrf.send(buffer_ef)
        while not result and limitRetransmitions:      
            result = nrf.send(buffer_ef)
            limitRetransmitions -= 1

        
        if limitRetransmitions > 0:
            success_nodes.append(i)
            success = True
            print("EOF sent successfully to node {i}")
        
    return success_nodes, success


    # This function does the token handshake and returns a token in a list format
def token_handover(nrf, token, address_list, backup_list, not_priority_list, token_payload, my_address):
    priority = []
    token[int(my_address)][:] = [True,True] # I have the file and token.
    for i in address_list:
        # NOTA: Falta acabar de fer les condicions
        if (token[i][1]) == False: # Never had the token. (If true, it must have the file)
            priority.append(i)
    print(f"Address list (handover): {address_list}")
    print("backup list:", backup_list)
    print("not prior list:", not_priority_list)
    print("To Send File: ", priority)
    priority.extend(backup_list)
    print("BackupList: ", priority)
    priority.extend(not_priority_list)
    
    
    print(f"Token: {token}")
    print(f"Priority list: {priority}")
    
    result = False
    while not result:
        for i in priority:
            dst_address = bytes(str(i), 'utf-8')+b"RC"
            print(f"Trying to send token to node {i} with address {dst_address}")
            nrf.open_tx_pipe(dst_address)
            flat_list = [item for sublist in token for item in sublist]
            int_list = [int(x) for x in flat_list]
            token_bytes = bytes(int_list)
            buffer_tx = token_payload+token_bytes
            result = nrf.send(buffer_tx, False, 5)
            if result:
                print(f"Token sent successfully to node {i}")
                break
    print(not result)
    return token, not result

    #### Slave ####

def receive(nrf, my_address, backoff, has_file, had_token):
    keep_listening = True
    has_token = False
    msg = b""
    print("listening...")
    strF = None
    while keep_listening:
        nrf.listen = True  # put radio into RX mode and power up
        if nrf.available():
            # grab information about the received payload
            payload_size, pipe_number = (nrf.any(), nrf.pipe)
            buffer_rx = nrf.read() #Clears flags & empties RX FIFO, saves bytes in rx
            print(f"Received {payload_size} bytes on pipe {pipe_number}: {buffer_rx}")
            if pipe_number == 0: # S'ha rebut a la pipe de broadcast -> Neighbour Discovery
                msg = b""
                address_received = buffer_rx[1:4] 
                print(f"Received neighbour discovery from address {address_received}")
                nrf.open_tx_pipe(address_received)
                time.sleep(backoff)
                send_address(nrf, my_address, has_file, had_token)
                # 3) Rebo algo unicast, mirar quin tipo de paquet arriba
            if pipe_number == 1: # S'ha rebut a la pipe de unicast -> O fitxer o Token
                type_byte = buffer_rx[0] # Agafar el primer byte que indica tipus de paquet
                print(f"Packet type: {type_byte}")
                if type_byte == 13: # Token
                    has_token = True
                    keep_listening = False
                    token = interpretarToken(buffer_rx[1:])
                    print(f"Token received: {token}")
                    print(f"I'm master {has_token}")

                elif type_byte == 14:
                    try:
                        pth = None
                        while pth is None:
                            pth = getUSBpath()
                            if pth is None:
                                time.sleep(0.3)  # Short delay to avoid excessive CPU usage
                    except:
                        print("ª")
                    writeFile(pth+"/MTP-F23-NM-A-RX.txt", msg)
                    
                    print(f"EOF received. Writing file to USB...")
                    strF = msg
                    msg = b""
                    has_file = True
                elif type_byte == 12:
                    msg += buffer_rx[1:] # Què és aqui "rx"?
                    print(f"Adding payload to message...")
            
    return has_file, has_token, token, strF
                        
def send_address(nrf, address, has_file, had_token):
    data_to_send = address    
    if has_file and had_token: # has token és si és master o no, s'ha d'usar una altra var
        data_to_send += b'\x02'
    elif has_file and not had_token:
        data_to_send += b'\x01'
    else:
        data_to_send += b'\x00'

    nrf.listen = False  # ensures the nRF24L01 is in TX 
    print(f"Neighbour advertise sent with data {data_to_send}")
    result = nrf.send(data_to_send, True) # Enviem adreça i control byte, i posem True el no ack
    nrf.listen = True 
        
def interpretarToken(data_token): # Chat GPT
    received_int_list = list(data_token)
    received_token = [received_int_list[i:i+2] for i in range(0, len(received_int_list), 2)]
    token = [[bool(x) for x in sublist] for sublist in received_token]
    return token
        

def fragmentFile(string, length):
    return list(string[0+i: length+i] for i in range(0, len(string), length))
