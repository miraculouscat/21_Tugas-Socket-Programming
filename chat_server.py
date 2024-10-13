import socket
import threading
from auth import AuthManager
from encryption_helper import EncryptionHelper

class ChatServer:
    def __init__(self, ip='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((ip, port))
        self.clients = {}
        self.auth_manager = AuthManager()
        self.encryption_helper = EncryptionHelper(key=65)  # Encryption only for client-to-client messages
        print(f"[SERVER] Listening on {ip}:{port}")
        self.chat_history_file = "chat_history.txt"  # File to store chat history

    def start(self):
        while True:
            message, client_address = self.server_socket.recvfrom(1024)
            threading.Thread(target=self.handle_client, args=(message, client_address)).start()

    def handle_client(self, message, client_address):
        decrypted_message = message.decode('utf-8')  # All incoming messages are not encrypted from clients
        print(f"[RECEIVED] {decrypted_message} from {client_address}")

        if decrypted_message.startswith("/register"):
            self.register_client(decrypted_message, client_address)
        elif decrypted_message.startswith("/login"):
            self.login_client(decrypted_message, client_address)
        else:
            self.broadcast_message(decrypted_message, client_address)
            self.save_chat_history(decrypted_message)

    def register_client(self, command, client_address):
        _, username, password = command.split()
        success, msg = self.auth_manager.register(username, password)
        response = msg  # Server messages are not encrypted
        self.server_socket.sendto(response.encode('utf-8'), client_address)

    def login_client(self, command, client_address):
        _, username, password = command.split()
        success, msg = self.auth_manager.login(username, password)
        if success:
            self.clients[client_address] = username
            welcome_message = f"Welcome, {username}! You are now connected."
            self.server_socket.sendto(welcome_message.encode('utf-8'), client_address)  # Not encrypted
        else:
            self.server_socket.sendto(msg.encode('utf-8'), client_address)  # Not encrypted

    def broadcast_message(self, message, sender_address):
        for client in self.clients:
            if client != sender_address:
                # Encrypt the message only for clients, not for server messages
                encrypted_message = self.encryption_helper.xor_encrypt(message)
                self.server_socket.sendto(encrypted_message.encode('utf-8'), client)

    def save_chat_history(self, message):
        with open(self.chat_history_file, "a") as file:
            file.write(f"{message}\n")
