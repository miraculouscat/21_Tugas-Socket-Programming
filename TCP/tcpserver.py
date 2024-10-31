import socket
import threading
from auth import AuthManager
from encryption_helper import EncryptionHelper

class ChatServer:
    def __init__(self, ip='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen()  
        self.clients = {}  # {client_address: (socket, username)}
        self.chatrooms = {}  # {chatroom_name: {client_address: username}}
        self.auth_manager = AuthManager()
        self.encryption_helper = EncryptionHelper(key='KEY')  # Initialize with a key for encryption
        print(f"[SERVER] Listening on {ip}:{port}")

    def start(self):
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"[NEW CONNECTION] Connected with {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            except Exception as e:
                print(f"[ERROR] An error occurred while accepting connections: {e}")

    def handle_client(self, client_socket, client_address):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    self.disconnect_client(client_socket, client_address)
                    break

                decrypted_message = self.encryption_helper.decrypt(message)
                print(f"[RECEIVED] {decrypted_message} from {client_address}")

                # Handle commands
                if decrypted_message.startswith("/register"):
                    self.register_client(decrypted_message, client_socket)
                elif decrypted_message.startswith("/login"):
                    self.login_client(decrypted_message, client_socket, client_address)
                elif decrypted_message.startswith("/join"):
                    self.join_chatroom(decrypted_message, client_address, client_socket)
                elif decrypted_message.startswith("/leave"):
                    self.leave_chatroom(decrypted_message, client_address, client_socket)
                elif decrypted_message.startswith("/list"):
                    self.list_chatrooms(client_socket)
                else:
                    # Broadcast message to current chatroom
                    if client_address in self.clients:
                        self.broadcast_message(decrypted_message, client_address)
                    else:
                        error_message = "You need to login or register first."
                        self.send_encrypted_message(error_message, client_socket)
        except ConnectionResetError:
            self.disconnect_client(client_socket, client_address)
        except Exception as e:
            print(f"[ERROR] An error occurred while handling client {client_address}: {e}")
            self.disconnect_client(client_socket, client_address)

    def register_client(self, command, client_socket):
        try:
            _, username, password = command.split()
            success, msg = self.auth_manager.register(username, password)
            self.send_encrypted_message(msg, client_socket)
        except ValueError:
            error_message = "Invalid registration command. Use: /register <username> <password>"
            self.send_encrypted_message(error_message, client_socket)

    def login_client(self, command, client_socket, client_address):
        try:
            _, username, password = command.split()
            success, msg = self.auth_manager.login(username, password)
            if success:
                self.clients[client_address] = (client_socket, username)
                welcome_message = f"WELCOME: Welcome, {username}! You are now connected."
                self.send_encrypted_message(welcome_message, client_socket)
            else:
                self.send_encrypted_message(msg, client_socket)
        except ValueError:
            error_message = "Invalid login command. Use: /login <username> <password>"
            self.send_encrypted_message(error_message, client_socket)

    def join_chatroom(self, command, client_address, client_socket):
        _, chatroom_name = command.split()
        
        # Check if the user is logged in
        if client_address not in self.clients:
            error_message = "You must log in to join a chatroom."
            self.send_encrypted_message(error_message, client_socket)
            return

        # Add client to the specified chatroom
        if chatroom_name not in self.chatrooms:
            self.chatrooms[chatroom_name] = {}
        self.chatrooms[chatroom_name][client_address] = self.clients[client_address][1]

        confirmation_message = f"You joined the chatroom '{chatroom_name}'."
        self.send_encrypted_message(confirmation_message, client_socket)

    def leave_chatroom(self, command, client_address, client_socket):
        _, chatroom_name = command.split()
        
        # Check if the user is logged in
        if client_address not in self.clients:
            error_message = "You must log in to leave a chatroom."
            self.send_encrypted_message(error_message, client_socket)
            return

        if chatroom_name in self.chatrooms and client_address in self.chatrooms[chatroom_name]:
            del self.chatrooms[chatroom_name][client_address]
            leave_message = f"You left the chatroom '{chatroom_name}'."
            self.send_encrypted_message(leave_message, client_socket)
        else:
            error_message = f"You're not in chatroom '{chatroom_name}'."
            self.send_encrypted_message(error_message, client_socket)

    def list_chatrooms(self, client_socket):
        chatroom_list = "Available chatrooms:\n" + "\n".join(self.chatrooms.keys()) if self.chatrooms else "No chatrooms available."
        self.send_encrypted_message(chatroom_list, client_socket)

    def broadcast_message(self, message, sender_address):
        sender_username = self.clients[sender_address][1]
        formatted_message = f"{sender_username}: {message}"

        # Broadcast only to clients in the sender's current chatroom(s)
        for chatroom_name, members in self.chatrooms.items():
            if sender_address in members:
                for client_address in members:
                    if client_address != sender_address:
                        self.send_encrypted_message(formatted_message, self.clients[client_address][0])

    def send_encrypted_message(self, message, client_socket):
        encrypted_message = self.encryption_helper.encrypt(message)
        client_socket.send(encrypted_message.encode('utf-8'))

    def disconnect_client(self, client_socket, client_address):
        if client_address in self.clients:
            username = self.clients[client_address][1]
            del self.clients[client_address]
            print(f"[DISCONNECTED] {username} at {client_address} disconnected.")
            # Remove client from all chatrooms
            for chatroom_name in list(self.chatrooms.keys()):
                self.chatrooms[chatroom_name].pop(client_address, None)
                if not self.chatrooms[chatroom_name]:  # If no members, remove chatroom
                    del self.chatrooms[chatroom_name]
        client_socket.close()
