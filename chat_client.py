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
                self.listen_for_auth_response()
                
                login_choice = input("Do you want to login now? (y/n): ").strip().lower()
                if login_choice == 'y':
                    self.login()  
                else:
                    print("You can log in later by using the /login command.")

            elif command.startswith("/login"):
                self.login()  
                valid_command = True
            else:
                print("Invalid command. Please use /register or /login.")

    def login(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        full_command = f"/login {username} {password}"
        self.send_message(full_command)
        self.listen_for_auth_response()  

    def join_chatroom(self):
        while True:
            chatroom = input("Enter chatroom name to join (or type 'exit' to leave): ")
            if chatroom.lower() == "exit":
                self.close()
                return
            join_command = f"/join {chatroom}"
            self.send_message(join_command)
            self.listen_for_join_response()  
            break  

    def listen_for_auth_response(self):
        try:
            message, _ = self.client_socket.recvfrom(1024)
            decrypted_message = self.encryption_helper.decrypt(message.decode('utf-8'))
            print(f"[AUTH RESPONSE] {decrypted_message}")

            if "welcome" in decrypted_message.lower() or "registration successful" in decrypted_message.lower():
                print("Registration successful.")
                self.join_chatroom()
            else:
                self.handle_auth_failure()  
        except Exception as e:
            print(f"Error receiving authentication response: {e}")


    def handle_auth_failure(self):
        print("Authentication failed.")
        while self.running:
            choice = input("Do you want to (r)egister again, (l)ogin, or (e)xit?: ").lower()
            if choice == 'r':
                self.authenticate() 
                break
            elif choice == 'l':
                self.login() 
                break
            elif choice == 'e':
                print("Exiting.")
                self.close()
                break
            else:
                print("Invalid choice. Please enter 'r', 'l', or 'e'.")

    def join_chatroom(self):
        predefined_chatroom = "default_chatroom" 

        while True:
            
            password = input("Enter password to join or type 'exit' to leave (default: 333): ")
            
        
            if password.lower() == "exit":
                self.close()
                return
            
    
            if password == "333":
                join_command = f"/join {predefined_chatroom}"  
                self.send_message(join_command)
                self.listen_for_join_response() 
                break  
            else:
                print("Incorrect password. Please try again.")



    def listen_for_join_response(self):
        try:
            message, _ = self.client_socket.recvfrom(1024)
            decrypted_message = self.encryption_helper.decrypt(message.decode('utf-8'))
            print(f"[JOIN RESPONSE] {decrypted_message}")

            if "successfully joined" in decrypted_message.lower():
                    print("You have joined the chatroom successfully.")
                    self.start_chat() 
            else:
                    print("Failed to join chatroom.")
                   
                    self.handle_login_registration_choice()
        except Exception as e:
                print(f"Error receiving join response: {e}")

    def handle_login_registration_choice(self):
        while True:
            choice = input("You must login first to join a chatroom. Enter command (/register or /login): ").strip().lower()
            if choice.startswith("/register"):
                self.authenticate()  
                break
            elif choice.startswith("/login"):
                self.login()  
                break
            else:
                print("Invalid command. Please use /register or /login.")


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
                    decrypted_message = self.encryption_helper.decrypt(message.decode('utf-8'))
                    print(f"\n[NEW MESSAGE] {decrypted_message}")
                    print("[CHAT INPUT] Type a message: ", end="", flush=True)
            except Exception as e:
                if self.running:  
                    print(f"[ERROR] Error receiving message: {e}")
                break

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
                    print(f"[CHAT HISTORY] {line.strip()}")
                print("\n")
        except FileNotFoundError:
            print("[INFO] No chat history found.")
            
    def close(self):
        self.running = False  
        self.client_socket.close()  
        print("[INFO] Connection closed.")
