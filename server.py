import socket
import threading
import json
import os

clients = {}

# Fungsi untuk menyimpan chat history ke file
def save_chat_history(message):
    with open("chat_history.txt", "a") as file:
        file.write(message + "\n")

# Fungsi untuk memuat user dari users.json
def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as file:
            json.dump({}, file)
    with open("users.json", "r") as file:
        return json.load(file)

# Fungsi untuk menangani pesan yang diterima dari client
def handle_messages(server_socket):
    while True:
        try:
            message, client_address = server_socket.recvfrom(1024)
            decoded_message = message.decode('utf-8')
            split_message = decoded_message.split(' ', 2)

            # Proses login atau register
            if split_message[0] == "REGISTER":
                username = split_message[1]
                password = split_message[2]
                register_user(username, password, server_socket, client_address)
            elif split_message[0] == "LOGIN":
                username = split_message[1]
                password = split_message[2]
                login_user(username, password, server_socket, client_address)
            elif split_message[0] == "MSG":
                username = split_message[1]
                user_message = split_message[2]
                broadcast_message(f"{username}: {user_message}", client_address)
        except Exception as e:
            print(f"Error: {e}")
            break

# Fungsi untuk mengirim pesan ke semua client
def broadcast_message(message, exclude_address=None):
    for client, address in clients.items():
        if address != exclude_address:
            server_socket.sendto(message.encode('utf-8'), address)
    save_chat_history(message)
    print(message)

# Fungsi untuk login user
def login_user(username, password, server_socket, client_address):
    users = load_users()
    
    if username in users and users[username] == password:
        clients[username] = client_address
        server_socket.sendto(f"LOGGED_IN {username}".encode('utf-8'), client_address)
        broadcast_message(f"{username} telah bergabung ke chatroom.", client_address)
        # Mengirim pesan selamat datang
        server_socket.sendto("Halo, selamat datang di chatroom!".encode('utf-8'), client_address)
    else:
        server_socket.sendto("LOGIN_FAILED".encode('utf-8'), client_address)

# Fungsi untuk register user
def register_user(username, password, server_socket, client_address):
    users = load_users()

    if username in users:
        server_socket.sendto(f"Username {username} sudah terdaftar.".encode('utf-8'), client_address)
    else:
        users[username] = password
        with open("users.json", "w") as file:
            json.dump(users, file)
        server_socket.sendto(f"Registrasi berhasil untuk {username}".encode('utf-8'), client_address)

def main():
    server_ip = "167.205.0.226"  # Menggunakan IP publik
    server_port = 12345
    server_address = (server_ip, server_port)

    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)

    print(f"Server berjalan di {server_ip}:{server_port}")
    
    threading.Thread(target=handle_messages, daemon=True).start()

    # Agar server tetap berjalan
    while True:
        pass

if __name__ == "__main__":
    main()
