import socket
import threading
import json
import re
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

emojis = {
"grinning_face>": "😀",
       "<emoji:grinning_face_with_big_eyes>": "😃",                                                                                               
       "<emoji:grinning_face_with_smiling_eyes>": "😄",                                                                                           
       "<emoji:beaming_face_with_smiling_eyes>": "😁",                                                                                            
       "<emoji:grinning_squinting_face>": "😆",                                                                                                   
       "<emoji:grinning_face_with_sweat>": "😅",                                                                                                  
       "<emoji:rolling_on_the_floor_laughing>": "🤣",                                                                                             
       "<emoji:face_with_tears_of_joy>": "😂",                                                                                                    
       "<emoji:slightly_smiling_face>": "🙂",                                                                                                     
       "<emoji:upside_down_face>": "🙃",   
       "<emoji:winking_face>": "😉", 
       "<emoji:smiling_face_with_smiling_eyes>": "😊",                                                                                            
       "<emoji:smiling_face_with_halo>": "😇",                                                                                                    
       "<emoji:smiling_face_with_hearts>": "🥰",                                                                                                  
       "<emoji:smiling_face_with_heart_eyes>": "😍",                                                                                              
       "<emoji:star_struck>": "🤩",  
       "<emoji:face_blowing_a_kiss>": "😘",
       "<emoji:kissing_face>": "😗", 
       "<emoji:smiling_face>": "☺️",  
       "<emoji:kissing_face_with_closed_eyes>": "😚",                                                                                             
       "<emoji:kissing_face_with_smiling_eyes>": "😙",                                                                                            
       "<emoji:face_savoring_food>": "😋", 
       "<emoji:face_with_tongue>": "😛",   
       "<emoji:winking_face_with_tongue>": "😜",                                                                                                  
       "<emoji:zany_face>": "🤪",    
       "<emoji:squinting_face_with_tongue>": "😝",                                                                                                
       "<emoji:money_mouth_face>": "🤑",   
       "<emoji:hugging_face>": "🤗", 
       "<emoji:face_with_hand_over_mouth>": "🤭",                                                                                                 
       "<emoji:shushing_face>": "🤫",
       "<emoji:thinking_face>": "🤔",
       "<emoji:zipper_mouth_face>": "🤐",  
       "<emoji:face_with_raised_eyebrow>": "🤨",                                                                                                  
       "<emoji:neutral_face>": "😐", 
       "<emoji:expressionless_face>": "😑",
       "<emoji:face_without_mouth>": "😶", 
       "<emoji:smirking_face>": "😏",
       "<emoji:unamused_face>": "😒",
       "<emoji:face_with_rolling_eyes>": "🙄",                                                                                                    
       "<emoji:grimacing_face>": "😬",                       
       "<emoji:lying_face>": "🤥",
       #<emoji: Hand gestures       
       "<emoji:waving_hand>": "👋",  
       "<emoji:raised_back_of_hand>": "🤚",
       "<emoji:hand_with_fingers_splayed>": "🖐",                                                                                                  
       "<emoji:raised_hand>": "✋",  
       "<emoji:vulcan_salute>": "🖖",
       "<emoji:ok_hand>": "👌",      
       "<emoji:pinched_fingers>": "🤌",    
       "<emoji:pinching_hand>": "🤏",
       "<emoji:victory_hand>": "✌️",  
       "<emoji:crossed_fingers>": "🤞",    
       "<emoji:love_you_gesture>": "🤟",   
       "<emoji:sign_of_the_horns>": "🤘",  
       "<emoji:call_me_hand>": "🤙", 
       "<emoji:backhand_index_pointing_left>": "👈",                                                                                              
       "<emoji:backhand_index_pointing_right>": "👉",                                                                                             
       "<emoji:backhand_index_pointing_up>": "👆",                                                                                                
       "<emoji:middle_finger>": "🖕",
       "<emoji:backhand_index_pointing_down>": "👇",                                                                                              
       "<emoji:index_pointing_up>": "☝️",   
       "<emoji:thumbs_up>": "👍",    
       "<emoji:thumbs_down>": "👎",  
       "<emoji:raised_fist>": "✊",  
       "<emoji:oncoming_fist>": "👊",
       "<emoji:left_facing_fist>": "🤛",   
       "<emoji:right_facing_fist>": "🤜",  
       "<emoji:clapping_hands>": "👏",     
       "<emoji:raising_hands>": "🙌",
       "<emoji:open_hands>": "👐",   
       "<emoji:palms_up_together>": "🤲",  
       "<emoji:handshake>": "🤝",    
       "<emoji:folded_hands>": "🙏",
    
       #<emoji: Animals & Nature    
       "<emoji:dog_face>": "🐶",     
       "<emoji:cat_face>": "🐱",     
       "<emoji:mouse_face>": "🐭",   
       "<emoji:hamster>": "🐹",      
       "<emoji:rabbit_face>": "🐰",  
       "<emoji:fox>": "🦊",          
       "<emoji:bear>": "🐻",         
       "<emoji:panda>": "🐼",        
       "<emoji:polar_bear>": "🐻‍❄️",  
       "<emoji:koala>": "🐨",        
       "<emoji:tiger_face>": "🐯",   
       "<emoji:lion>": "🦁",         
       "<emoji:cow_face>": "🐮",     
       "<emoji:pig_face>": "🐷",     
       "<emoji:frog>": "🐸",         
       "<emoji:monkey_face>": "🐵",  
       "<emoji:chicken>": "🐔",      
       "<emoji:penguin>": "🐧",      
       "<emoji:bird>": "🐦",         
       "<emoji:baby_chick>": "🐤",   
       "<emoji:hatching_chick>": "🐣",     
       "<emoji:front_facing_baby_chick>": "🐥",                                                                                                   
       "<emoji:duck>": "🦆",         
       "<emoji:eagle>": "🦅",        
       "<emoji:owl>": "🦉",          
       "<emoji:bat>": "🦇",          
       "<emoji:wolf>": "🐺",         
       "<emoji:boar>": "🐗",         
       "<emoji:horse_face>": "🐴",   
       "<emoji:unicorn>": "🦄",      
       "<emoji:honeybee>": "🐝",     
       "<emoji:bug>": "🐛",          
       "<emoji:butterfly>": "🦋",    
       "<emoji:snail>": "🐌",        
       "<emoji:lady_beetle>": "🐞",  
       "<emoji:ant>": "🐜",          
       "<emoji:mosquito>": "🦟",     
       "<emoji:microbe>": "🦠",      
       "<emoji:bouquet>": "💐",      
       "<emoji:cherry_blossom>": "🌸",     
       "<emoji:rose>": "🌹",         
       "<emoji:hibiscus>": "🌺",     
       "<emoji:sunflower>": "🌻",    
       "<emoji:blossom>": "🌼",      
       "<emoji:tulip>": "🌷",        
       "<emoji:palm_tree>": "🌴",
       "<emoji:cactus>": "🌵",       
       "<emoji:herb>": "🌿",         
       "<emoji:four_leaf_clover>": "🍀",   
       "<emoji:maple_leaf>": "🍁",   
       "<emoji:fallen_leaf>": "🍂",  
       "<emoji:leaf_fluttering_in_wind>": "🍃",

       #<emoji: Objects             
       "<emoji:fire>": "🔥",         
       "<emoji:droplet>": "💧",      
       "<emoji:water_wave>": "🌊",   
       "<emoji:jack_o_lantern>": "🎃",     
       "<emoji:christmas_tree>": "🎄",     
       "<emoji:fireworks>": "🎆",    
       "<emoji:sparkler>": "🎇",     
       "<emoji:sparkles>": "✨",     
       "<emoji:balloon>": "🎈",      
       "<emoji:party_popper>": "🎉", 
       "<emoji:confetti_ball>": "🎊",
       "<emoji:collision>": "💥",    
       "<emoji:money_bag>": "💰",    
       "<emoji:gem_stone>": "💎",    
       "<emoji:crown>": "👑",        
       "<emoji:ring>": "💍",         
       "<emoji:light_bulb>": "💡",   
       "<emoji:bomb>": "💣",         
       "<emoji:smoking>": "🚬",      
       "<emoji:coffin>": "⚰️",        
       "<emoji:headstone>": "🪦",    
       "<emoji:crystal_ball>": "🔮", 
       "<emoji:prayer_beads>": "📿", 
       "<emoji:barber_pole>": "💈",  
       "<emoji:alembic>": "⚗️",       
       "<emoji:telescope>": "🔭",    
       "<emoji:microscope>": "🔬",   
       "<emoji:hole>": "🕳",          
       "<emoji:shopping_cart>": "🛒",
       "<emoji:gift>": "🎁",         
       "<emoji:red_envelope>": "🧧", 
       "<emoji:ribbon>": "🎀",       
       "<emoji:joystick>": "🕹",      
       "<emoji:teddy_bear>": "🧸",   
       "<emoji:kite>": "🪁",         
       "<emoji:parachute>": "🪂",    
       "<emoji:boomerang>": "🪃",    
       "<emoji:magic_wand>": "🪄",   
       "<emoji:yo_yo>": "🪀",        
       "<emoji:kite>": "🪁",         
       "<emoji:puzzle_piece>": "🧩", 
       "<emoji:chess_pawn>": "♟",    
       "<emoji:diamond_suit>": "♦️",  
       "<emoji:club_suit>": "♣️",     
       "<emoji:heart_suit>": "♥️",    
       "<emoji:spade_suit>": "♠️",    
       "<emoji:red_paper_lantern>": "🏮",  
       "<emoji:notebook>": "📓",     
       "<emoji:notebook_with_decorative_cover>": "📔",                                                                                            
       "<emoji:ledger>": "📒",       
       "<emoji:page_with_curl>": "📃",  
}

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
        raise KeyboardInterrupt

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
    pass



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
                with open("./contacts.json", "r") as file:
                    contacts = file.read()
                contacts = json.loads(contacts)

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
            case "4":
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("\nClosing messenger...")
        exit(0)

if __name__ == "__main__":
    main()