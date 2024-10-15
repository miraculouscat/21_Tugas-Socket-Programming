import socket
import threading
from auth import AuthManager
from encryption_helper import EncryptionHelper

class ChatServer:
    def __init__(self, ip='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((ip, port))
        self.clients = {}  # Dictionary to store client address and usernames
        self.auth_manager = AuthManager()
        self.encryption_helper = EncryptionHelper(shift=3)  # Ensure shift is consistent with client
        print(f"[SERVER] Listening on {ip}:{port}")

    def start(self):
        while True:
            message, client_address = self.server_socket.recvfrom(1024)
            threading.Thread(target=self.handle_client, args=(message, client_address)).start()

    def handle_client(self, message, client_address):
        decrypted_message = self.encryption_helper.decrypt(message.decode('utf-8'))
        print(f"[RECEIVED] {decrypted_message} from {client_address}")

        if decrypted_message.startswith("/register"):
            self.register_client(decrypted_message, client_address)
        elif decrypted_message.startswith("/login"):
            self.login_client(decrypted_message, client_address)
        else:
            if client_address in self.clients:
                self.broadcast_message(decrypted_message, client_address)
            else:
                error_message = "You need to login or register first."
                self.send_encrypted_message(error_message, client_address)

    def register_client(self, command, client_address):
        try:
            _, username, password = command.split()
            success, msg = self.auth_manager.register(username, password)
            self.send_encrypted_message(msg, client_address)
        except ValueError:
            error_message = "Invalid registration command. Use: /register <username> <password>"
            self.send_encrypted_message(error_message, client_address)

    def login_client(self, command, client_address):
        try:
            _, username, password = command.split()
            success, msg = self.auth_manager.login(username, password)
            if success:
                self.clients[client_address] = username  # Store the client address and username
                welcome_message = f"WELCOME: Welcome, {username}! You are now connected."
                print(f"[DEBUG] Sending welcome message: {welcome_message}")  # Debugging
                self.send_encrypted_message(welcome_message, client_address)
            else:
                self.send_encrypted_message(msg, client_address)
        except ValueError:
            error_message = "Invalid login command. Use: /login <username> <password>"
            self.send_encrypted_message(error_message, client_address)


    def broadcast_message(self, message, sender_address):
            sender_username = self.clients[sender_address]
            formatted_message = f"{sender_username}: {message}"
            print(f"[DEBUG] Broadcasting message: {formatted_message}")  # Debugging

            for client in self.clients:
                if client != sender_address:  # Broadcast to all other clients
                    self.send_encrypted_message(formatted_message, client)

    def send_encrypted_message(self, message, client_address):
        encrypted_message = self.encryption_helper.encrypt(message)
        self.server_socket.sendto(encrypted_message.encode('utf-8'), client_address)
