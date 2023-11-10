def compress(msg):

    dictionary = {}
    output = []
    buffer = ""
# Creant el diccionari per UNICODE (amb ascii es de 256) --> NO ESTAN TOTS ELS CARACTERS, PERO ESQUE HI HAN MES DE 100000.
    for i in range(5000):
      dictionary[chr(i)] = i
    next_code = 5001


    for i in msg:
        buffer += i # Miro el seguent caracter i del msg.
        if buffer not in dictionary:  #Afegeixo al diccionari i al output la seq no guardada -->.
            output.append(dictionary[buffer[:-1]])
            dictionary[buffer] = next_code
            next_code += 1
            buffer = i

    output.append(dictionary[buffer]) # String que conforma el output: Llista dels index del diccionari que envio.
    serialized_data = [num.to_bytes(2, byteorder='big') for num in output]
    return serialized_data

def decompress(compressed_data):

    compressed_data = [int.from_bytes(byte,byteorder='big') for byte in compressed_data]

    dictionary = {i: chr(i) for i in range(5000)} # Es pot fer també així i queda més compacte, same que el compressor.
    output = []
    buffer = ""
    next_code = 5001

    for j in compressed_data:
        if j not in dictionary:
            entry = buffer + buffer[0]  # Si surt això el canal ens fastidia la compressió i no podem descomprimir.
        else:
            entry = dictionary[j]
        output.append(entry)
        if buffer:
            dictionary[next_code] = buffer + entry[0]
            next_code += 1
        buffer = entry

    return ''.join(output)
