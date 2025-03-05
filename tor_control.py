from stem import Signal
from stem.control import Controller

def change_tor_circuit():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM) # Request a new circuit