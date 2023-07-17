"""
26/01/2023 11:45
Georgi Tyufekchiev
War of F(u)nctions
A 1v1 turn based game where you try to guess the other players function
This file contains the Server application, which can accept multiple client connections
"""
import csv
import socket
from _thread import *
from enum import Enum
from time import sleep

from Crypto.Hash import SHA384
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


class States(Enum):
    """
    Class for enumerating the states of the game
    """
    NONE = 0
    CONNECTED = 1
    MENU = 2
    START_GAME = 3
    PLAYING = 4
    DISCONNECT = 5
    WELCOME = 6
    WAIT_TURN = 7
    LOST = 8
    ADMIN = 10


class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__port = 50000
        self.__hostname = "localhost"
        self.__STATE = {}
        self.__GAME_STATE = {}
        self.__counter = 0
        self.__signatures = {}

    def startServer(self):
        """
        Start the server by binding the socket and start listening for clients
        :return:
        """
        self.sock.bind((self.__hostname, self.__port))
        print("Server is listening on port %d" % self.__port)
        self.sock.listen()
        while True:
            self._acceptClient(self.sock)

    def _acceptClient(self, sock):
        """
        Accept a client connection and start a thread for them
        :param sock: the server socket
        :return:
        """
        client, address = sock.accept()
        playerID = self.__counter
        self.__STATE[playerID] = States.CONNECTED
        self.__GAME_STATE[playerID] = States.NONE
        self.__counter += 1
        print("Connected to", address)
        start_new_thread(self._handleClient, (client, playerID))

    def _handleClient(self, conn, playerID):
        """
        Handle the client connection and states of the game
        :param conn: the client connection socket
        :param playerID: the id of the player
        :return: n/a
        """

        def _startGame(state, playerID):
            """
            Start the game for a client
            :param state: the state of the server
            :param playerID: the id for a player
            :return:
            """
            if state == States.START_GAME:
                self.__STATE[playerID] = States.PLAYING
                ID = "ID %d" % playerID
                # send the id to client
                conn.send(ID.encode('utf-8'))
                # a temporary rule on who to start first
                if playerID % 2 == 0:
                    conn.send(b'begin')
                else:
                    conn.send(b'next')
                    # the second player is in a state of waiting
                    self.__GAME_STATE[playerID] = States.WAIT_TURN

        def _handleCode(code):
            if code == 200:
                # set the game state of the other player to lost
                if playerID == 0:
                    self.__GAME_STATE[playerID + 1] = States.LOST
                else:
                    self.__GAME_STATE[playerID - 1] = States.LOST

                # transition to a menu state
                self.__STATE[playerID] = States.MENU

            if code == 300:
                print("SEND next for ", playerID)
                conn.send(b'next')
                self.__GAME_STATE[playerID] = States.WAIT_TURN
                if playerID % 2 == 0:
                    self.__GAME_STATE[playerID + 1] = States.PLAYING
                else:
                    self.__GAME_STATE[playerID - 1] = States.PLAYING

            if code == 778:
                player = conn.recv(1024).decode('utf-8')
                filename = f"{player}_save.csv"
                print(filename)
                try:
                    with open(filename, 'r') as f:
                        csvread = csv.reader(f)
                        _ = next(csvread)
                        _ = next(csvread)
                        data = next(csvread)
                        data = str(','.join(data))
                        f.close()
                        print(data)
                    conn.send(data.encode('utf-8'))
                except OSError:
                    conn.send(b'704')

        while True:

            if self.__STATE[playerID] == States.CONNECTED:
                # send code 2 to indicate the client has connected and needs to send a username
                conn.send(b'2')

            if self.__GAME_STATE[playerID] == States.WAIT_TURN:
                # while the player is in a state of waiting check the game state
                # for now they will lose
                # print(playerID, self.__GAME_STATE)
                while True:
                    try:
                        if self.__GAME_STATE[playerID] == States.LOST:
                            self.__STATE[playerID] = States.MENU
                            # send to the user that they lost the game
                            conn.send(b'400')
                            break
                        if self.__GAME_STATE[playerID] == States.PLAYING:
                            print("SEND BEGIN for ", playerID)
                            conn.send(b'begin')
                            break
                    except KeyError:
                        pass
                    sleep(1)

            msg = conn.recv(1024).decode('utf-8')

            if msg:
                print(msg)

            try:
                # when the message is a code -> make it an int
                msg = int(msg)
            except ValueError:
                pass

            if self.__STATE[playerID] == States.CONNECTED:
                # send code 3 to the client to indicate the connection is complete
                # transition to meny state
                conn.send(b"3")
                self.__STATE[playerID] = States.MENU

            if self.__STATE[playerID] == States.MENU:
                # the player has sent code 1 indicating they want to play a game
                if msg == 1:
                    # transition to a state of playing a game
                    self.__STATE[playerID] = States.START_GAME
                    _startGame(States.START_GAME, playerID)

            if msg == 777:
                self.__STATE[playerID] = States.ADMIN

            if msg == 778:
                _handleCode(778)

            # a player has sent code 200 indicating they won the game
            # for now we have only 2 players
            if msg == 200:
                _handleCode(200)

            # a player has sent code 300 indicating their guess was wrong
            # now we have the turn to the next player
            if msg == 300:
                _handleCode(300)

            if msg == 500:
                sig = conn.recv(1024)
                self.__signatures[playerID] = sig
                print(self.__signatures)

            if msg == 501:
                name = conn.recv(1024).decode('utf-8')
                recipient_key = RSA.import_key(open(f"receiver_{name}.pem").read())
                signature = pkcs1_15.new(recipient_key)
                oldSign = open(f"signature_{name}", "rb").read()
                filename = f"{name}_save.csv"
                file = open(filename).read()
                hash = SHA384.new()
                hash.update(bytes(file.encode("utf8")))
                signature.verify(hash, oldSign)
                print("Valid file signature")

            if msg == 7:
                self.__STATE[playerID] = States.DISCONNECT
                self.closeConnection(conn, playerID)

    def closeConnection(self, conn, playerID):
        if self.__STATE[playerID] == States.DISCONNECT:
            print("STOPPING")
            conn.close()


if __name__ == "__main__":
    server = Server()
    server.startServer()
