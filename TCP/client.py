from tcpclient import ChatClient

def main():
    # Default values for server IP and port
    default_ip = "127.0.0.1"
    default_port = 12345
    
    # Get server IP from user input
    server_ip = input(f"Enter server IP (default {default_ip}): ") or default_ip
    
    # Get server port from user input with error handling
    while True:
        server_port_input = input(f"Enter server port (default {default_port}): ") or default_port
        try:
            server_port = int(server_port_input)
            break  # Exit the loop if conversion is successful
        except ValueError:
            print("Invalid port. Please enter a valid integer.")

    # Create and start the client
    client = ChatClient(server_ip=server_ip, server_port=server_port)
    try:
        client.start()
    except Exception as e:
        print(f"[ERROR] An error occurred while starting the client: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()