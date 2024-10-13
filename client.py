from chat_client import ChatClient

def main():
    server_ip = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
    server_port = input("Enter server port (default 12345): ") or "12345"
    
    # Create an instance of ChatClient with predefined encryption key
    client = ChatClient(server_ip=server_ip, server_port=int(server_port))
    client.start()

if __name__ == "__main__":
    main()
