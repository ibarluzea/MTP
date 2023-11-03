###############################################################################
#########################   LIBRARIES IMPORT    ###############################
###############################################################################
import RF24
import time
import struct
import digitalio as dio
import board
import math

###############################################################################
#########################   INIZIALIZATION BLOCK    ###########################
###############################################################################


########### FLAGS INIZIALIZATION #########

state = 0 # 1->TX 0->RX
msg = "Hola bon dia"



pipes = [0xE8, 0xE8, 0xF0, 0xF0, 0xE1] #TODO: Definir Pipes
pipesbytes = bytearray(pipes)
payloadSize= 31; #bytes
ce = dio.DigitalInOut(board.D22)
csn = dio.DigitalInOut(board.D08)
radio = RF24.RF24()
radio.begin(ce, csn)
radio.setPALevel(RF24.RF24_PA_MAX)
radio.setDataRate(RF24.RF24_250KBPS)
radio.setRetries(3,5) # TODO: Falta definir setRetries (uint8_t delay, uint8_t count) Set the number and delay of retries upon failed submit. (Delay is the num*250us)
radio.setChannel(0x4c) #TODO: canviar channel al que ens assignin

radio.setAutoAck(True)
radio.flush_rx()



###############################################################################
#########################   TRANSMISSION FUNCTION    ##########################
###############################################################################

def transmit(msg, N_packets):

########### TRANSMISSION INITIALIZATION #########
    radio.stopListening()  # Put radio in TX mode (Used also for power saving)
    print("Starting transmission of ", N_packets)
    #Set address of RX node into a TX pipe
    radio.openWritingPipe(1, pipesbytes) #openWritingPipe (uint8_t number, uint64_t address)
    radio.powerUp() #Leave low-power mode - making radio more responsive.
    sent_packets = 0 #Initialization of the counter

    while sent_packets < N_packets:
# Transmisió dels N_packets -  1 primers packets
        if sent_packets < N_packets - 1:
            flag_last = 0;
            buffer = msg[sent_packets*payloadSize : (sent_packets + 1)*payloadSize -1] + flag_last
            print(radio.write(buffer))
        else:
            flag_last = 1
            remaining_msg = b'~'*(length(msg) - sent_packets*payloadSize) #Add redundant data to get 32 byte payload
            buffer = msg[sent_packets*payloadSize : ] + remaining_msg + flag_last
            print(radio.write(buffer))
        sent_packets += 1
        time.sleep(1)
        


###############################################################################
#########################   RECEPTION FUNCTION    ##########################
###############################################################################

def receive(): #Returns file with all data received

########### RECEPTION INITIALIZATION #########
    print("Reception mode, waiting for transmission")
    #Pipe number: The data pipe to use for RX transactions. Range: [0, 5].
    #nrf.open_rx_pipe(pipe_number, address_of_RX)
    radio.openReadingPipe(1, pipesbytes)
    radio.startListening()  
    flag_last = 0
    received_packets = 0
    radio.powerDown()

############# DATA PAYLOAD OBTANTION  ###########
    #Repeat until flag_last_packet = 1 or timer ends
    while not flag_last:
        while not radio.available()
            time.sleep(0.3)
        recv_buffer = bytearray([])
        recv_buffer = radio.read(payloadSize + 1)
        flag_last = recv_buffer[-1]
        print("Received paquet:")
        print(recv_buffer[0:length(recv_buffer) -1])
        
        
        if flag_last # si es ultim pck hem de treure empty msg
            print("Last Packet Received")
            


###############################################################################
#########################   MAIN FUNCTION    ##################################
###############################################################################

while True:
#--------------- Transmition (state = 1) -----------------
    if state:
        N_packets = math.ceil(length(msg)/payloadSize)
        transmit(msg, N_packets)
#--------------- Receive (state = 0) -----------------
    else:
        receive()
        
    