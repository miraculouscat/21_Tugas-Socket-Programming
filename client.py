import socket
import threading

# Fungsi untuk menerima pesan dari server
def receive_messages(client_socket):
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            print(message.decode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
            break

def main():
    # Meminta pengguna memasukkan alamat server dan port
    server_ip = input("Masukkan alamat IP server: ")
    server_port = int(input("Masukkan port server: "))
    server_address = (server_ip, server_port)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Login atau registrasi
    while True:
        command = input("Masukkan perintah (REGISTER / LOGIN): ").strip().upper()

        if command == "REGISTER":
            username = input("Masukkan username: ")
            password = input("Masukkan password: ")
            client_socket.sendto(f"REGISTER {username} {password}".encode('utf-8'), server_address)
            response, _ = client_socket.recvfrom(1024)
            print(response.decode('utf-8'))

        elif command == "LOGIN":
            username = input("Masukkan username: ")
            password = input("Masukkan password: ")
            client_socket.sendto(f"LOGIN {username} {password}".encode('utf-8'), server_address)
            response, _ = client_socket.recvfrom(1024)
            print(response.decode('utf-8'))
            if response.decode('utf-8').startswith("LOGGED_IN"):
                break
        else:
            print("Perintah tidak valid. Silakan coba lagi.")

    # Mulai menerima pesan di thread terpisah
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    # Mengirim pesan ke server
    while True:
        message = input()
        if message.lower() == "exit":
            break
        client_socket.sendto(f"MSG {username} {message}".encode('utf-8'), server_address)

    client_socket.close()

if __name__ == "__main__":
    main()
