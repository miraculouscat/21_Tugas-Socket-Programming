from chat_server import ChatServer

def main():
    hostname = "0.0.0.0"  # Server IP
    port = 12345  # Server port

    server = ChatServer(ip=hostname, port=port)
    server.start()

if __name__ == "__main__":
    main()
