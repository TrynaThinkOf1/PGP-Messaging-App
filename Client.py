import socket
from datetime import datetime, UTC
from time import sleep

import genkey
import cryption

connection = None
priv_key = None
connection_pub_key = None

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
    except KeyboardInterrupt:
        print("Closing messenger...")

if __name__ == "__main__":
    main()