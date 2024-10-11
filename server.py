import socket
import threading
import queue
import hashlib
import os

# Store valid users for authentication
valid_users = {"user1": "password1", "user2": "password2"}

# Store clients and their usernames
clients = {}
recvPackets = queue.Queue()

# Caesar Cipher for basic encryption
def caesar_cipher_encrypt(text, shift=3):
    encrypted = ""
    for char in text:
        if char.isalpha():
            shift_by = shift % 26
            encrypted += chr((ord(char) + shift_by - 65) % 26 + 65)
        else:
            encrypted += char
    return encrypted

def caesar_cipher_decrypt(text, shift=3):
    return caesar_cipher_encrypt(text, -shift)

# Checksum generation for integrity verification
def generate_checksum(message):
    return hashlib.sha256(message.encode('utf-8')).hexdigest()

def verify_checksum(message, received_checksum):
    return generate_checksum(message) == received_checksum

# Save message to file
def save_message_to_file(message, filename="chat_history.txt"):
    with open(filename, "a") as file:
        file.write(message + "\n")

def load_chat_history(filename="chat_history.txt"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return file.readlines()
    return []

# Authenticate users
def authenticate(username, password):
    return valid_users.get(username) == password

# Function to receive data
def recv_data(sock):
    while True:
        data, addr = sock.recvfrom(2048)
        recvPackets.put((data, addr))

# Server function
def run_server():
    host = socket.gethostbyname(socket.gethostname())
    port = 12345
    print(f'Server hosting on IP -> {host}')
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print('Server running...')
    threading.Thread(target=recv_data, args=(s,)).start()

    while True:
        while not recvPackets.empty():
            data, addr = recvPackets.get()
            data = data.decode('utf-8')

            # First message expected to be authentication
            if addr not in clients:
                try:
                    username, password = data.split(',')
                    if authenticate(username, password):
                        clients[addr] = username
                        print(f'Client {username} authenticated from {addr}')
                        s.sendto("Authentication successful".encode('utf-8'), addr)
                        for msg in load_chat_history():
                            s.sendto(msg.encode('utf-8'), addr)  # Send chat history
                    else:
                        s.sendto("Authentication failed".encode('utf-8'), addr)
                        print(f'Failed authentication attempt from {addr}')
                except ValueError:
                    print(f'Invalid authentication attempt from {addr}')
                continue

            # Message received from authenticated client
            username = clients[addr]
            print(f"Received from {username} -> {data}")
            
            # Verify checksum
            try:
                msg, checksum = data.rsplit(',', 1)
                if not verify_checksum(msg, checksum):
                    print(f"Message integrity check failed from {username}")
                    continue
            except ValueError:
                print(f"Malformed message from {username}")
                continue

            # Save message to file
            save_message_to_file(data)

            # Forward message to all other clients
            for client_addr in clients:
                if client_addr != addr:
                    encrypted_msg = caesar_cipher_encrypt(f"[{username}] -> {msg}")
                    s.sendto(f"{encrypted_msg},{checksum}".encode('utf-8'), client_addr)

    s.close()

if __name__ == '__main__':
    run_server()
