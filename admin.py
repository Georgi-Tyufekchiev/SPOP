"""
26/01/2023 11:45
Georgi Tyufekchiev
War of F(u)nctions
A 1v1 turn based game where you try to guess the other players function
This file contains the Admin application, which will connect to the Server application
"""
import socket


class Admin:
    def __init__(self):
        self.name = "Admin"
        self.serverAddress = ("localhost", 50000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """
        Connect to the server and start receiving messages
        :return: n/a
        """
        self.sock.connect(self.serverAddress)
        self.sendMsg("777")
        self.rcvMsg()

    def sendMsg(self, msg=None):
        self.sock.send(msg.encode('utf-8'))

    def rcvMsg(self):
        """
          Receive messages
          :return: n/a
          """
        while True:
            msg = self.sock.recv(2048).decode('utf-8')

            if msg:
                print(msg)
            try:
                # When the message is a code i.e. an integer as str, convert it to an int
                msg = int(msg)
            except ValueError:
                pass

            if msg == 2:
                msg = self.sock.recv(2048).decode('utf-8')
                return
            if msg == 704:
                print("Error!")

                return
            else:
                return

    def getPlayerStats(self):
        player = input("Enter player name: ")
        self.sendMsg("778")
        self.sendMsg(player)
        self.rcvMsg()

    def banPlayer(self):
        player = input("Enter player name: ")
        filename = f"{player}_save.csv"

        f = open(filename, "w+")
        f.close()
        print(f"{player} banned successfully!")
        return


if __name__ == "__main__":
    admin = Admin()
    admin.connect()
    option = ["Check Player", "Ban Player"]
    print("OPTIONS:")
    for i, opt in enumerate(option, start=1):
        print(f"{i}.{opt}")

    while True:
        getOption = int(input("Enter option: "))

        if getOption == 1:
            admin.getPlayerStats()
        elif getOption == 2:
            admin.banPlayer()
        else:
            continue
