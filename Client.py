import socket
import threading
import json
import re
from requests import get
from datetime import datetime, UTC
from time import sleep
from os import system
from os.path import isfile

from rich.console import Console
from rich.text import Text
from rich.panel import Panel


import genkey
import cryption

connection: socket.socket = None
priv_key = None
connection_pub_key = None

console = Console()

with open("./emojis.json", "r") as file:
    emojis = json.loads(file.read())

with open("./contacts.json", "r") as file:
    contacts = json.loads(file.read())

def receive_messages(name):
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
                    title=f"[ {name} ]",
                    border_style="green",
                    padding=(1, 2)
                )

                console.print(message_panel)

        except (ConnectionResetError, ConnectionAbortedError):
            break

def send_messages(name):
    global connection, connection_pub_key

    buf = (len(name) - 3) // 2
    title = "[" + (" " * (buf + 1)) + "YOU" + (" " * (buf + 1)) + "]"

    system("clear")
    print_header()

    console.print(Text("\nEnter your message below. Press [Enter] to send.\n\n", "bright_black"))
    while True:
        try:
            msg = input("").strip()
            if not msg:
                continue

            print("\033[A\033[K", end="", flush=True)

            if msg.startswith("!"):
                run_command(msg[1:])
                continue

            emoji_instances = re.findall(r"<emoji:[^>]+>", msg)
            for instance in emoji_instances:
                if instance not in emojis.keys():
                    continue
                msg = msg.replace(instance, emojis[instance])

            encrypted_msg = cryption.encrypt_plaintext(connection_pub_key, msg)
            connection.sendall(encrypted_msg + b"<EOM>") # already bytes

            message = Text()
            message.append(msg, style="bold bright_blue")

            message_panel = Panel(
                message,
                title=title,
                border_style="blue",
                padding=(1, 2)
            )

            console.print(message_panel)
        except (BrokenPipeError, ConnectionResetError):
            break

def message_loop(name):
    global connection, connection_pub_key, priv_key

    connection.settimeout(None)

    receive_thread = threading.Thread(target=receive_messages, args=(name,), daemon=True)
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(name,), daemon=True)
    send_thread.start()

    try:
        while receive_thread.is_alive() and send_thread.is_alive():
            sleep(1)
    except KeyboardInterrupt:
        receive_thread.join()
        send_thread.join()
        connection.close()
        print("\nClosing messenger...")
        exit(0)

def handshake():
    global connection, connection_pub_key, priv_key

    pub_key, priv_key = genkey.genkey("ELM")
    connection.sendall(f"START KEY EXCHANGE HANDSHAKE | {pub_key} | END KEY EXCHANGE HANDSHAKE".encode())

    connection.settimeout(10.0)
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
        console.print(Text("    Handshake successful.", "bold bright_green"))
        return
    else:
        print("Unsuccessful handshake, please restart the client.")
        exit(0)

    return





def listen(ip=None, contacts=None):
    global connection

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", 4500))
        sock.settimeout(0.125)
        sock.listen(1)

        conn, connected_ip = sock.accept()
        if ip:
            if connected_ip[0] == ip:
                connection = conn
                return True
            else:
                conn.close()
        else:
            console.print(Text("CONNECTION ATTEMPT RECEIVED FROM " + connected_ip[0], "bold bright_green"))

    except (socket.timeout, OSError):
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




def command_line_utility():
    system("clear")
    print_header()
    print("\n\n")

    prompt = "self@" + get("http://api.ipify.org").text + " #> "

    while True:
        command = input(prompt)
        run_command(command)

def run_command(command):
    match command:
        case "help":
            display = Text()
            display.append("Usable commands and aliases:\n", style="bold bright_white")
            display.append("COMMAND", style="bold bright_cyan")
            display.append(" | ALIAS | ", style="bold bright_blue")
            display.append("PURPOSE\n\n", style="bold bright_magenta")
            def add_command(cmd, alias, purpose):
                display.append(cmd, style="bright_cyan")
                display.append(" | " + alias + " | ", style="bright_blue")
                display.append(purpose + "\n", style="bright_magenta")

            add_command("cmod add <name>@<IPv4 address>", "N/A", "Create a new contact with a specified name and IPv4 address.")

            console.print(display)

        case "ls-c" | "ls-contacts" | "list-contacts":
            display = Text()
            display.append("Contacts:\n", style="bold bright_white")
            foo = ""
            for name, ip in contacts.items():
                foo += f"{name} -> {ip}\n"
            display.append(foo, style="white")
            console.print(display)

        case "clear":
            system("clear")
            print_header()
            print("\n\n")

        case "exit":
            print("\nClosing messenger...")
            exit(0)

        case _:
            print("Invalid command.")
    return


def print_header():
    system("clear")
    welcome = r"""       
      _______  ___       ___      ___ 
     /"     "||"  |     |"  \    /"  |
    (: ______)||  |      \   \  //   |
     \/    |  |:  |      /\\  \/.    |
     // ___)_  \  |___  |: \.        |
    (:      "|( \_|:  \ |.  \    /:  |
     \_______) \_______)|___|\__/|___|
    """
    console.print(Text("|" + ("=" * (console.width - 2)) + "|", "blue_violet"), justify="center")
    console.print(Text(welcome, "bold blue_violet"), justify="center")
    console.print(Text("|" + ("=" * (console.width - 2)) + "|", "blue_violet"), justify="center")

def main():
    try:
        print_header()

        choice_tree = r"""
        
        
        
        ┏━ (1) Message with a contact
        ┃
        ┣━━ (2) Listen for connections
        ┃
        ┣━━━━ (3) Command-line utility for ELM
        ┃
        ┗━━━━━━━━ (4) Exit
"""
        console.print(Text(choice_tree, "blue_violet"), justify="left")

        choice = ""
        while choice not in ["1", "2", "3"]:
            choice = input(" " * 20 + "> ")
            if choice not in ["1", "2", "3"]:
                print("Invalid choice.")
                sleep(2)
                print("\033[A\033[K", end="", flush=True)
                print("\033[A\033[K", end="", flush=True)

        match choice:
            case "1":
                contact = input("\n\n" + " " * 20 + "Enter contact name: ")
                if contact not in contacts.keys():
                    console.print(Text(" " * 22 + f"Contact not '{contact}' found.", "bold bright_red"))
                    console.print(Text(" " * 24 + "Redirecting to the command-line utility...", "red"))
                    command_line_utility()
                else:
                    ip = contacts[contact]
                    print(f"Attempting connection to {contact}@{ip}:4500 | {datetime.now(UTC)} UTC")

                    while not connection:
                        if listen(ip):
                            break
                        if connect(ip):
                            break

                    print(f"Successfully connected to {contact}@{ip}:4500 | {datetime.now(UTC)} UTC")
                    handshake()
                    message_loop(contact)

            case "3":
                command_line_utility()

            case "4":
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("\nClosing messenger...")
        exit(0)

if __name__ == "__main__":
    main()