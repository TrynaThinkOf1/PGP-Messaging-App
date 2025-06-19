import socket
import threading
import json
import re
import subprocess
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

    priv_key, pub_key = genkey.genkey()
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
            connection = conn
            return True, connected_ip

    except (socket.timeout, OSError):
        pass
    finally:
        sock.close()
    return False

def send_connect_req(ip):
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
    try:
        system("clear")
        print_header()
        print("\n\n")

        prompt = Text("self@" + get("http://api.ipify.org").text + " !> ", style="bold dark_slate_gray1")

        while True:
            console.print(prompt, end="")
            command = input("")
            run_command(command)
    except KeyboardInterrupt:
        main()

def run_command(command):
    try:
        match command:
            case "help":
                display = Text()
                display.append("Usable commands and aliases:\n", style="bold bright_white")
                display.append("    In order to execute any of these commands while inside of the messenger rather than the CLU,\n     simply add a '!' directly in front of the command.\n\n", style="bright_white")

                display.append("COMMAND", style="bold bright_cyan")
                display.append(" | ALIAS | ", style="bold bright_blue")
                display.append("PURPOSE\n\n", style="bold bright_magenta")
                def add_command(cmd, alias, purpose):
                    display.append(cmd, style="bright_cyan")
                    display.append(" | " + alias + " | ", style="bright_blue")
                    display.append(purpose + "\n", style="bright_magenta")

                display.append("conn utility (connection-tools) [\n", style="bold light_goldenrod1")
                add_command("    conn <name>", "N/A", "Same as messaging a contact through the main menu.")
                add_command("    conn once <IPv4 address>", "N/A", "Connect to an IP address without adding it to your contacts.")
                display.append("]\n", style="bold light_goldenrod1")

                display.append("\ncmod utility (contact-modifier) [\n", style="bold chartreuse1")
                add_command("    cmod add <name>@<IPv4 address>", "N/A", "Create a new contact with a specified name and IPv4 address.")
                add_command("    cmod del <name>", "N/A", "Delete a contact from the contact book by name.")
                add_command("    cmod altname <name> <new name>", "N/A", "Change the name of a contact.")
                add_command("    cmod altip <name> <new IPv4 address>", "N/A", "Change the IPv4 address of the contact.")
                display.append("]\n", style="bold chartreuse1")

                display.append("\nOther contact utils [\n", style="bold cyan2")
                display.append("]\n", style="bold cyan2")

                display.append("\nCommand execution (external, or without this CLU) [\n", style="bold sky_blue1")
                add_command("    $<bash/zsh command to be executed>", "N/A", "Execute a terminal command, returning any output.")
                add_command("    !<command to be executed>", "N/A", "Execute a CLU command while not in the CLU (can include a bash execution using '!$<cmd>').")
                display.append("]\n", style="bold sky_blue1")

                console.print(display)

            case "ls-c" | "ls-contacts" | "list-contacts":
                display = Text()
                display.append("Contacts:\n", style="bold bright_white")
                foo = ""
                for name, ip in contacts.items():
                    foo += f"{name} -> {ip}\n"
                display.append(foo, style="white")
                console.print(display)

            case x if x.startswith("conn "):
                command = command.removeprefix("conn ")
                if command.startswith("once "):
                    ip = command.removeprefix("once ")
                    if len(ip.split(".")) != 4:
                        console.print(Text("Invalid IPv4 address format! Format is 4 series of 3 digit numbers, separated by periods.", style="red"))
                        return

                    print(f"Attempting connection to {ip}:4500 | {datetime.now(UTC)} UTC")

                    while not connection:
                        if listen(ip):
                            break
                        if send_connect_req(ip):
                            break

                    print(f"Successfully connected to {ip}:4500 | {datetime.now(UTC)} UTC")
                    handshake()
                    message_loop("ANONYMOUS")
                else:
                    contact = command
                    if contact not in contacts.keys():
                        console.print(Text(f"Contact not '{contact}' found.", "bold bright_red"))
                        return
                    else:
                        ip = contacts[contact]
                        print(f"Attempting connection to {contact}@{ip}:4500 | {datetime.now(UTC)} UTC")

                        while not connection:
                            if listen(ip):
                                break
                            if send_connect_req(ip):
                                break

                        print(f"Successfully connected to {contact}@{ip}:4500 | {datetime.now(UTC)} UTC")
                        handshake()
                        message_loop(contact)

            case x if x.startswith("cmod "):
                command = command.removeprefix("cmod ")
                if command.startswith("add "):
                    command = command.removeprefix("add ")
                    command = command.split("@")
                    if len(command) != 2:
                        console.print(Text("Invalid contact format! Format is <name>@<IPv4 address>. The 'help' command brings you to a help menu.", style="red"))
                        return
                    name, ip = command
                    if len(ip.split(".")) != 4:
                        console.print(Text("Invalid IPv4 address format! Format is 4 series of 3 digit numbers, separated by periods.", style="red"))
                        return
                    contacts[name] = ip
                    with open("./contacts.json", "w") as file:
                        file.write(json.dumps(contacts))

                    console.print(Text(f"Contact {name}@{ip} added successfully!", style="bold green"))

                elif command.startswith("del "):
                    name = command.removeprefix("del ")
                    if name in contacts:
                        del contacts[name]
                        with open("./contacts.json", "w") as file:
                            file.write(json.dumps(contacts))

                        console.print(Text(f"Contact {name} deleted successfully!", style="bold green"))
                    else:
                        console.print(Text(f"Contact not '{contact}' found.", "bold bright_red"))

                elif command.startswith("altname "):
                    command = command.removeprefix("altname ")
                    command = command.split(" ")
                    if len(command) != 2:
                        console.print(Text("Invalid command format, 'cmod altname <contact name> <new contact name>'.", "red"))
                        return
                    contact, new_name = command
                    if contact in contacts.keys():
                        ip = contacts[contact]
                        del contacts[contact]
                        contacts[new_name] = ip
                        with open("./contacts.json", "w") as file:
                            file.write(json.dumps(contacts))
                        console.print(Text(f"Contact changed from {contact}@{ip} -> {new_name}@{ip} successfully!", style="bold green"))
                        return
                    else:
                        console.print(Text(f"Contact '{contact}' not found.", "red"))

                elif command.startswith("altip "):
                    command = command.removeprefix("altip ")
                    command = command.split(" ")
                    if len(command) != 2:
                        console.print(Text("Invalid command format, 'cmod altip <contact name> <new IPv4 address>'.", "red"))
                        return
                    contact, new_ip = command
                    if contact in contacts.keys():
                        ip = contacts[contact]
                        del contacts[contact]
                        contacts[contact] = new_ip
                        with open("./contacts.json", "w") as file:
                            file.write(json.dumps(contacts))
                        console.print(Text(f"Contact changed from {contact}@{ip} -> {contact}@{new_ip} successfully!", style="bold green"))
                    else:
                        console.print(Text(f"Contact '{contact}' not found.", "red"))

            case x if x.startswith("$"):
                command = command.removeprefix("$")
                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    console.print(Text(output.decode(), style="bright_blue"))
                except subprocess.CalledProcessError as e:
                    console.print(Text(e.output.decode(), style="bright_red"))

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
    except KeyboardInterrupt:
        print("\n")
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
        while choice not in ["1", "2", "3", "4"]:
            choice = input(" " * 20 + "> ")
            if choice not in ["1", "2", "3", "4"]:
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
                        if send_connect_req(ip):
                            break

                    print(f"Successfully connected to {contact}@{ip}:4500 | {datetime.now(UTC)} UTC")
                    handshake()
                    message_loop(contact)

            case "2":
                try:
                    system("clear")
                    print_header()
                    print("\n\n")
                    console.print(Text("Listening for connections...", "bright_blue"))
                    while True:
                        c = listen()
                        if c:
                            connected_ip = c[1]
                            console.print(Text("CONNECTION ATTEMPT RECEIVED FROM " + connected_ip[0], "bold bright_green"))
                            if connected_ip in contacts.values():
                                console.print(Text(f"This connection appears to be from your contact '{[name for name, ip in contacts.items() if ip == connected_ip][0]}'.", "bright_blue"))
                            else:
                                console.print(Text("The IPv4 address from the connection does not appear in your contacts.", "bright_blue"))
                            connect = input("Would you like to connect (y/n): ")
                            if connect != "y":
                                connection.close()
                                continue
                            else:
                                print(f"Successfully connected to {connected_ip}:4500 | {datetime.now(UTC)} UTC")
                                handshake()
                                message_loop(connected_ip)
                        else:
                            continue
                except KeyboardInterrupt:
                    main()

            case "3":
                command_line_utility()

            case "4":
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("\nClosing messenger...")
        exit(0)

if __name__ == "__main__":
    main()