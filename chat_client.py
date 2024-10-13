import socket
import threading
from encryption_helper import EncryptionHelper
from auth import AuthManager

class ChatClient:
    def __init__(self, server_ip, server_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (server_ip, server_port)

        # Predefined encryption key only for client-to-client encryption
        self.encryption_helper = EncryptionHelper(key=65)

        self.auth_manager = AuthManager()

    def start(self):
        print("[INIT] Connected to server", self.server_address)
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.authenticate()

    def authenticate(self):
        while True:
            command = input("Enter command (/register or /login): ")
            if command.startswith("/register") or command.startswith("/login"):
                self.client_socket.sendto(command.encode('utf-8'), self.server_address)
                self.listen_for_auth_response()
                break
            else:
                print("Invalid command. Please use /register or /login.")

    def listen_for_auth_response(self):
        try:
            message, _ = self.client_socket.recvfrom(1024)
            # Authentication responses from the server are not encrypted
            print(f"[AUTH RESPONSE] {message.decode('utf-8')}")
            if "successful" in message.decode('utf-8'):
                self.wait_for_welcome_message()
        except Exception as e:
            print(f"Error receiving authentication response: {e}")

    def wait_for_welcome_message(self):
        try:
            message, _ = self.client_socket.recvfrom(1024)
            # Welcome message from the server is not encrypted
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
                decrypted_message = self.encryption_helper.xor_decrypt(message.decode('utf-8'))
                print(f"\n[NEW MESSAGE] {decrypted_message}")
            except Exception as e:
                print(f"Error receiving message: {e}")
