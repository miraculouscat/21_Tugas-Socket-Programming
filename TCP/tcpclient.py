import socket
import threading
from encryption_helper import EncryptionHelper
from auth import AuthManager

class ChatClient:
    def __init__(self, server_ip, server_port):
        # Create the TCP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_address = (server_ip, server_port)
        
        # Predefined encryption key for client-to-client encryption
        self.encryption_helper = EncryptionHelper(key='KEY')  # Use a string key for encryption

        self.auth_manager = AuthManager()

    def start(self):
        # Connect to the server
        try:
            self.client_socket.connect(self.server_address)
            print("[INIT] Connected to server", self.server_address)
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.authenticate()
        except Exception as e:
            print(f"[ERROR] Unable to connect to server: {e}")

    def authenticate(self):
        valid_command = False
        while not valid_command:
            command = input("Enter command (/register or /login): ")
            if command.startswith("/register"):
                username = input("Enter username: ")
                password = input("Enter password: ")
                full_command = f"/register {username} {password}"
                self.send_message(full_command)
                valid_command = True  # Command sent successfully

            elif command.startswith("/login"):
                username = input("Enter username: ")
                password = input("Enter password: ")
                full_command = f"/login {username} {password}"
                self.send_message(full_command)
                valid_command = True  # Command sent successfully

            else:
                print("Invalid command. Please use /register or /login.")

    def send_message(self, message):
        # Encrypt the message for client-to-server communication
        encrypted_message = self.encryption_helper.encrypt(message)
        self.client_socket.send(encrypted_message.encode('utf-8'))

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    decrypted_message = self.encryption_helper.decrypt(message)
                    print(f"\n[NEW MESSAGE] {decrypted_message}")
                else:
                    print("[ERROR] Server closed the connection.")
                    break
            except Exception as e:
                print(f"[ERROR] An error occurred while receiving messages: {e}")
                break

    def close(self):
        self.client_socket.close()
        print("[INFO] Connection closed.")