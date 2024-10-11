import socket
import threading
import json
import os

clients = {}

# Function to save chat history to a file
def save_chat_history(message):
    with open("chat_history.txt", "a") as file:
        file.write(message + "\n")

# Function to load users from users.json
def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as file:
            json.dump({}, file)
    with open("users.json", "r") as file:
        return json.load(file)

# Function to handle messages received from the client
def handle_messages():
    while True:
        try:
            message, client_address = server_socket.recvfrom(1024)
            decoded_message = message.decode('utf-8')
            split_message = decoded_message.split(' ', 2)
            print(f"Received message: {decoded_message} from {client_address}")

            # Process login or register
            if split_message[0] == "REGISTER":
                username = split_message[1]
                password = split_message[2]
                register_user(username, password, client_address)
            elif split_message[0] == "LOGIN":
                username = split_message[1]
                password = split_message[2]
                login_user(username, password, client_address)
            elif split_message[0] == "MSG":
                username = split_message[1]
                user_message = split_message[2]
                broadcast_message(f"{username}: {user_message}", client_address)
        except Exception as e:
            print(f"Error: {e}")
            break

# Function to send messages to all clients
def broadcast_message(message, exclude_address=None):
    for client, address in clients.items():
        if address != exclude_address:
            server_socket.sendto(message.encode('utf-8'), address)
    save_chat_history(message)
    print(f"Broadcasting message: {message}")

# Function to log in user
def login_user(username, password, client_address):
    users = load_users()
    
    if username in users and users[username] == password:
        clients[username] = client_address
        server_socket.sendto(f"LOGGED_IN {username}".encode('utf-8'), client_address)
        broadcast_message(f"{username} has joined the chatroom.", client_address)
        # Send welcome message
        server_socket.sendto("Welcome to the chatroom!".encode('utf-8'), client_address)
    else:
        server_socket.sendto("LOGIN_FAILED".encode('utf-8'), client_address)

# Function to register user
def register_user(username, password, client_address):
    users = load_users()

    if username in users:
        server_socket.sendto(f"Username {username} is already registered.".encode('utf-8'), client_address)
    else:
        users[username] = password
        with open("users.json", "w") as file:
            json.dump(users, file)
        server_socket.sendto(f"Registration successful for {username}".encode('utf-8'), client_address)

def main():
    server_ip = "0.0.0.0"  # Listen on all available interfaces
    server_port = 12345
    server_address = (server_ip, server_port)

    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)

    print(f"Server running on {server_ip}:{server_port}")
    
    threading.Thread(target=handle_messages, daemon=True).start()

    # Keep server running
    while True:
        pass

if __name__ == "__main__":
    main()
