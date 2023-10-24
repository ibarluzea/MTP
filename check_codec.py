import chardet  # chardet helps to detect the character encoding

def read_file_with_unknown_encoding(filename):
    try:
        # Use chardet to detect the encoding
        with open(filename, 'rb') as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']

        # Now, read the file with the detected encoding
        with open(filename, 'r', encoding=encoding) as file:
            content = file.read()
            print(f"Successfully read with encoding: {encoding}")
            return content

    except UnicodeDecodeError:
        print(f"Failed with encoding: {encoding}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return encoding  # appropriate error handling based on your application's logic.

