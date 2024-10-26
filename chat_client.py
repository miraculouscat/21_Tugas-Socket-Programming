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
        self.username = None
        self.running = True

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
                self.username = username
                valid_command = True
            elif command.startswith("/login"):
                username = input("Enter username: ")
                password = input("Enter password: ")
                full_command = f"/login {username} {password}"
                self.send_message(full_command)
                self.username = username
                valid_command = True
            else:
                print("Invalid command. Please use /register or /login.")
            
            self.listen_for_auth_response()

    def listen_for_auth_response(self):
        try:
            message, _ = self.client_socket.recvfrom(1024)
            decrypted_message = self.encryption_helper.decrypt(message.decode('utf-8'))
            
            print("\n")
            print(f"[AUTH RESPONSE] {decrypted_message}")

            if "welcome" in decrypted_message.lower() or "registration successful" in decrypted_message.lower():
                print("Login or Registration successful.")
                self.start_chat()  # Start chat after successful authentication
            else:
                self.handle_auth_failure()  # Handle failed registration or login
        except Exception as e:
            print(f"Error receiving authentication response: {e}")

    def handle_auth_failure(self):
        print("Authentication failed.")
        while self.running:
            choice = input("Do you want to (r)egister again, (l)ogin, or (e)xit?: ").lower()
            if choice == 'r':
                self.authenticate()  # Retry registration or login
                break
            elif choice == 'l':
                self.authenticate()  # Switch to login
                break
            elif choice == 'e':
                print("Exiting.")
                self.close()
                break
            else:
                print("Invalid choice. Please enter 'r', 'l', or 'e'.")

    def start_chat(self):
        # Start a thread to listen for incoming messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

        # Enter the chat loop to send messages
        self.chat_loop()

    def chat_loop(self):
        self.load_chat_history()
        # print("You can start chatting now! Type your message:")

        while self.running:
            try:
                message = input("[CHAT INPUT] Type a message: ")
                if message.lower() == "exit":
                    print("Exiting chat.")
                    self.running = False  # Signal to stop the thread
                    break
                self.send_message(message)
                self.save_to_history(f"{self.username}: {message}")  # Save sent message to chat history
            except Exception as e:
                print(f"[ERROR] Issue with input or message sending: {e}")

    def send_message(self, message):
        try:
            encrypted_message = self.encryption_helper.encrypt(message)
            self.client_socket.sendto(encrypted_message.encode('utf-8'), self.server_address)
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")

    def receive_messages(self):
        while self.running:
            try:
                message, _ = self.client_socket.recvfrom(1024)
                if message:
                    encrypted_message = message.decode('utf-8')
                    decrypted_message = self.encryption_helper.decrypt(encrypted_message)
                    
                    # Print the received message without interfering with the chat input
                    print(f"\n[NEW MESSAGE] {decrypted_message}")

                    # Reprint the chat input prompt after the message is received
                    print("[CHAT INPUT] Type a message: ", end="", flush=True)
            except Exception as e:
                if self.running:  # Only print errors if we're still running
                    print(f"Error receiving message: {e}")
                break  # Exit loop if an error occurs and we're shutting down

    def save_to_history(self, message):
        try:
            with open('chat_history.txt', 'a') as file:
                file.write(message + '\n')
        except Exception as e:
            print(f"[ERROR] Failed to save message to chat history: {e}")
            
    def load_chat_history(self):
        try:
            with open('chat_history.txt', 'r') as file:
                lines = file.readlines()
                print("\n")
                for line in lines:
                    print(f"[CHAT HISTORY] {line.strip()}")  # Print past messages
                print("\n")
        except FileNotFoundError:
            print("[INFO] No chat history found.")
            
    def close(self):
        self.running = False  # Signal all threads to stop
        self.client_socket.close()  # Close the socket
