import socket
import sys
import selectors
import types


class Server:
    def __init__(self):
        self.__hostname = "localhost"
        self.__port = 50000
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((self.__hostname, self.__port))
        self.__sel = selectors.DefaultSelector()

    def startServer(self):
        self.__server.listen()
        # Set the socket to non-blocking state
        self.__server.setblocking(False)
        # Register the socket to be monitored for reading
        self.__sel.register(self.__server, selectors.EVENT_READ, data=None)

    def acceptClient(self, sock):
        conn, addr = sock.accept()
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        # use bitwise OR to know when the client is ready for reading and writing
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.__sel.register(conn, events, data=data)

    def waitForClient(self):
        # Wait until the socket is ready for I/O
        # With timeout as None the call will block until it is ready
        # The event contains a key and mask, where key.fileobj is the socket
        event = self.__sel.select(timeout=None)
        for key, mask in event:
            # Listening socket, accept connection
            if key.data is None:
                self.acceptClient(key.fileobj)
            else:
                # Client socket that has been accepted
                self.serviceConnection(key, mask)

    def serviceConnection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            getData = sock.recv(1024)
            if getData:
                data.outb += getData
            else:
                print(f"Closing connection to {data.addr}")
                self.__sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print(f"Echoing {data.outb!r} to {data.addr}")
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]

    def sendMessage(self, msg):
        self.__connectionSocket.send(msg.encode())

    def closeConnection(self):
        self.__sel.close()


if __name__ == "__main__":
    server = Server()
    server.startServer()
    try:
        while True:
            server.waitForClient()
    except KeyboardInterrupt:
        pass
    finally:
        server.closeConnection()
