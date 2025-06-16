import socket
import threading
import time
import sys
import re
import netifaces
import asyncio
from os import system, name
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, Window, Dimension, VSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import ANSI

# ASCII art for "X" in Terminal HUD Style
ASCII_X = """
\033[1;36m
        //H3llo.. verr /p/

            ██╗    ██╗
            ╚██╗  ██╔╝
             ╚██╗██╔╝ 
              ╚███╔╝  
              ██╔██╗  
             ██╔╝╚██╗ 
            ██╔╝  ╚██╗
            ╚═╝    ╚═╝

//Welc0me To VulneraX Relay Chat [:p]
\033[0m
"""

def clear_screen():
    system('cls' if name == 'nt' else 'clear')

def is_valid_ip(ip):
    pattern = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return ip == "0.0.0.0" or bool(pattern.match(ip))

def is_valid_port(port_str):
    try:
        port = int(port_str)
        return 0 <= port <= 65535
    except ValueError:
        return False

def get_local_ip():
    try:
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if not ip.startswith('127.'):
                        return ip
    except:
        pass
    return '127.0.0.1'

def receive_until_newline(client):
    buffer = ""
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if not data:
                return None
            buffer += data
            if '\n' in buffer:
                message, _, buffer = buffer.partition('\n')
                return message.strip()
        except socket.error:
            return None
        except UnicodeDecodeError:
            return None

# Server
def start_server():
    ip = input("\033[1;34mEnter server IP (e.g., 0.0.0.0 for all interfaces): \033[0m").strip()
    if not is_valid_ip(ip):
        print("\033[1;31mInvalid IP address. Please enter a valid IP (e.g., 192.168.1.x or 0.0.0.0).\033[0m")
        return

    port_str = input("\033[1;34mEnter server port (e.g., 55555): \033[0m").strip()
    if not is_valid_port(port_str):
        print("\033[1;31mInvalid port. Please enter a number between 0 and 65535.\033[0m")
        return
    port = int(port_str)

    server_password = input("\033[1;34mEnter server password: \033[0m").strip()
    if not server_password:
        print("\033[1;31mPassword cannot be empty.\033[0m")
        return

    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
        server.listen()
        broadcast_ip = ip if ip != "0.0.0.0" else get_local_ip()
        print(f"\033[1;32m[SERVER] Started on {ip}:{port}\033[0m")
        print(f"\033[1;33m[SERVER] IP for clients to connect: {broadcast_ip}:{port}\033[0m")
        print(f"\033[1;33m[SERVER] Password required: {server_password}\033[0m")
    except socket.error as e:
        print(f"\033[1;31mFailed to start server: {e}. Ensure IP/port are valid and not in use.\033[0m")
        if server:
            server.close()
        return
    except Exception as e:
        print(f"\033[1;31mUnexpected error starting server: {e}\033[0m")
        if server:
            server.close()
        return

    def broadcast_server_info():
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.bind(('', 0))
        message = f"VULNERAX_SERVER:{broadcast_ip}:{port}".encode('utf-8')
        try:
            while True:
                udp_socket.sendto(message, ('255.255.255.255', 37020))
                time.sleep(2)
        except:
            pass
        finally:
            udp_socket.close()

    broadcast_thread = threading.Thread(target=broadcast_server_info, daemon=True)
    broadcast_thread.start()

    clients = {}
    
    def broadcast(message, sender=None):
        timestamp = time.strftime("%H:%M:%S")
        message = f"[{timestamp}] {message}"
        for client, _ in list(clients.items()):
            if client != sender:
                try:
                    client.send(f"{message}\n".encode('utf-8'))
                except socket.error as e:
                    print(f"\033[1;31m[SERVER] Failed to broadcast to {clients[client]}: {e}\033[0m")
                    client.close()
                    clients.pop(client, None)
    
    def send_private(sender, target_username, message):
        timestamp = time.strftime("%H:%M:%S")
        for client, username in list(clients.items()):
            if username == target_username:
                try:
                    client.send(f"[{timestamp}] \033[1;35m[PRIVATE from {clients[sender]}] {message}\033[0m\n".encode('utf-8'))
                    sender.send(f"[{timestamp}] \033[1;35m[PRIVATE to {target_username}] {message}\033[0m\n".encode('utf-8'))
                    print(f"\033[1;34m[SERVER] Private message from {clients[sender]} to {target_username}: {message}\033[0m")
                    return True
                except socket.error as e:
                    print(f"\033[1;31m[SERVER] Failed to send private message to {target_username}: {e}\033[0m")
                    client.close()
                    clients.pop(client, None)
        try:
            sender.send(f"[{timestamp}] \033[1;31mUser {target_username} not found\033[0m\n".encode('utf-8'))
            print(f"\033[1;34m[SERVER] User {target_username} not found for {clients[sender]}\033[0m")
        except socket.error as e:
            print(f"\033[1;31m[SERVER] Failed to notify {clients[sender]}: {e}\033[0m")
            sender.close()
            clients.pop(sender, None)
        return False
    
    def update_client_list():
        client_list = ", ".join(clients.values())
        broadcast(f"\033[1;33mConnected users: {client_list}\033[0m")
    
    def handle_client(client, addr):
        try:
            password = receive_until_newline(client)
            print(f"\033[1;34m[SERVER] Received password from {addr}: {password}\033[0m")
            if not password:
                print(f"\033[1;31m[SERVER] Empty password from {addr}\033[0m")
                client.close()
                return
            if password != server_password:
                try:
                    client.send("AUTH_FAILED\n".encode('utf-8'))
                    print(f"\033[1;31m[SERVER] Client {addr} rejected: Incorrect password\033[0m")
                except socket.error as e:
                    print(f"\033[1;31m[SERVER] Failed to send AUTH_FAILED to {addr}: {e}\033[0m")
                finally:
                    client.close()
                return
            try:
                client.send("AUTH_SUCCESS\n".encode('utf-8'))
                print(f"\033[1;34m[SERVER] Client {addr} authenticated successfully\033[0m")
            except socket.error as e:
                print(f"\033[1;31m[SERVER] Failed to send AUTH_SUCCESS to {addr}: {e}\033[0m")
                client.close()
                return
            
            username = receive_until_newline(client)
            if not username:
                print(f"\033[1;31m[SERVER] Client {addr} failed to send username\033[0m")
                client.close()
                return
            print(f"\033[1;34m[SERVER] Client {addr} registered as {username}\033[0m")
            clients[client] = username
            broadcast(f"\033[1;33m{username} joined the chat!\033[0m")
            update_client_list()
            
            while True:
                try:
                    header = receive_until_newline(client)
                    if not header:
                        print(f"\033[1;31m[SERVER] Client {username} disconnected (no data)\033[0m")
                        break
                    print(f"\033[1;34m[SERVER] Received from {username}: {header}\033[0m")
                    if header.startswith("PRIVATE:"):
                        try:
                            _, target_username, message = header.split(":", 2)
                            send_private(client, target_username, message.strip())
                        except ValueError as e:
                            print(f"\033[1;31m[SERVER] Invalid private message format from {username}: {e}\033[0m")
                            continue
                    else:
                        broadcast(f"{username}: {header}", client)
                except socket.error as e:
                    print(f"\033[1;31m[SERVER] Client {username} disconnected: {e}\033[0m")
                    break
                except UnicodeDecodeError as e:
                    print(f"\033[1;31m[SERVER] Decoding error from {username}: {e}\033[0m")
                    continue
        except socket.error as e:
            print(f"\033[1;31m[SERVER] Error initializing client {addr}: {e}\033[0m")
        except Exception as e:
            print(f"\033[1;31m[SERVER] Unexpected error initializing client {addr}: {e}\033[0m")
        
        try:
            client.close()
        except:
            pass
        if client in clients:
            username = clients[client]
            clients.pop(client, None)
            broadcast(f"\033[1;31m{username} left the chat!\033[0m")
            update_client_list()
    
    try:
        while True:
            client, addr = server.accept()
            print(f"\033[1;32m[SERVER] New connection from {addr}\033[0m")
            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.start()
    except KeyboardInterrupt:
        print("\033[1;31m[SERVER] Shutting down...\033[0m")
        for client in list(clients.keys()):
            try:
                client.close()
            except:
                pass
        server.close()
    except Exception as e:
        print(f"\033[1;31mServer error: {e}\033[0m")
        for client in list(clients.keys()):
            try:
                client.close()
            except:
                pass
        server.close()

def start_client():
    print("\033[1;34mSearching for server...\033[0m")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(('', 37020))
        udp_socket.settimeout(10)
        data, _ = udp_socket.recvfrom(1024)
        message = data.decode('utf-8')
        if message.startswith("VULNERAX_SERVER:"):
            _, ip, port = message.split(":")
            port = int(port)
            if ip.startswith('127'):
                raise ValueError("Loopback IP detected")
            print(f"\033[1;32mFound server at {ip}:{port}\033[0m")
    except socket.timeout:
        print("\033[1;31mNo server found. Please enter server details.\033[0m")
        udp_socket.close()
        ip = input("\033[1;34mEnter server IP (e.g., 192.168.1.x): \033[0m").strip()
        if not is_valid_ip(ip):
            print("\033[1;31mInvalid IP address. Please enter a valid IP (e.g., 192.168.1.x).\033[0m")
            return
        port_str = input("\033[1;34mEnter server port (e.g., 55555): \033[0m").strip()
        if not is_valid_port(port_str):
            print("\033[1;31mInvalid port. Please enter a number between 0 and 65535.\033[0m")
            return
        port = int(port_str)
    except ValueError as e:
        print(f"\033[1;31mInvalid server address: {e}. Please enter server details manually.\033[0m")
        udp_socket.close()
        ip = input("\033[1;34mEnter server IP (e.g., 192.168.1.x): \033[0m").strip()
        if not is_valid_ip(ip):
            print("\033[1;31mInvalid IP address. Please enter a valid IP (e.g., 192.168.1.x).\033[0m")
            return
        port_str = input("\033[1;34mEnter server port (e.g., 55555): \033[0m").strip()
        if not is_valid_port(port_str):
            print("\033[1;31mInvalid port. Please enter a number between 0 and 65535.\033[0m")
            return
        port = int(port_str)
    except Exception as e:
        print(f"\033[1;31mError discovering server: {e}\033[0m")
        udp_socket.close()
        return
    finally:
        udp_socket.close()

    client = None
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(10)
        client.connect((ip, port))
        client.settimeout(None)
        print(f"\033[1;34m[CLIENT] Connected to server at {ip}:{port}\033[0m")
    except socket.error as e:
        print(f"\033[1;31mFailed to connect to server: {e}. Ensure server is running and IP/port are correct.\033[0m")
        if client:
            client.close()
        return
    except Exception as e:
        print(f"\033[1;31mUnexpected error connecting to server: {e}\033[0m")
        if client:
            client.close()
        return

    attempts = 0
    max_attempts = 3
    while attempts < max_attempts:
        password = input(f"\033[1;34mEnter server password (attempt {attempts + 1}/{max_attempts}): \033[0m").strip()
        if not password:
            print("\033[1;31mPassword cannot be empty.\033[0m")
            attempts += 1
            continue
        try:
            client.send(f"{password}\n".encode('utf-8'))
            auth_response = receive_until_newline(client)
            print(f"\033[1;34m[CLIENT] Received auth response: {auth_response}\033[0m")
            if auth_response is None:
                print("\033[1;31mServer disconnected during authentication.\033[0m")
                client.close()
                return
            if auth_response == "AUTH_FAILED":
                attempts += 1
                if attempts < max_attempts:
                    print(f"\033[1;31mIncorrect password. {max_attempts - attempts} attempt(s) remaining.\033[0m")
                continue
            if auth_response == "AUTH_SUCCESS":
                break
        except socket.error as e:
            print(f"\033[1;31mSocket error during authentication: {e}\033[0m")
            client.close()
            return
        except UnicodeDecodeError as e:
            print(f"\033[1;31mDecoding error during authentication: {e}\033[0m")
            client.close()
            return
    else:
        print("\033[1;31mAuthentication failed: Incorrect password.\033[0m")
        client.close()
        return

    username = input("\033[1;32mEnter your username: \033[0m").strip()
    if not username:
        print("\033[1;31mUsername cannot be empty.\033[0m")
        client.close()
        return
    try:
        client.send(f"{username}\n".encode('utf-8'))
        print(f"\033[1;34m[CLIENT] Sent username: {username}\033[0m")
    except socket.error as e:
        print(f"\033[1;31mFailed to send username: {e}\033[0m")
        client.close()
        return
    except Exception as e:
        print(f"\033[1;31mUnexpected error sending username: {e}\033[0m")
        client.close()
        return

    clear_screen()
    print(ASCII_X)
    print("\033[1;36m══════ VULNERAX RELAY CHAT ══════\033[0m")
    print(f"\033[1;32mConnected to {ip}:{port}\033[0m")
    print("\033[1;34mAvailable Commands:\033[0m")
    print("  \033[1;37m•\033[0m Send message: <message>")
    print("  \033[1;37m•\033[0m Broadcast: broadcast <message>")
    print("  \033[1;37m•\033[0m Private message: private <username> <message>")
    print("  \033[1;37m•\033[0m Quit: exit")
    print("\033[1;36m════════════════════════════════\033[0m")

    output_text = []

    output_window = Window(
        FormattedTextControl(lambda: ANSI(''.join(output_text))),
        wrap_lines=True,
        height=Dimension(max=sys.maxsize),
        width=Dimension(max=80)
    )
    input_buffer = Buffer()
    prompt_window = Window(
        FormattedTextControl(ANSI(f"\033[1;32m{username}@VulneraX:~$ \033[0m")),
        width=Dimension.exact(len(f"{username}@VulneraX:~$ ") + 2),
        height=1
    )
    input_control_window = Window(
        BufferControl(buffer=input_buffer),
        height=1,
        width=Dimension(max=80)
    )
    input_container = VSplit([
        prompt_window,
        input_control_window
    ])
    separator_window = Window(
        height=1,
        char='═',
        style='fg:#00aaaa',
        width=Dimension.exact(32)
    )
    root_container = HSplit([
        output_window,
        separator_window,
        input_container
    ])
    layout = Layout(root_container)

    style = Style.from_dict({
        '': '#ffffff',
    })

    bindings = KeyBindings()

    @bindings.add('enter')
    def _(event):
        message = input_buffer.text.strip()
        if message:
            if message.lower() == 'exit':
                app.exit()
                try:
                    client.close()
                except:
                    pass
                sys.exit(0)
            try:
                if message.startswith("private "):
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        output_text.append("\n\033[1;31mUsage: private <username> <message>\033[0m\n\033[1;36m════════════════════════════════\033[0m")
                        input_buffer.text = ""
                        app.invalidate()
                        return
                    _, target_username, private_message = parts
                    client.send(f"PRIVATE:{target_username}:{private_message}\n".encode('utf-8'))
                else:
                    if message.startswith("broadcast "):
                        message = message.split(" ", 1)[1]
                    client.send(f"{message}\n".encode('utf-8'))
                input_buffer.text = ""
                app.invalidate()
            except socket.error as e:
                output_text.append(f"\n\033[1;31mError sending message: {e}\033[0m\n\033[1;36m════════════════════════════════\033[0m")
                app.exit()
            except Exception as e:
                output_text.append(f"\n\033[1;31mUnexpected error: {e}\033[0m\n\033[1;36m════════════════════════════════\033[0m")
                app.exit()

    @bindings.add('c-c')
    def _(event):
        app.exit()
        try:
            client.close()
        except:
            pass
        output_text.append("\n\033[1;31mExiting VulneraX Relay Chat...\033[0m\n\033[1;36m════════════════════════════════\033[0m")
        sys.exit(0)

    try:
        app = Application(
            layout=layout,
            key_bindings=bindings,
            style=style,
            full_screen=True
        )
    except Exception as e:
        print(f"\033[1;31mFailed to initialize application: {e}\033[0m")
        client.close()
        return

    app.layout.focus(input_control_window)

    async def receive():
        loop = asyncio.get_event_loop()
        buffer = ""
        while True:
            try:
                data = client.recv(1024).decode('utf-8')
                if not data:
                    await loop.run_in_executor(None, lambda: output_text.append("\n\033[1;31mDisconnected from server\033[0m\n\033[1;36m════════════════════════════════\033[0m"))
                    await loop.run_in_executor(None, app.invalidate)
                    break
                buffer += data
                while '\n' in buffer:
                    message, _, buffer = buffer.partition('\n')
                    message = message.strip()
                    if message:
                        # Debug: Log received data
                        # print(f"\033[1;34m[CLIENT] Received: {repr(message)}\033[0m")
                        await loop.run_in_executor(None, lambda: output_text.append(f"\n\033[0;37m{message}\033[0m\n\033[1;36m════════════════════════════════\033[0m"))
                        await loop.run_in_executor(None, app.invalidate)
            except socket.error as e:
                await loop.run_in_executor(None, lambda: output_text.append(f"\n\033[1;31mDisconnected from server: {e}\033[0m\n\033[1;36m════════════════════════════════\033[0m"))
                await loop.run_in_executor(None, app.invalidate)
                break
            except UnicodeDecodeError as e:
                await loop.run_in_executor(None, lambda: output_text.append(f"\n\033[1;31mDecoding error: {e}\033[0m\n\033[1;36m════════════════════════════════\033[0m"))
                await loop.run_in_executor(None, app.invalidate)
        try:
            client.close()
        except:
            pass
        await loop.run_in_executor(None, app.exit)

    def start_receive_thread():
        try:
            asyncio.run(receive())
        except Exception as e:
            print(f"\033[1;31mReceive thread error: {e}\033[0m")

    receive_thread = threading.Thread(target=start_receive_thread, daemon=True)
    receive_thread.start()

    try:
        app.run()
    except Exception as e:
        print(f"\033[1;31mApplication error: {e}\033[0m")
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    try:
        clear_screen()
        print(ASCII_X)
        print("\033[1;36m══════ VULNERAX RELAY CHAT ══════\033[0m")
        print("\033[1;33mSecure Multi-Client Communication Platform\033[0m")
        print("\033[1;37mFeatures:\033[0m")
        print("  \033[1;37m•\033[0m Group chat with broadcast messages")
        print("  \033[1;37m•\033[0m Private messaging between users")
        print("  \033[1;37m•\033[0m Password-protected server access")
        print("  \033[1;37m•\033[0m Server or client mode")
        print("\033[1;36m════════════════════════════════\033[0m")
        choice = input("\033[1;34mRun as (1) Server or (2) Client? \033[0m").strip()
        if choice == '1':
            start_server()
        elif choice == '2':
            start_client()
        else:
            print("\033[1;31mInvalid choice. Please select 1 or 2.\033[0m")
    except KeyboardInterrupt:
        print("\n\033[1;31mApplication terminated.\033[0m")
    except Exception as e:
        print(f"\n\033[1;31mUnexpected error: {e}\033[0m")
