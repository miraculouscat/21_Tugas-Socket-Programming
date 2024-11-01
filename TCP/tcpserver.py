import socket
import threading
from encryption_helper import EncryptionHelper

class TCPServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        print(f"Server started on {host}:{port}")

        self.clients = []
        self.users = {}  # Store user credentials in memory
        self.rooms = {
            "Room1": "123",  # Room names and passwords
            "Room2": "labtekV"
        }
        self.room_clients = {room: [] for room in self.rooms}
        self.encryption_helper = EncryptionHelper()

    def broadcast(self, message, room, max_retries=3):
        """Send a message to all clients in a specific room."""
        for client in self.room_clients[room]:
            retries = 0
            while retries < max_retries:
                try:
                    client.send(message)
                    break
                except Exception as e:
                    print(f"Failed to send message. Attempt {retries + 1} of {max_retries}: {e}")
                    retries += 1

    def handle_client(self, client, address):
        """Authenticate or register user, join room, and handle messages."""
        try:
            client.send("Do you want to (R)egister or (L)ogin? ".encode('ascii'))
            choice = client.recv(1024).decode('ascii').strip().upper()

            # Register new user
            if choice == 'R':
                client.send("Enter new username: ".encode('ascii'))
                username = client.recv(1024).decode('ascii')
                if username in self.users:
                    client.send("Username already taken.".encode('ascii'))
                    client.close()
                    return
                client.send("Enter new password: ".encode('ascii'))
                password = client.recv(1024).decode('ascii')
                self.users[username] = password
                client.send("Registration successful.\n".encode('ascii'))

            # Login existing user
            client.send("Enter username: ".encode('ascii'))
            username = client.recv(1024).decode('ascii')
            client.send("Enter password: ".encode('ascii'))
            password = client.recv(1024).decode('ascii')

            if self.users.get(username) != password:
                client.send("Invalid username or password.".encode('ascii'))
                client.close()
                return

            # Join a chatroom
            client.send("Enter room name: ".encode('ascii'))
            room = client.recv(1024).decode('ascii')
            client.send("Enter room password: ".encode('ascii'))
            room_password = client.recv(1024).decode('ascii')

            # Validate room access
            if room in self.rooms and self.rooms[room] == room_password:
                self.room_clients[room].append(client)
                client.send(f"Welcome to {room}!\n".encode('ascii'))
                print(f"{username} joined {room} from {address}.")
                self.listen_to_client(client, room, username)
            else:
                client.send("Invalid room or password.".encode('ascii'))
                client.close()
        except Exception as e:
            print(f"Error handling client {address}: {e}")
            client.close()

    def listen_to_client(self, client, room, username):
        """Receive and broadcast messages from a client."""
        while True:
            try:
                message = client.recv(1024)
                if not message:
                    break

                decrypted_text = self.encryption_helper.decrypt(message.decode('ascii'))
                print(f"{username} in {room}: {decrypted_text}")

                # Broadcast message to the room
                broadcast_message = f"{username}: {decrypted_text}".encode('ascii')
                self.broadcast(broadcast_message, room)
            except Exception as e:
                print(f"Error with {username}: {e}")
                break

        # Client has disconnected
        self.room_clients[room].remove(client)
        client.close()

    def start(self):
        """Accept incoming client connections."""
        while True:
            client, address = self.server.accept()
            print(f"Connected with {address}")
            threading.Thread(target=self.handle_client, args=(client, address)).start()

# Initialize and start the server
if __name__ == "__main__":
    server = TCPServer()
    server.start()
