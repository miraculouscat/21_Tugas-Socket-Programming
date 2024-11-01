import socket
import threading
from encryption_helper import EncryptionHelper

class TCPClient:
    def __init__(self, host='127.0.0.1', port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.encryption_helper = EncryptionHelper()
    
    def receive_messages(self):
        """Receive and decrypt messages from the server."""
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')
                if message:
                    if message.startswith("Welcome") or message.startswith("Enter"):
                        print(message)
                    else:
                        decrypted_message = self.encryption_helper.decrypt(message)
                        print(decrypted_message)
                else:
                    print("Disconnected from the server.")
                    break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_message(self):
        """Send encrypted messages to the server."""
        while True:
            message = input("")
            encrypted_message = self.encryption_helper.encrypt(message)
            self.client.send(encrypted_message.encode('ascii'))

    def authenticate_and_join(self):
        """Handle authentication, registration, and room joining."""
        try:
            action = input("Do you want to (R)egister or (L)ogin? ").strip().upper()
            self.client.send(action.encode('ascii'))

            if action == 'R':
                print(self.client.recv(1024).decode('ascii'))
                username = input("Enter a new username: ")
                self.client.send(username.encode('ascii'))

                print(self.client.recv(1024).decode('ascii'))
                password = input("Enter a new password: ")
                self.client.send(password.encode('ascii'))

                print(self.client.recv(1024).decode('ascii'))

            print(self.client.recv(1024).decode('ascii'))
            username = input("Enter your username: ")
            self.client.send(username.encode('ascii'))

            print(self.client.recv(1024).decode('ascii'))
            password = input("Enter your password: ")
            self.client.send(password.encode('ascii'))

            print(self.client.recv(1024).decode('ascii'))
            room = input("Enter room name: ")
            self.client.send(room.encode('ascii'))

            print(self.client.recv(1024).decode('ascii'))
            room_password = input("Enter room password: ")
            self.client.send(room_password.encode('ascii'))

            welcome_message = self.client.recv(1024).decode('ascii')
            print(welcome_message)
            if welcome_message.startswith("Welcome"):
                threading.Thread(target=self.receive_messages).start()
                self.send_message()
            else:
                print("Authentication or room access denied.")
                self.client.close()
        except Exception as e:
            print(f"Error during authentication: {e}")
            self.client.close()

if __name__ == "__main__":
    client = TCPClient()
    client.authenticate_and_join()
