# II2120_UDP_Socket-Programming

# UDP Socket Chat Programming

## Deskripsi
Tugas ini berisi tentang pembuatan sebuah aplikasi chat room sederhana yang memungkinkan pengguna-pengguna untuk bertukar pesan secara daring dan instan. Aplikasi dibuat menggunakan bahasa pemrograman Python >=3.10, dan memanfaatkan protokol transport UDP.

## Struktur Folder
/UDP Socket Programming
    ├── auth.py                 # Manajemen autentikasi
    ├── chat_client.py           # Kode client
    ├── chat_history.txt         # File untuk menyimpan riwayat chat
    ├── chat_server.py           # Kode server
    ├── client.py                # Implementasi klien
    ├── encryption_helper.py      # Pembantu enkripsi 
    └── README.md                # File ini



## Cara Menjalankan Program

### 1. Jalankan Program Server
- Buka terminal di perangkat yang dijadikan sebagai server.
- Arahkan ke direktori di file server 
- Jalankan dengan command python server.py

### 2. Jalankan Dua Program Client
- Buka terminal di perangkat yang dijadikan sebagai server.
- Arahkan ke direktori di file client
- Jalankan dengan command python client.py
- Di terminal lainnya, jalankan file yang sama

### Tahapan Pendaftaran dan Menutup Socket

1. **Register**
   - Pengguna diminta untuk memilih perintah `/register`.
   - Setelah memilih untuk mendaftar, pengguna diminta untuk memasukkan username dan password.
   - Jika username sudah terdaftar, server akan mengirimkan pesan "Username already taken." dan pengguna akan diminta untuk memilih kembali antara mendaftar atau login.
   - Jika pendaftaran berhasil, server mengirimkan pesan "Registration successful.".

2. **Login**
   - Pengguna diminta untuk memilih perintah `/login`.
   - Setelah memilih untuk login, pengguna diminta untuk memasukkan username dan password.
   - Jika username atau password salah, server akan mengirimkan pesan "Invalid username or password." dan pengguna diminta untuk memilih kembali antara mendaftar atau login.
   - Jika login berhasil, pengguna akan diberikan akses ke chatroom.

3. **Bergabung ke Chatroom**
   - Setelah berhasil login, pengguna diminta untuk memasukkan password.
   - Jika password yang dimasukkan sesuai, pengguna akan diterima dan dapat mulai bertukar pesan.

4. **Mengirim dan Menerima Pesan**
   - Pengguna dapat mulai mengirim pesan ke chatroom yang diikuti.
   - Pesan yang dikirim akan diterima oleh semua pengguna di chatroom yang sama.

5. **Menutup Socket**
   - Pengguna dapat keluar dari chatroom atau menutup aplikasi dengan mengetikkan perintah `exit`.
   - Setelah pengguna memilih untuk keluar, socket akan ditutup dan koneksi akan dihentikan dengan pesan "[INFO] Connection closed." ditampilkan.


# Kelompok 21 - Risol Ayam