import socket
import _thread

class Bidirectional_communication:
    def __init__(self):
        self.disconnected = True
        self.incoming_connection = socket.socket()
        self.outgoing_connection = socket.socket()

    def connect(self, ip, port):
        self.outgoing_connection.settimeout(5)
        self.outgoing_connection.connect((ip, port))
        self.disconnected = False

    def host(self, ip, port, onconnect, onreceive):
        self.incoming_connection.bind((ip, port))
        self.disconnected = False
        _thread.start_new(self.server, (onconnect, onreceive))

    def server(self, onconnect, onreceive):
        self.incoming_connection.listen(5)
        connected_socket, address = self.incoming_connection.accept()
        onconnect(address)
        while not self.disconnected:
            onreceive(connected_socket.recv(1024).decode())

    def send(self, data):
        self.outgoing_connection.send(data.encode())

    def disconnect(self):
        self.disconnected = True
        self.incoming_connection.close()
        self.outgoing_connection.close()