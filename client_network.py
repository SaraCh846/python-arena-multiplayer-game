import socket
import json

class NetworkClient:
    def __init__(self, server_ip, server_port): #store server address info
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None
        self.sock_file = None

    def connect(self): #connecting to game server by creating a TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip, self.server_port))
        self.sock_file = self.sock.makefile("r")
        print(f"Connected to server at {self.server_ip}:{self.server_port}")

    def send_message(self, message): #convert python dictionary to JSON string and send to server 
        json_message = json.dumps(message) + "\n"
        self.sock.sendall(json_message.encode())

    def receive_message(self): #receive messages from the server by converting JSON message back to python dictionary
        try:
            line = self.sock_file.readline()

            if not line:
                return None

            return json.loads(line.strip())

        except (ConnectionAbortedError, ConnectionResetError, OSError): #handling connection or socket errors
            return None
        except json.JSONDecodeError: #handle invalid JSON messages
            return None

    def close(self): #safe socket shutdown
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass #ignore errors if socket is already closed

        try: 
            if self.sock_file:
                self.sock_file.close()
        except OSError:
            pass

        try:
            if self.sock:
                self.sock.close()
                print("Connection closed")
        except OSError:
            pass

        #reset to allow clean reuse if needed
        self.sock = None
        self.sock_file = None