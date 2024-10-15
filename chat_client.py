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

                # Check if authentication was successful based on the welcome message or registration success
                if "welcome" in decrypted_message.lower():
                    self.wait_for_welcome_message()  # Proceed to chat after successful login
                elif "registration successful" in decrypted_message.lower():
                    print("Registration completed.")
                    self.wait_for_welcome_message()  # Call wait_for_welcome_message after registration
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

    def wait_for_welcome_message(self):
        try:
            # Now wait for the welcome message from the server
            message, _ = self.client_socket.recvfrom(1024)
            decrypted_message = self.encryption_helper.decrypt(message.decode('utf-8'))

            # Use a more flexible check for the welcome message (case-insensitive)
            if "welcome" in decrypted_message.lower():
                print(f"[WELCOME] {decrypted_message}")

                # Debugging: Check if we're about to enter the chat loop
                print("[DEBUG] Proceeding to chat loop")
                
                # After receiving the welcome message, proceed to the chat loop
                self.chat_loop()
            else:
                print(f"[ERROR] Unexpected message: {decrypted_message}")
                # Optionally, prompt the user again for further action
                self.prompt_for_next_action()
        except Exception as e:
            print(f"Error receiving welcome message: {e}")


    def chat_loop(self):
        print("You can start chatting now! Type your message:")
        while True:
            message = input()
            if message.lower() == "exit":
                print("Exiting chat.")
                self.client_socket.close()
                break
            self.send_message(message)

    def send_message(self, message):
        encrypted_message = self.encryption_helper.encrypt(message)
        self.client_socket.sendto(encrypted_message.encode('utf-8'), self.server_address)
        print(f"Sent encrypted message: {encrypted_message}")

    def receive_messages(self):
        while True:
            try:
                message, _ = self.client_socket.recvfrom(1024)
                if message:
                    encrypted_message = message.decode('utf-8')
                    print(f"Received encrypted message: {encrypted_message}")
                    decrypted_message = self.encryption_helper.decrypt(encrypted_message)
                    print(f"\n[NEW MESSAGE] {decrypted_message}")
            except Exception as e:
                print(f"Error receiving message: {e}")
