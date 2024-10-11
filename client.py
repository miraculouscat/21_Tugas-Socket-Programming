import socket
import threading

def listen_for_messages(client_socket):
    while True:
        try:
            response, _ = client_socket.recvfrom(1024)
            print("\n" + response.decode('utf-8'))  # Print incoming messages
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    # Ask user for server IP and port
    server_ip = input("Enter server IP address: ")  # Use the actual public IP of the server
    server_port = int(input("Enter server port: "))

    # Server address
    server_address = (server_ip, server_port)

    # Create UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Command input
    command = input("Enter command (REGISTER / LOGIN): ").upper()
    username = input("Enter username: ")
    password = input("Enter password: ")

    if command == "REGISTER":
        message = f"REGISTER {username} {password}"
    elif command == "LOGIN":
        message = f"LOGIN {username} {password}"
    else:
        print("Invalid command.")
        return

    # Send message to server
    print(f"Sending {command.lower()} request: {message}")
    client_socket.sendto(message.encode('utf-8'), server_address)

    # Receive response from server
    try:
        response, _ = client_socket.recvfrom(1024)
        print("Server response:", response.decode('utf-8'))
    except Exception as e:
        print(f"Error receiving server response: {e}")
        return

    # Listen for incoming messages in a separate thread
    threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True).start()

    # Allow the user to send messages
    while True:
        user_message = input("Enter message to send (or type 'exit' to quit): ")
        if user_message.lower() == 'exit':
            break
        if username:  # Ensure the user is logged in
            full_message = f"MSG {username} {user_message}"
            client_socket.sendto(full_message.encode('utf-8'), server_address)

    client_socket.close()

if __name__ == "__main__":
    main()
