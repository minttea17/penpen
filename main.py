# main.py
import threading
from service import app  # Import the Flask app
from client import run_client  # Import the client function
from stem.control import Controller
import stem
import os
import time

def run_app():
    print(' * Connecting to tor')
    key_path = os.path.expanduser('tor_key')
    try:
        controller1 = Controller.from_port("127.0.0.1", 9051)
    except:
        print("Unable to connect; please check your Tor connection.")
        print("Note that Tor may be censored by your ISP, system administrator, etc.")
        return
    with controller1 as controller:
        controller.authenticate()

        if not os.path.exists(key_path):
            service = controller.create_ephemeral_hidden_service({80: 5000}, await_publication = True)
            print("Started a new hidden service with the address of %s.onion" % service.service_id)

            with open(key_path, 'w') as key_file:
                key_file.write('%s:%s' % (service.private_key_type, service.private_key))
        else:
            with open(key_path) as key_file:
                key_type, key_content = key_file.read().split(':', 1)

            service = controller.create_ephemeral_hidden_service({80: 5000}, key_type = key_type, key_content = key_content, await_publication = True)
            print("Resumed %s.onion" % service.service_id)
        try:
            app.run()
        finally:
            print(" * Shutting down our hidden service")

if __name__ == '__main__':
    print(r"""
                               /\    ____   
  _ ___      ____     _ ___   /  \  / _  `. 
 J '__ J    F __ J   J '__ J /_/\_\J_/-7 .' 
 | |--| |  | _____J  | |__| |L_/\_J`-:'.'.' 
 F L__J J  F L___--. F L  J J      .' ;_J__ 
J  _____/LJ\______/FJ__L  J__L    J________L
|_J_____F  J______F |__L  J__|    |________|
L_J                                         

""")

    # Create a thread for the Flask app
    flask_thread = threading.Thread(target=run_app)
    flask_thread.start()
    time.sleep(10)

    # Run the client in the main thread
    run_client()
