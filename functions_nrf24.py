def master(nrf, payload):  # count = 5 will only transmit 5 packets
    """Transmits an incrementing integer every second"""
    nrf.listen = False  # ensures the nRF24L01 is in TX mode
    zero_timer = time.monotonic_ns()
    result = False
#   print(nrf.is_lna_enabled())
    count=len(payload)
    for i in range(count):
        # use struct.pack to structure your data
        # into a usable payload
        limit = 100
        print(type(payload[i]))
        print(payload[i])
        buffer = payload[i]
        # "<f" means a single little endian (4 byte) float value.
        start_timer = time.monotonic_ns()  # start timer
        result = nrf.send(buffer, False, 10)
        
        while not result and limit: 
            result = nrf.send(buffer, False, 10)
            time.sleep(0.5)
            limit -= 1
        end_timer = time.monotonic_ns()  # end timer
        
        if not result:
            print("send() failed or timed out")
        else:
            print(
                "Transmission successful! Time to Transmit:",
                "{} us. Sent: {}".format((end_timer - start_timer) / 1000, payload[i]),
            )
        print("Transmission rate: ", (((len(payload)*32)*8)/((end_timer-zero_timer)/1e9)))
        
def slave(nrf, timeout, codec):
    """Polls the radio and prints the received value. This method expires
    after 6 seconds of no received transmission"""
    nrf.listen = True  # put radio into RX mode and power up
    msg = ""
    start = time.monotonic()
    while (time.monotonic() - start) < timeout:
        if nrf.available():
            # grab information about the received payload
            payload_size, pipe_number = (nrf.any(), nrf.pipe)
            # fetch 1 payload from RX FIFO
            buffer = nrf.read()  # also clears nrf.irq_dr status flag
            # expecting a little endian float, thus the format string "<f"
            # buffer[:4] truncates padded 0s if dynamic payloads are disabled
            
           # Here there is another option
            #msg += buffer#.decode("utf-8")
            msg.extend(buffer)
            # print details about the received packet
            print(
                "Received {} bytes on pipe {}: {}".format(
                    payload_size, pipe_number, msg
                )
            )
            start = time.monotonic()

    # recommended behavior is to keep in TX mode while idle
    nrf.listen = False  # put the nRF24L01 is in TX mode
        
