import struct

def read_two_integers(file_path):
    try:
        with open(file_path, 'rb') as file:
            # Read the 16 bytes from the binary file
            data = file.read(16)

            # Ensure we have exactly 16 bytes
            if len(data) != 16:
                raise ValueError("The file does not contain exactly 16 bytes.")

            # Unpack the data into two 64-bit integers (little-endian)
            int1, int2 = struct.unpack('<QQ', data)
            return int1, int2
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
# file_path = "data.bin"
file_path="cache_info-12-26-24"
MB = 1024 * 1024
result = read_two_integers(file_path)
if result:
    print(f"The two integers are: {result[0]} and {result[1]}, or {result[0]/MB} MB and {result[1]/MB} MB")
