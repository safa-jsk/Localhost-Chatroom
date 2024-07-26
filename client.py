import threading
import socket
import argparse
import os
import sys
import tkinter as tk

class Send(threading.Thread):

    # Listens for user input from command line

    # Sock the connected sock object
    # User (str) : The username provided by user

    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
    
    def run(self):
        # Listen for user input from the command line and send it to the server 
        # Typing Quit will close the connection and exit the app
        
        while True:
            print("{}: ".format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]
            
            # Type "QUIT" to leave Chatroom

            if message == "QUIT":
                self.sock.sendall("Server: {} has left the chat".format(self.name).encode('ascii'))
                break
            
            else:
                self.sock.sendall("{}: {}".format(self.name, message).encode('ascii'))
        
        print("\nQuitting...")
        self.sock.close()
        os.close(0)


class Receive(threading.Thread):

    # Listens for incoming messages from the server
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None
    
    def run(self):

        # Receives data from the server and displays it in the gui

        while True:
            message = self.sock.recv(4096).decode('ascii')

            if message:
                if self.messages:
                    self.messages.insert(tk.END, message)
                    print('Hi')
                    print(f"\r{message}\n{self.name}", end = "")
                
                # Send message to server for broadcasting
                else:
                    print(f"\r{message}\n{self.name}", end = "")
            
            else:
                print("\n No. We have lost connection to the server")
                print("\n Quitting...")
                self.sock.close()

                os._exit(0)


class Client:

    # Management of client-server connection and integration of GUI

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None


    def start(self):      
        print(f"Trying to connect to {self.host}:{self.port}")

        self.sock.connect((self.host, self.port))

        print(f"Successfully connected to {self.host}:{self.port}")
        print()

        self.name = input("Your name: ")
        print()

        print(f"Wwelcome, {self.name}! Getting ready to send and receive messages...")

        # Create Send and Receive Threads
        send = Send(self.sock, self.name)
        receive = Receive(self.sock, self.name)

        # Start Send and Receive Threads
        send.start()
        receive.start()

        self.sock.sendall("Server: {} has joined the chat!".format(self.name).encode('ascii'))
        print("\rReady! You may leave the Chatroom anytime by typing 'QUIT'.")
        print(f"{self.name}: ", end='')

        return receive


    def send(self, textInput):

        # Sends textInput data from the GUI
        message = textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, f"{self.name}: {message}")

        # Type "QUIT" to leave the Chatroom
        if message == "QUIT":
            self.sock.sendall("Server: {} has left the chat!".format(self.name).encode('ascii'))
            
            print("\n Quitting...")
            self.sock.close()
            os._exit(0)

        # Send message to server for broadcasting
        else:
            self.sock.sendall("{}: {}".format(self.name, message).encode('ascii'))


def main(host, port):
    # Initialize and Run GUI
    client = Client(host, port)
    receive = client.start()

    window = tk.Tk()
    window.title("Chatroom")

    fromMessage = tk.Frame(window)
    scrollBar = tk.Scrollbar(fromMessage)
    messages = tk.Listbox(fromMessage, yscrollcommand=scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    receive.messages = messages

    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
    fromEntry = tk.Frame(window)
    textInput = tk.Entry(fromEntry)

    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "Write your message here.")

    btnSend = tk.Button(
        master=window,
        text="Send",
        command=lambda: client.send(textInput)
    )

    fromEntry.grid(row=1, column=0, padx=10, sticky='ew')
    btnSend.grid(row=1, column=1, pady=10, sticky='ew')

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.mainloop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Chatroom Server")
    parser.add_argument('host', help = 'Interface the server listends at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port(default 1060)')

    args = parser.parse_args()

    main(args.host, args.p)