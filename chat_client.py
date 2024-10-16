import socket
import threading
from encryption_helper import EncryptionHelper
from auth import AuthManager

class ChatClient:
    def __init__(self, server_ip, server_port, local_ip="0.0.0.0", local_port=0):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind((local_ip, local_port))
        self.server_address = (server_ip, server_port)
        self.encryption_helper = EncryptionHelper(shift=3)
        self.auth_manager = AuthManager()

    def start(self):
        print("[INIT] Connected to server", self.server_address)
        self.authenticate()

    def authenticate(self):
        valid_command = False
        while not valid_command:
            command = input("Enter command (/register or /login): ")
            if command.startswith("/register"):
                username = input("Enter username: ")
                password = input("Enter password: ")
                full_command = f"/register {username} {password}"
                self.send_message(full_command)
                valid_command = True
            elif command.startswith("/login"):
                username = input("Enter username: ")
                password = input("Enter password: ")
                full_command = f"/login {username} {password}"
                self.send_message(full_command)
                valid_command = True
            else:
                print("Invalid command. Please use /register or /login.")
            
            # Listen for response from the server (registration confirmation or error)
            self.listen_for_auth_response()

    def listen_for_auth_response(self):
        try:
            message, _ = self.client_socket.recvfrom(1024)
            decrypted_message = self.encryption_helper.decrypt(message.decode('utf-8'))
            print(f"[AUTH RESPONSE] {decrypted_message}")

            if "welcome" in decrypted_message.lower():
                self.start_chat()  # Start chat after successful login
            elif "registration successful" in decrypted_message.lower():
                print("Registration completed.")
                self.start_chat()  # Call start_chat after registration
            else:
                self.handle_auth_failure()  # Handle failed registration or login
        except Exception as e:
            print(f"Error receiving authentication response: {e}")

    def handle_auth_failure(self):
        print("Authentication failed.")
        while True:
            choice = input("Do you want to (r)egister again, (l)ogin, or (e)xit?: ").lower()
            if choice == 'r':
                self.authenticate()  # Retry registration or login
                break
            elif choice == 'l':
                self.authenticate()  # Switch to login
                break
            elif choice == 'e':
                print("Exiting.")
                self.client_socket.close()
                break
            else:
                print("Invalid choice. Please enter 'r', 'l', or 'e'.")

    def start_chat(self):
        print("[DEBUG] Starting chat")
        # Start a thread to listen for incoming messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

        # Enter the chat loop to send messages
        self.chat_loop()

    def chat_loop(self):
        print("[DEBUG] Entering chat loop")  # Debugging
        print("You can start chatting now! Type your message:")

        while True:
            try:
                message = input("[CHAT INPUT] Type a message: ")
                if message.lower() == "exit":
                    print("Exiting chat.")
                    self.client_socket.close()
                    break
                self.send_message(message)
                self.save_to_history(f"Me: {message}")  # Save sent message to chat history
            except Exception as e:
                print(f"[ERROR] Issue with input or message sending: {e}")


    def send_message(self, message):
        try:
            encrypted_message = self.encryption_helper.encrypt(message)
            self.client_socket.sendto(encrypted_message.encode('utf-8'), self.server_address)
            print(f"[DEBUG] Sent encrypted message: {encrypted_message}")
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")

    def receive_messages(self):
        while True:
            try:
                message, _ = self.client_socket.recvfrom(1024)
                if message:
                    encrypted_message = message.decode('utf-8')
                    decrypted_message = self.encryption_helper.decrypt(encrypted_message)
                    
                    # Print the received message without interfering with the chat input
                    print(f"\n[NEW MESSAGE] {decrypted_message}")
                    self.save_to_history(f"Other: {decrypted_message}")  # Save received message to chat history

                    # Reprint the chat input prompt after the message is received
                    print("[CHAT INPUT] Type a message: ", end="", flush=True)
            except Exception as e:
                print(f"Error receiving message: {e}")
                
    def save_to_history(self, message):
        try:
            with open('chat_history.txt', 'a') as file:
                file.write(message + '\n')
        except Exception as e:
            print(f"[ERROR] Failed to save message to chat history: {e}")
