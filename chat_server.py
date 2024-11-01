import socket
import threading
from auth import AuthManager
from encryption_helper import EncryptionHelper

class ChatServer:
    def __init__(self, ip='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((ip, port))
        self.clients = {}  
        self.chatrooms = {}  
        self.auth_manager = AuthManager()
        self.encryption_helper = EncryptionHelper(shift=3)
        print(f"[SERVER] Listening on {ip}:{port}")

        
    def start(self):
        while True:
            try:
                message, client_address = self.server_socket.recvfrom(1024)
                threading.Thread(target=self.handle_client, args=(message, client_address)).start()
            except ConnectionResetError:
                print(f"[ERROR] Connection reset by {client_address}")
            except Exception as e:
                print(f"[ERROR] An error occurred: {e}")


    def handle_client(self, message, client_address):
            try:
                # Log the raw (encrypted) message received from the client
                raw_message = message.decode('utf-8')

                # Attempt to decrypt the message for command processing
                decrypted_message = self.encryption_helper.decrypt(raw_message)

                # Check if the message is a command
                if decrypted_message.startswith("/register"):
                    print(f"[RECEIVED] {decrypted_message} from {client_address}")
                    self.register_client(decrypted_message, client_address)
                elif decrypted_message.startswith("/login"):
                    print(f"[RECEIVED] {decrypted_message} from {client_address}")
                    self.login_client(decrypted_message, client_address)
                elif decrypted_message.startswith("/join"):
                    print(f"[RECEIVED] {decrypted_message} from {client_address}")
                    self.join_chatroom(decrypted_message, client_address)
                else:
                    # If the message is not a command, it is treated as a chat message
                    if client_address in self.clients:
                        print(f"[CHAT MESSAGE] {raw_message} from {client_address}")  # Log chat messages
                        self.broadcast_message(decrypted_message, client_address)
                    else:
                        error_message = "You need to login or register first."
                        self.send_encrypted_message(error_message, client_address)
            except Exception as e:
                print(f"[ERROR] Failed to handle client message: {e}")




    def join_chatroom(self, command, client_address):
        try:
            _, chatroom_name = command.split()
            if client_address not in self.clients:
                self.send_encrypted_message("You must login to join a chatroom.", client_address)
                return

      
            if chatroom_name not in self.chatrooms:
                self.chatrooms[chatroom_name] = [] 
            
            if client_address not in self.chatrooms[chatroom_name]:
                self.chatrooms[chatroom_name].append(client_address)
                self.send_encrypted_message(f"You have successfully joined the chatroom: {chatroom_name}", client_address)
            else:
                self.send_encrypted_message(f"You are already in the chatroom: {chatroom_name}", client_address)
        except Exception as e:
            print(f"[ERROR] Failed to join chatroom: {e}")
            self.send_encrypted_message("Failed to join chatroom. Please try again.", client_address)



    def register_client(self, command, client_address):
        try:
            _, username, password = command.split()
            if username in self.clients.values():  
                error_message = "Username already taken. Please try another."
                self.send_encrypted_message(error_message, client_address)
                return

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
                self.clients[client_address] = username  
                welcome_message = f"WELCOME: Welcome, {username}! You are now connected."
                self.send_encrypted_message(welcome_message, client_address)
            else:
                self.send_encrypted_message(msg, client_address)
        except ValueError:
            error_message = "Invalid login command. Use: /login <username> <password>"
            self.send_encrypted_message(error_message, client_address)



    def broadcast_message(self, message, sender_address):
        sender_username = self.clients[sender_address]
        formatted_message = f"{sender_username}: {message}"
        
        for client in self.clients:
            if client != sender_address: 
                self.send_encrypted_message(formatted_message, client)


    def send_encrypted_message(self, message, client_address):
        encrypted_message = self.encryption_helper.encrypt(message)
        self.server_socket.sendto(encrypted_message.encode('utf-8'), client_address)
