# penpen
pen^2 - anonymous electronic message-in-a-bottle system.  

### What is it?
I was inspired by the app called ["Bottled"](https://www.bottledapp.com/), which allows everyone to send messages to random others around the globe. I thought it might be interesting to create something similar, but with a decentralised and anonymous approach. That's how the idea for pen^2 came about.

### How does it work?
pen^2 uses the Tor anonymous network and its "hidden services" functionality to enable your computer to send and receive messages anonymously from strangers on the internet.  
To protect you from spam, we employ a proof-of-work system (similar to what Bitcoin or HashCash uses). Essentially, your computer needs to perform some brute force calculations to send a message.  
  
Please remember that Tor itself is **not** 100% anonymous. It does not provide theoretical anonymity.

### How to use it?
Install Tor on your machine and run it in a manner appropriate for your operating system:  
`tor --ControlPort 9051`  
Then install the dependencies with `pip install -r requirements.txt`  
and start everything with `python main.py`

✨🦄📝
