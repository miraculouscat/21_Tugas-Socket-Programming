import socket
import threading
import hashlib
import os

# Fungsi untuk enkripsi Caesar Cipher
def caesar_cipher_encrypt(text, shift=3):
    encrypted = ""
    for char in text:
        if char.isalpha():
            shift_by = shift % 26
            encrypted += chr((ord(char) + shift_by - 65) % 26 + 65)
        else:
            encrypted += char
    return encrypted

# Fungsi untuk dekripsi Caesar Cipher
def caesar_cipher_decrypt(text, shift=3):
    decrypted = ""
    for char in text:
        if char.isalpha():
            shift_by = shift % 26
            decrypted += chr((ord(char) - shift_by - 65) % 26 + 65)
        else:
            decrypted += char
    return decrypted

# Fungsi untuk menghitung checksum SHA256 untuk pesan
def generate_checksum(message):
    return hashlib.sha256(message.encode('utf-8')).hexdigest()

# Fungsi untuk menerima pesan dari server
def receive_data(sock):
    while True:
        try:
            data, addr = sock.recvfrom(2048)  # Menerima data dari server
            decrypted_msg, checksum = data.decode('utf-8').rsplit(',', 1)
            decrypted_msg = caesar_cipher_decrypt(decrypted_msg)
            print(f"Received -> {decrypted_msg}")
        except:
            pass

# Fungsi utama untuk client
def run_client(server_ip):
    host = socket.gethostbyname(socket.gethostname())  # IP client
    port = int(input("Enter client port number (between 6000 and 10000): "))  # Port client

    # Menghubungkan client ke server
    server = (server_ip, 5000)  # Alamat server dan portnya
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    # Meminta username dan password dari user
    username = input('Enter your username: ')
    password = input('Enter your password: ')
    s.sendto(f"{username},{password}".encode('utf-8'), server)  # Mengirim username dan password ke server

    # Menunggu respons autentikasi dari server
    response, _ = s.recvfrom(1024)
    response = response.decode('utf-8')
    if "Authentication successful" in response:
        print("Successfully authenticated. Welcome to the chatroom!")
    else:
        print("Authentication failed. Exiting.")
        s.close()
        return

    # Memulai thread untuk menerima pesan
    threading.Thread(target=receive_data, args=(s,)).start()

    # Loop utama untuk mengirim pesan
    while True:
        msg = input()  # Input pesan dari pengguna
        if msg == 'exit':  # Jika pengguna mengetik 'exit', keluar dari chat
            print("Exiting the chatroom.")
            break

        # Menghitung checksum dan mengenkripsi pesan sebelum dikirim ke server
        checksum = generate_checksum(msg)
        encrypted_msg = caesar_cipher_encrypt(msg)
        s.sendto(f"{encrypted_msg},{checksum}".encode('utf-8'), server)

    s.close()
    os._exit(1)  # Menutup client

if __name__ == '__main__':
    server_ip = input("Enter server IP address: ")  # Meminta alamat IP server dari pengguna
    run_client(server_ip)
