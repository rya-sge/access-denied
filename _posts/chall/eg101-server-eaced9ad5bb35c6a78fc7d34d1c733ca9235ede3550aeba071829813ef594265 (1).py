import socket
import threading
import random
import const
import binascii

VERBOSE = True

import random

# Performs modular exponentiation.
def mod_exp(base, exp, mod):
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result

# Calculate the greatest common divisor (gcd) of a and b.
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# Generates ElGamal public and private keys.
def generate_keys(prime):
    g = random.randint(2, prime - 1)
    private_key = random.randint(1, prime - 2)
    public_key = mod_exp(g, private_key, prime)
    return (prime, g, public_key), private_key

# Encrypts a message using the public key.
def encrypt(public_key, message):
    """"""
    prime, g, h = public_key
    y = random.randint(1, prime - 2)
    c1 = mod_exp(g, y, prime)
    s = mod_exp(h, y, prime)
    c2 = (message * s) % prime
    return c1, c2

# Decrypt a ciphertext using the private key.
def decrypt(private_key, public_key, ciphertext):
    c1, c2 = ciphertext
    prime, g, _ = public_key
    s = mod_exp(c1, private_key, prime)
    s_inv = pow(s, -1, prime)  # Modular multiplicative inverse
    message = (c2 * s_inv) % prime
    return message


def get_data(client_socket, client_address):
    data = client_socket.recv(1024)
    if not data:
        if VERBOSE: print(f"Connection with {client_address} closed.")
        return None
    message = data.decode().strip()
    if VERBOSE: print(f"Received from {client_address}: {message}")
    return message


def msg_to_int(msg):
    hex_string = msg.encode("utf-8").hex()
    print("hex_string before",hex_string)
    return int(hex_string, 16)


def decrypt_msg(Km, gy, x):
    # Compute the original plaintext in integer format
    K = mod_exp(gy, x, PRIME)
    K_inv = pow(K, -1, PRIME)  # Modular multiplicative inverse
    message = (Km * K_inv) % PRIME

    # int to string (inverse of msg_to_int)
    hex_string = hex(int(message))[2:]  # Remove '0x' prefix
    if len(hex_string) % 2 != 0:
        hex_string = "0" + hex_string  # Ensure even length

    print("hex_string",hex_string)
    byte_string = binascii.unhexlify(hex_string)
    return byte_string.decode("utf-8")


def send_msg(msg, client_socket):
    client_socket.sendall(msg.encode())


PRIME = 9359920040557521287640188225332795304009466497049561443299088499643424200245588313061025165619294040667209797774612400137263138479335798194382908649492031


def handle_client(client_socket, client_address):
    if VERBOSE: print(f"New connection from {client_address}")
    # Compute the generator
    g = random.randint(2, PRIME - 2)

    client_socket.sendall(f"P = {PRIME}, g = {g}\n".encode())
    client_socket.settimeout(50)
    try:
        try:
            # Bob sends g^x
            x = random.randint(2, PRIME - 2)
            value = mod_exp(g, x, PRIME)
            send_msg(f"I'm Bob, I want the flag, here's g^x (mod p): {value}\n", client_socket)

            # Mallory can alter the message that is sent from Bob to Alice if she wants
            message = get_data(client_socket, client_address)
            if message == None:
                return

            gx = int(message.split(" ")[-1].strip())
            # Alice now have g^x (mod p) from Bob, she will fist compute g^y (mod p), then K = (g^x)^y (mod p)
            y = random.randint(2, PRIME - 2)
            gy = mod_exp(g, y, PRIME)
            K = mod_exp(gx, y, PRIME)

            # Alice can encrypt her message by using K*m (mod p)
            message = msg_to_int(const.FLAG)
            Km = (message * K) % PRIME
            # Alice sends the ciphertext Km to Bob
            send_msg(f"I'm Alice, here's g^y (mod p): {gy} , here's Km (mod p): {Km}\n", client_socket)

            # Mallory can alter the message that is sent from Alice to Bob
            message = get_data(client_socket, client_address)
            if message == None:
                return

            # Bob can now decrypt the ciphertext
            gy = int(message.split(" ")[6].strip())
            Km = int(message.split(" ")[-1].strip())
            decrypted_message = decrypt_msg(Km, gy, x)
            #print(len(decrypted_message.strip()))
            assert(len(decrypted_message.strip()) == 16)
            #print(decrypted_message)
            send_msg(f"I'm Bob, thanks and have a nice day! 🌞\n", client_socket)


        except socket.timeout:
            if VERBOSE: print(f"Timeout: No data received from {client_address}. Closing connection.")
            client_socket.sendall(b"Server timeout, goodbye!\n")
            return
    except Exception as e:
        if VERBOSE: print(f"Error with client {client_address}: {e}")
    finally:
        client_socket.close()
        if VERBOSE: print(f"Connection with {client_address} ended.")



def start_server(host='0.0.0.0', port=9999):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    if VERBOSE: print(f"Server listening on {host}:{port}")
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        if VERBOSE: print("\nServer shutting down...")
    except Exception as e:
        if VERBOSE: print(f"An error occurred: {e}")
    finally:
        server_socket.close()
        if VERBOSE: print("Socket closed.")

if __name__ == "__main__":
    start_server()
