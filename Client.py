import socket
import threading
from datetime import datetime, UTC
from time import sleep

from rich.console import Console
from rich.text import Text
from rich.panel import Panel


import genkey
import cryption

connection: socket.socket = None
priv_key = None
connection_pub_key = None

console = Console()

def receive_messages(ip):
    global connection, priv_key

    while True:
        try:
            encrypted_msg = b""
            while True:
                try:
                    chunk = connection.recv(1024)
                    if not chunk:
                        return
                    encrypted_msg += chunk
                    if encrypted_msg.endswith(b"<EOM>"):
                        break
                except socket.timeout:
                    continue

            if encrypted_msg:
                encrypted_msg = encrypted_msg[:-5]
                msg = cryption.decrypt_plaintext(priv_key, encrypted_msg)

                message = Text()
                message.append(msg, style="bold bright_green")

                message_panel = Panel(
                    message,
                    title=f"[ {ip} ]",
                    border_style="green",
                    padding=(1, 2)
                )

                console.print(message_panel)

        except (ConnectionResetError, ConnectionAbortedError):
            break

def send_messages():
    global connection, connection_pub_key

    print("\nEnter your message below. Press [Enter] to send.\n\n")
    while True:
        try:
            msg = input("").strip()
            if not msg:
                continue

            print("\033[A\033[K", end="", flush=True)

            encrypted_msg = cryption.encrypt_plaintext(connection_pub_key, msg)
            connection.sendall(encrypted_msg + b"<EOM>") # already bytes

            message = Text()
            message.append(msg, style="bold bright_blue")

            message_panel = Panel(
                message,
                title=f"[      YOU      ]",
                border_style="blue",
                padding=(1, 2)
            )

            console.print(message_panel)
        except (BrokenPipeError, ConnectionResetError):
            break

def message_loop(ip):
    global connection, connection_pub_key, priv_key

    connection.settimeout(None)

    receive_thread = threading.Thread(target=receive_messages, args=(ip,), daemon=True)
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, daemon=True)
    send_thread.start()

    try:
        while receive_thread.is_alive() and send_thread.is_alive():
            sleep(1)
    except KeyboardInterrupt:
        receive_thread.join()
        send_thread.join()
        connection.close()
        raise KeyboardInterrupt

def handshake():
    global connection, connection_pub_key, priv_key

    pub_key, priv_key = genkey.genkey("ELM")
    connection.sendall(f"START KEY EXCHANGE HANDSHAKE | {pub_key} | END KEY EXCHANGE HANDSHAKE".encode())

    connection.settimeout(5.0)
    handshake = ""
    while True:
        data = connection.recv(1024).decode()
        if not data:
            break
        handshake += data
        if handshake.endswith("END KEY EXCHANGE HANDSHAKE"):
            break


    if handshake.startswith("START KEY EXCHANGE HANDSHAKE |") and handshake.endswith(
            "| END KEY EXCHANGE HANDSHAKE"):
        connection_pub_key = handshake[30:-28]
        return connection_pub_key, priv_key
    else:
        print("Unsuccessful handshake, please restart the client.")
        exit(0)

    return

def listen(ip):
    global connection

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", 4500))
        sock.settimeout(0.125)
        sock.listen(1)

        conn, connected_ip = sock.accept()
        if connected_ip[0] == ip:
            connection = conn
            return True
        else:
            conn.close()
    except socket.timeout:
        pass
    finally:
        sock.close()
    return False

def connect(ip):
    global connection

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.125)
        try:
            sock.connect((ip, 4500))
            connection = sock
            return True
        except socket.error:
            pass
    except socket.error:
        pass
    finally:
        if not connection:
            sock.close()
    return False

def main():
    try:
        print("Welcome to ELM!\n")
        ip = input("What IP address would you like to message with? ")
        while len(ip.split(".")) != 4:
            print("Invalid IP address.")
            ip = input("What IP address would you like to message with? ")

        print(f"Attempting connection to {ip}:4500 @ {datetime.now(UTC)} UTC")

        while not connection:
            if listen(ip):
                break
            if connect(ip):
                break

        print(f"Successfully connected to {ip}:4500 @ {datetime.now(UTC)} UTC")
        handshake()
        message_loop(ip)
    except KeyboardInterrupt:
        print("\nClosing messenger...")
        exit(0)

if __name__ == "__main__":
    main()