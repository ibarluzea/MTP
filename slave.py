import time
import struct
import board
from digitalio import DigitalInOut
import os, glob, getpass, math
from subprocess import check_output
from circuitpython_nrf24l01.rf24 import RF24
import spidev

has_token = False
has_file = False

def slave(nrf):
    keep_listening = True

    address_length = 3
    nrf.address_length = address_length

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
