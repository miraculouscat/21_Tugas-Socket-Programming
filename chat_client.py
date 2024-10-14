import socket
import threading
from encryption_helper import EncryptionHelper
from auth import AuthManager

class ChatClient:
    def __init__(self, server_ip, server_port, local_ip="0.0.0.0", local_port=0):
        # Create the UDP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Bind the client socket to a local address (optional, 0 allows the OS to choose a port)
        self.client_socket.bind((local_ip, local_port))

        self.server_address = (server_ip, server_port)

        # Predefined encryption key only for client-to-client encryption
        self.encryption_helper = EncryptionHelper(key=65)

        self.auth_manager = AuthManager()

    def start(self):
        print("[INIT] Connected to server", self.server_address)
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.authenticate()

    def authenticate(self):
        valid_command = False
        while not valid_command:
            command = input("Enter command (/register or /login): ")
            if command.startswith("/register"):
                username = input("Enter username: ")
                password = input("Enter password: ")
                full_command = f"/register {username} {password}"
                self.client_socket.sendto(full_command.encode('utf-8'), self.server_address)
                self.listen_for_auth_response()
                valid_command = True  # Command sent successfully

            elif command.startswith("/login"):
                username = input("Enter username: ")
                password = input("Enter password: ")
                full_command = f"/login {username} {password}"
                self.client_socket.sendto(full_command.encode('utf-8'), self.server_address)
                self.listen_for_auth_response()
                valid_command = True  # Command sent successfully

            else:
                print("Invalid command. Please use /register or /login.")

    def listen_for_auth_response(self):
        try:
            message, _ = self.client_socket.recvfrom(1024)
            print(f"[AUTH RESPONSE] {message.decode('utf-8')}")
            if "successful" in message.decode('utf-8'):
                self.wait_for_welcome_message()
        except Exception as e:
            print(f"Error receiving authentication response: {e}")

    def wait_for_welcome_message(self):
        try:
            message, _ = self.client_socket.recvfrom(1024)
            print(f"[WELCOME] {message.decode('utf-8')}")
            self.chat_loop()
        except Exception as e:
            print(f"Error receiving welcome message: {e}")

    def chat_loop(self):
        print("You can start chatting now! Type your message:")
        while True:
            message = input()
            if message.lower() == "exit":
                print("Exiting chat.")
                break
            self.send_message(message)

    def send_message(self, message):
        # Encrypt the message for client-to-client communication
        encrypted_message = self.encryption_helper.xor_encrypt(message)
        self.client_socket.sendto(encrypted_message.encode('utf-8'), self.server_address)

    def receive_messages(self):
        while True:
            try:
                message, _ = self.client_socket.recvfrom(1024)
                if message:
                    # Decrypt the message if necessary
                    decrypted_message = self.encryption_helper.xor_decrypt(message.decode('utf-8'))
                    print(f"\n[NEW MESSAGE] {decrypted_message}")
            except Exception as e:
                print(f"Error receiving message: {e}")
