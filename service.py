from flask import Flask, request, abort, jsonify
import hashlib
import secrets
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import database
import requests
import random
import logging
from tor_control import change_tor_circuit

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True
database.init_db()
pow_list = []
# Difficulty level for the proof-of-work
DIFFICULTY = 6  # Number of leading zeros required in the hash

@app.before_request
def check_localhost():
    if request.remote_addr != '127.0.0.1':
        abort(403)

def proof_of_work(nonce, secret, difficulty):
    """Generate a hash with a given nonce and difficulty."""
    prefix_str = '0' * difficulty
    hash_result = hashlib.sha256((nonce+secret).encode()).hexdigest()
    return hash_result, hash_result.startswith(prefix_str)

@app.route('/receive', methods=['POST'])
def receive():
    """A protected method that requires proof-of-work."""
    data = request.json
    nonce = data.get('nonce')
    secret = data.get('secret')
    message = data.get('message')
    f_verify_key = data.get('verify_key')
    if nonce is None:
        return jsonify({"error": "Nonce is required"}), 400
    if secret is None:
        return jsonify({"error": "Secret is required"}), 400
    if message is None:
        return jsonify({"error": "Message is required"}), 400
    if f_verify_key is None:
        return jsonify({"error": "Verify key is required"}), 400
    if nonce not in pow_list:
        return jsonify({"error": "Nonce is invalid"}), 400

    # Validate the proof-of-work
    hash_result, valid = proof_of_work(nonce, secret, DIFFICULTY)
    if not valid:
        return jsonify({"error": "Invalid proof-of-work"}), 403

    # If valid, save the message and delete pow nonce
    pow_list.remove(nonce)
    try:
        verify_key = VerifyKey(bytes.fromhex(f_verify_key))
    except:
        return jsonify({"error": "Invalid verify key"}), 403
    try:
        to_save = verify_key.verify(bytes.fromhex(message))
    except BadSignatureError:
        return jsonify({"error": "Invalid signature"}), 403

    database.insert_message(to_save, f_verify_key)

    return jsonify({"message": "Message sent"}), 200

@app.route('/start_pow', methods=['GET'])
def start_pow():
    """Start a proof-of-work challenge with a secure nonce."""
    nonce = secrets.token_hex(16)  # Generates a secure random nonce (32 hex characters)
    pow_list.append(nonce)
    return jsonify({"nonce": nonce}), 200

@app.route('/hello', methods=['GET'])
def hello():
    return "Hi. pen^2 is running.", 200

@app.route('/introduce', methods=['POST'])
def introduce():
    """A protected method that requires proof-of-work."""
    data = request.json
    nonce = data.get('nonce')
    secret = data.get('secret')
    address = data.get('address')

    if nonce is None:
        return jsonify({"error": "Nonce is required"}), 400
    if secret is None:
        return jsonify({"error": "Secret is required"}), 400
    if address is None:
        return jsonify({"error": "Address is required"}), 400

    hash_result, valid = proof_of_work(nonce, secret, DIFFICULTY)
    if not valid:
        return jsonify({"error": "Invalid proof-of-work"}), 403

    # If valid, delete pow nonce
    pow_list.remove(nonce)
    change_tor_circuit()
    try:
        response = requests.get(f"http://{address}.onion/hello", 
                                proxies={'http': 'socks5h://127.0.0.1:9051', 
                                         'https': 'socks5h://127.0.0.1:9051'})
        if response.status_code == 200:
            database.insert_node(address)
            return jsonify({"message": "Introduction succeed"}), 200
        else:
            return jsonify({"error": "Invalid address"}), 403
    except requests.exceptions.RequestException:
        return jsonify({"error": "Invalid address"}), 403

app.route('/get_nodes', methods="GET")
def get_nodes():
    nodes = database.get_nodes_pub()
    return random.shuffle(nodes)

# app.run()
# offline mode