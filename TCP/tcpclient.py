import socket
import threading
from encryption_helper import EncryptionHelper

class ChatClient:
    def __init__(self, server_ip, server_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (server_ip, server_port)
        self.encryption_helper = EncryptionHelper(key='KEY')  # Use a key for encryption
        self.username = None
        self.running = True

    def start(self):
        try:
            self.client_socket.connect(self.server_address)
            print("[INIT] Connected to server", self.server_address)
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.authenticate()
        except Exception as e:
            print(f"[ERROR] Unable to connect to server: {e}")

    def authenticate(self):
        while True:
            command = input("Enter command (/register or /login): ")
            if command.startswith("/register"):
                username = input("Enter username: ")
                password = input("Enter password: ")
                full_command = f"/register {username} {password}"
                self.send_message(full_command)
                self.listen_for_auth_response()
            elif command.startswith("/login"):
                username = input("Enter username: ")
                password = input("Enter password: ")
                full_command = f"/login {username} {password}"
                self.send_message(full_command)
                self.listen_for_auth_response()
            elif command.lower() == "exit":
                self.close()
                break
            else:
                print("Invalid command. Please use /register or /login.")

    def send_message(self, message):
        encrypted_message = self.encryption_helper.encrypt(message)
        self.client_socket.send(encrypted_message.encode('utf-8'))

    def listen_for_auth_response(self):
        try:
            message = self.client_socket.recv(1024).decode('utf-8')
            decrypted_message = self.encryption_helper.decrypt(message)
            print(f"[AUTH RESPONSE] {decrypted_message}")

            if "successful" in decrypted_message.lower():
                print("Login or Registration successful.")
                self.prompt_for_chatroom_password()  # Ask for chatroom password after successful auth
            elif "already taken" in decrypted_message.lower():
                print(decrypted_message)
                # Prompt the user to retry immediately
                self.authenticate()
            else:
                print("Authentication failed.")
        except Exception as e:
            print(f"Error receiving authentication response: {e}")

    def prompt_for_chatroom_password(self):
        while True:
            password = input("Enter chatroom password to join (or type 'exit' to leave): ")
            if password.lower() == 'exit':
                self.close()
                break
            
            # Assuming a default chatroom name
            chatroom_name = "default_chatroom"
            join_command = f"/join {chatroom_name}"
            self.send_message(join_command)
            self.listen_for_join_response()
            break  # Exit the loop after sending the join command

    def listen_for_join_response(self):
        try:
            message = self.client_socket.recv(1024).decode('utf-8')
            decrypted_message = self.encryption_helper.decrypt(message)
            print(f"[JOIN RESPONSE] {decrypted_message}")

            if "successfully joined" in decrypted_message.lower():
                print("You have joined the chatroom successfully.")
                self.start_chat()
            else:
                print("Failed to join chatroom.")
        except Exception as e:
            print(f"Error receiving join response: {e}")

    def start_chat(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.chat_loop()

    def chat_loop(self):
        while self.running:
            try:
                message = input("[CHAT INPUT] Type a message: ")
                if message.lower() == "exit":
                    print("Exiting chat.")
                    self.running = False
                    break
                self.send_message(message)
            except Exception as e:
                print(f"[ERROR] Issue with input or message sending: {e}")

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    decrypted_message = self.encryption_helper.decrypt(message)
                    print(f"\n[NEW MESSAGE] {decrypted_message}")
                else:
                    print("[ERROR] Server closed the connection.")
                    break
            except Exception as e:
                if self.running:  # Only print errors if we're still running
                    print(f"[ERROR] An error occurred while receiving messages: {e}")
                break

    def close(self):
        self.running = False
        self.client_socket.close()
        print("[INFO] Connection closed.")

# Example usage:
if __name__ == "__main__":
    server_ip = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
    server_port = int(input("Enter server port (default 12345): ") or 12345)
    client = ChatClient(server_ip, server_port)
    client.start()
