import socket
import sys
import selectors
import types

class Client:

    def __init__(self):
        self.__serverAddress = ("localhost",50000)
        self.__sel = selectors.DefaultSelector()

    def connect(self,messages):
        for i in range(2):
            connid = i + 1
            print(f"Starting connection {connid} to {self.__serverAddress}")
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.setblocking(False)
            # connect_ex will return an error indicator instead of an exception
            # IF the operation succeeded the indicator is 0
            # Useful for asynchronus connects
            sock.connect_ex(self.__serverAddress)
            event = selectors.EVENT_READ | selectors.EVENT_WRITE
            data = types.SimpleNamespace(
                connid=connid,
                msg=sum(len(m) for m in messages),
                recv=0,
                messages=messages.copy(),
                outb=b""
            )
            self.__sel.register(sock,event,data=data)

    def service(self):
        # Wait until the socket is ready for I/O
        # With timeout as None the call will block until it is ready
        # The event contains a key and mask, where key.fileobj is the socket
        event = self.__sel.select(timeout=None)
        for key, mask in event:
            # Listening socket, accept connection
            if key.data is not None:
                self.sendMessage(key, mask)

    def sendMessage(self,key,mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            getData = sock.recv(1024)
            if getData:
                print(f"Received {getData!r} from connection {data.connid}")
                data.recv += len(getData)
            if not getData or data.recv == data.msg:
                print(f"Closing connection {data.connid}")
                self.__sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.messages:
                data.outb = data.messages.pop(0)
            if data.outb:
                print(f"Sending {data.outb!r} to connection {data.connid}")

                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]


if __name__ == "__main__":
    messages = [b"Message 1 from client.", b"Message 2 from client."]

    client = Client()
    client.connect(messages)
    while True:
        client.service()