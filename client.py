import requests
import hashlib
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
import database
import datetime
import os
import requests
import json
import random

# Difficulty level for the proof-of-work
DIFFICULTY = 6  # Number of leading zeros required in the hash

tor_proxies = {'http': 'socks5h://127.0.0.1:9050', 
                'https': 'socks5h://127.0.0.1:9050'}

def proof_of_work(nonce_hex, difficulty):
    """Find a valid secret that satisfies the proof-of-work requirement."""
    prefix_str = '0' * difficulty
    secret = 0
    while True:
        hash_result = hashlib.sha256((nonce_hex+str(secret)).encode()).hexdigest()
        if hash_result.startswith(prefix_str):
            return secret, hash_result
        secret += 1

database.init_db()

def run_client():
    while True:
        if len(database.get_nodes()) == 0:
            print("You need to add at least one node for being able to send messages.")
            print("Choose option 4 to do that.\n")

        print("\nWhat you want to do?")
        print("1. Check for bottles")
        print("2. Send the bottle")
        print("3. Manage identity")
        print("4. Manage nodes")
        choice = int(input("> "))

        if choice == 1:
            messages = database.get_messages()
            for i in messages:
                print("----------------------------")
                print(datetime.datetime.fromtimestamp(i[2]).strftime('%Y-%m-%d %H:%M:%S'))
                print(f"Signed by {i[3]}")
                print("\n"+str(i[1], "utf-8"))

        if choice == 2:
            print("Input your message:")
            message = input("> ")
            signing_key = SigningKey.generate()
            signed = signing_key.sign(bytes(message, "utf-8")).hex()
            verify_key = bytes(signing_key.verify_key).hex()
            nodes = database.get_nodes_pub()

            ready = False

            while (len(nodes) != 0 and ready != True):
                node = random.choice(nodes)
                nodes.remove(node)
                print(f"Trying {node[0]}")
                try:
                    response = requests.get(f"http://{node[0]}.onion/hello", 
                                            proxies=tor_proxies)
                    if response.status_code == 200:
                        ready = True
                except requests.exceptions.RequestException:
                    continue

            if ready != True:
                print("There's no online nodes available now.\n")
                continue

            # Step 1: Get a secure nonce from the Flask app
            response = requests.get(f'http://{node[0]}.onion/start_pow',
                                    proxies=tor_proxies)
            if response.status_code != 200:
                print("Failed to get nonce:", response.json())
                exit(0)

            nonce_hex = response.json().get('nonce')
            print(f"Received nonce: {nonce_hex}")

            # Step 2: Solve the proof-of-work
            secret, valid_hash = proof_of_work(nonce_hex, DIFFICULTY)
            print(f"Secret: {secret}, Hash: {valid_hash}")

            # Step 3: Submit the valid nonce back to the Flask app
            pow_response = requests.post(f'http://{node[0]}.onion/receive', 
                                            json={'nonce': nonce_hex, 'secret': str(secret),
                                            'message': signed, 'verify_key': verify_key},
                                            proxies=tor_proxies)
            if pow_response.status_code == 200:
                print("Proof-of-work validated:", pow_response.json())
            else:
                print("Failed to validate proof-of-work:", pow_response.json())

        if choice == 3:
            print("You can delete your Tor hidden service key, if you want to.")
            print("It will change your onion address and revoke the old one.")
            print("Procced? (y/n)")
            option = input("> ")
            if option.lower() == "y":
                os.remove("tor_key")
                exit(0)

        if choice == 4:
            print("1. Add new node")
            print("2. Scan the network for new nodes")
            print("3. List all nodes")
            option = int(input("> "))

            if option == 1:
                address = input("Provide node's address: ")
                try:
                    response = requests.get(f"http://{address}.onion/hello", 
                                            proxies=tor_proxies)
                    if response.status_code == 200:
                        database.insert_node(address)
                        print("OK!")
                    else:
                        print("Invalid address")
                except requests.exceptions.RequestException:
                    print("Invalid address")

            if option == 2:
                count = 0
                asked = []
                depth = int(input("Specify depth: "))
                found_nodes = []
                my_nodes = database.get_nodes()

                for j in range(depth):
                    for i in my_nodes:
                        if i in asked:
                            continue
                        try:
                            response = requests.get(f"http://{i[1]}.onion/get_nodes", 
                                                    proxies=tor_proxies)
                            if response.status_code == 200:
                                found = json.loads(response.data)
                                print(f"Found {len(found)} nodes")
                                found_nodes = my_nodes + found
                            else:
                                print("Invalid address")
                        except requests.exceptions.RequestException:
                            print("Invalid address")

                        asked.append(i)
                    
                    for i in found_nodes:
                        try:
                            database.insert_node(i[0])
                            count+=1
                        except:
                            pass

                print("----------------------------")
                print(f"Total: {count} nodes added")
            
            if option == 3:
                nodes = database.get_nodes()
                for i in nodes:
                    print(f"id: {i[0]}, address: {i[1]}, added: {datetime.datetime.fromtimestamp(i[2]).strftime('%Y-%m-%d %H:%M:%S')}")