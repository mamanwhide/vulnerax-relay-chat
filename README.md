# VulneraX Relay Chat

![VulneraX Logo](https://vulnerax.id/img/logo.png)

**VulneraX Relay Chat**, aplikasi obrolan intern berbasis terminal yang aman dan mendukung komunikasi multi-klien. Dibangun dengan Python, aplikasi ini menawarkan pengalaman obrolan grup dan pribadi.

```
██╗    ██╗
╚██╗  ██╔╝
 ╚██╗██╔╝ 
  ╚███╔╝  
  ██╔██╗  
 ██╔╝╚██╗ 
██╔╝  ╚██╗
╚═╝    ╚═╝
```

## Deskripsi Proyek

VulneraX Relay Chat adalah aplikasi obrolan berbasis TCP yang memungkinkan pengguna untuk berkomunikasi dalam grup atau secara pribadi melalui server yang dilindungi kata sandi. Aplikasi ini mendukung penemuan server otomatis melalui UDP broadcast dan menampilkan antarmuka terminal yang menarik dengan warna ANSI dan desain modern.

Proyek ini cocok untuk pengguna yang ingin menjelajahi komunikasi jaringan, pemrograman soket, atau sekadar menikmati obrolan berbasis terminal dengan estetika tinggi.

## Fitur Utama

- **Obrolan Grup**: Kirim pesan yang dapat dilihat oleh semua klien yang terhubung.
- **Pesan Pribadi**: Komunikasi satu lawan satu dengan pengguna lain secara aman.
- **Broadcast Pesan**: Kirim pesan ke semua klien secara serentak dengan perintah `broadcast`.
- **Autentikasi Kata Sandi**: Server dilindungi dengan kata sandi, dengan batas tiga kali percobaan.
- **Penemuan Server Otomatis**: Menggunakan UDP broadcast untuk mendeteksi server di jaringan lokal.
- **Antarmuka Estetis**: Desain Terminal HUD dengan ASCII art "X", warna ANSI, dan garis pemisah elegan.
- **Perintah Exit**: Keluar dari aplikasi klien dengan rapi menggunakan perintah `exit`.
- **Pembersihan Terminal**: Mendukung pembersihan layar untuk pengalaman pengguna yang lebih baik.

## Prasyarat

Untuk menjalankan VulneraX Relay Chat, pastikan Anda memiliki:

- **Python 3.6** atau versi lebih baru.
- **Modul Python**:
  - `socket` (bawaan Python)
  - `threading` (bawaan Python)
  - `time` (bawaan Python)
  - `sys` (bawaan Python)
  - `re` (bawaan Python)
  - `netifaces` (instal dengan `pip install netifaces`)
  - `os` (bawaan Python)
- **Sistem Operasi**: Windows, Linux, atau macOS dengan terminal yang mendukung kode warna ANSI.
- **Jaringan**: Koneksi jaringan lokal untuk komunikasi antar klien dan server. Pastikan port TCP dan UDP (default: 37020 untuk UDP) tidak diblokir oleh firewall.

## Instalasi

1. **Klon Repositori**:
   ```bash
   git clone https://github.com/mamanwhide/vulnerax-relay-chat.git
   cd vulnerax-relay-chat
   ```

2. **Instal Dependensi**:
   ```bash
   pip3 install netifaces
   pipx install netifaces
   sudo apt install python3-netifaces
   ```

3. **Jalankan Aplikasi**:
   ```bash
   python chat.py
   ```

## Cara Penggunaan

1. **Memulai Aplikasi**:
   - Jalankan `python chat.py`.
   - Anda akan melihat antarmuka awal dengan ASCII art "X":
     ```
     ██╗    ██╗
     ╚██╗  ██╔╝
      ╚██╗██╔╝ 
       ╚███╔╝  
       ██╔██╗  
      ██╔╝╚██╗ 
     ██╔╝  ╚██╗
     ╚═╝    ╚═╝

     ══════ VULNERAX RELAY CHAT ══════
     Secure Multi-Client Communication Platform
     ...
     Run as (1) Server or (2) Client?
     ```
   - Pilih `1` untuk menjalankan sebagai server atau `2` sebagai klien.

2. **Menjalankan Server**:
   - Masukkan IP server (misalnya, `0.0.0.0` untuk semua antarmuka).
   - Masukkan port (misalnya, `32342`).
   - Masukkan kata sandi server (misalnya, `Hello123!`).
   - Server akan berjalan dan menampilkan log koneksi klien.

3. **Menjalankan Klien**:
   - Klien akan mencoba mendeteksi server melalui UDP broadcast.
   - Jika gagal, masukkan IP dan port server secara manual.
   - Masukkan kata sandi server (maksimal 3 percobaan).
   - Masukkan nama pengguna (misalnya, `po`).
   - Antarmuka obrolan akan muncul:
     ```
     ══════ VULNERAX RELAY CHAT ══════
     Connected to 192.168.1.32:32342
     Available Commands:
       • Send message: <message>
       • Broadcast: broadcast <message>
       • Private message: private <username> <message>
       • Quit: exit
     ════════════════════════════════
     po@VulneraX:~$
     ```

4. **Perintah Obrolan**:
   - **Kirim pesan grup**: Ketik pesan langsung, misalnya, `hello lala`.
   - **Broadcast**: `broadcast important information`.
   - **Pesan pribadi**: `private Hasrul hello po`.
   - **Keluar**: `exit` untuk menutup klien.

## Struktur Kode

- **chat.py**:
  - File utama yang berisi logika server dan klien.
  - Menggunakan modul `socket` untuk komunikasi TCP dan UDP.
  - Mengimplementasikan threading untuk menangani multiple klien.
  - Menyediakan antarmuka terminal dengan warna ANSI dan ASCII art.

- **Fungsi Utama**:
  - `start_server()`: Mengelola server, autentikasi, dan komunikasi klien.
  - `start_client()`: Menangani koneksi klien, obrolan, dan UI terminal.
  - `receive_until_newline()`: Membaca data hingga newline untuk autentikasi.
  - `clear_screen()`: Membersihkan layar terminal.
  - `is_valid_ip()` dan `is_valid_port()`: Validasi input IP dan port.
  - `get_local_ip()`: Mendeteksi IP lokal untuk broadcast.

## Kontribusi

Kami menyambut kontribusi untuk meningkatkan VulneraX Relay Chat! Ikuti langkah berikut:

1. **Fork Repositori**:
   - Klik tombol "Fork" di GitHub.

2. **Buat Branch**:
   ```bash
   git checkout -b fitur-baru
   ```

3. **Lakukan Perubahan**:
   - Tambahkan fitur, perbaiki bug, atau tingkatkan dokumentasi.
   - Pastikan kode sesuai dengan gaya PEP 8.

4. **Commit dan Push**:
   ```bash
   git commit -m "Menambahkan fitur baru"
   git push origin fitur-baru
   ```

5. **Buat Pull Request**:
   - Jelaskan perubahan Anda secara rinci di pull request.

**Ide Kontribusi**:
- Menambahkan fitur pengiriman file.
- Meningkatkan UI dengan animasi terminal.
- Mendukung enkripsi pesan.
- Menambahkan log obrolan ke file.

## Lisensi

Proyek ini dilisensikan di bawah [Vulnerax](LICENSE). Anda bebas menggunakan, memodifikasi, dan mendistribusikan kode ini sesuai ketentuan lisensi.

## Kontak

Jika Anda memiliki pertanyaan atau saran, silakan hubungi:

- **Email**: [maman@vulnerax.com](mailto:maman@vulnerax.com)
- **GitHub Issues**: Buka isu baru di repositori ini.

Terima kasih telah menggunakan VulneraX Relay Chat! 
