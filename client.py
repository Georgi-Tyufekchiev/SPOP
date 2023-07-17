"""
26/01/2023 11:45
Georgi Tyufekchiev
War of F(u)nctions
A 1v1 turn based game where you try to guess the other players function
This file contains the Client application, which will connect to the Server application
"""
import re
import socket
import sys
from enum import Enum
import csv
from interface import Interface
from polynomials import Poly
from signature import *
import os
import os.path


class States(Enum):
    """
    Class for enumerating the states of the game
    """
    MENU = 1
    CONNECTING = 2
    CONNECTED = 3
    PLAY = 4
    WON = 5
    LOST = 6
    CLOSE = 7


class Client:
    """
    Class for the client, which will handle messages and game play
    """

    def __init__(self):

        self.__serverAddress = ("localhost", 50000)
        # Create TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__STATE = States.CONNECTING
        self.__name = None
        self.__money = 10000
        self.__games = {"total": 0, "won": 0, "lost": 0}
        self.__unlockedModes = ["linear"]
        self.__achievements = []
        self.__ID = None
        # Create the Interface object
        self.interface = Interface()
        # Create the Polynomial object, which will handle all poly operations
        self.__poly = Poly()

    def connect(self):
        """
        Connect to the server and start receiving messages
        :return: n/a
        """
        self.sock.connect(self.__serverAddress)
        self._rcvMsg()

    def _sendMsg(self, msg=None):
        """
        Send messages to the server and handle certain game states
        :param msg: message to be sent. It has to be encoded or be a byte object
        :return: n/a
        """
        if self.__STATE == States.CONNECTING:
            # Send the username to the server
            # Change the game state
            # Wait for a message
            self.sock.send(msg.encode('utf-8'))
            self.__STATE = States.CONNECTED
            self._rcvMsg()

        if self.__STATE == States.PLAY:
            # Send messages regarding the playing state
            # e.g. Send 1 to indicate the player want to start the game
            if msg == '1':
                self.sock.send(msg.encode('utf-8'))
                self._rcvMsg()

            # Send 300 indicating the player's guess was wrong
            if msg == '300':
                self.sock.send(msg.encode('utf-8'))
                self._rcvMsg()

        if self.__STATE == States.WON:
            # When the player has won send 200 to the server
            # Since the game is over change the game state to the Menu
            self.sock.send(msg.encode('utf-8'))
            self.__STATE = States.MENU
            self._handleStates()

    def _rcvMsg(self):
        """
        Receive messages and handle states
        :return: n/a
        """
        while True:
            msg = self.sock.recv(1024).decode('utf-8')

            # if msg:
            #     print(msg)
            try:
                # When the message is a code i.e. an integer as str, convert it to an int
                msg = int(msg)
            except ValueError:
                pass

            # The server send the code 2 to indicate the client has connected
            # The client is supposed to send the username to the server to complete the connection
            if msg == 2:
                self.__STATE = States.CONNECTING
                self._handleStates(msg)

            # The server sends the code 3 to indicate the connection is complete
            if msg == 3:
                self.__STATE = States.MENU
                self._handleStates()

            # The server send the code 400 to indicate the player lost the game
            if msg == 400:
                self.__STATE = States.LOST
                self._handleStates()

            # Send messages regarding the playing state of the game
            if self.__STATE == States.PLAY:
                self._handleStates(msg)

    def _askOption(self):
        """
        Prompt the client to choose a meny option
        :return: n/a
        """
        option = self.interface.selectOption()
        # Option 1 is to play a game
        if option == 1:
            self.__STATE = States.PLAY
            self.__games['total'] += 1
            # Send to the server code 1 to indicate the player wants to start a game
            self._sendMsg(msg='1')

        if option == 2:
            self.saveGame()

        if option == 3:
            self.loadGame()

        if option == 4:
            self.interface.displayLockedModes(self.__unlockedModes)
            option = self.interface.selectOption()

            if option == 1 and self.__money >= 150:
                print("Mode unlocked!")
                self.__money -= 150
                self.__unlockedModes.append('quadratic')
            elif option == 2 and self.__money >= 250:
                print("Mode unlocked!")
                self.__money -= 250
                self.__unlockedModes.append('cubic')
            elif option == 3 and self.__money >= 350:
                print("Mode unlocked!")
                self.__unlockedModes.append('all')
                self.__money -= 350
            else:
                print("Not enough money")

            self._askOption()

        if option == 5:
            self.interface.displayProgressOptions()
            option = self.interface.selectOption()
            if option == 1:
                print(f"Money - {self.__money}")
            if option == 2:
                print(f"Achievements - {self.__achievements}")

            self._askOption()

        if option == 6:
            self.__STATE = States.CLOSE
            self.closeConnection()

    def _handleStates(self, msg=None):
        """
        Handle state of the game
        :param msg: any message received from the server
        :return: n/a
        """
        if self.__STATE == States.CONNECTING:
            self.__name = self.interface.askUsername()
            # set the username in the interface
            self.interface.setName(self.__name)
            # send the username to the server
            self._sendMsg(self.__name)

        if self.__STATE == States.MENU:
            # print a welcome message and display the options
            self.interface.welcomeMessage()
            self.interface.displayOptions()
            # ask the user to choose a menu option
            self._askOption()

        if self.__STATE == States.PLAY:
            # The server will send a message "ID 'playerID'"

            if msg.startswith("ID"):
                # take the 'playerID'
                self.__ID = msg.split()[1]
                self.interface.displayModes(self.__unlockedModes)
                option = self.interface.selectOption()
                if option == 1:
                    # generate the polynomial to guess
                    self.__poly.linear()
                if option == 2:
                    self.__poly.quadratic()
                if option == 3:
                    self.__poly.cubic()
                # create a string of the polynomial
                polyString = self.__poly.poly
                # for now display the polynomial to test the gameplay
                self.interface.displayPoly(polyString)

            # the server will send a 'begin' msg to the player, who's turn to guess has came
            if msg == "begin":
                # ask the user to input their guess for the poly coefficients
                coeffs: list = self.interface.playerTurn()
                # create the Cartesian graph
                self.__poly.createGrid()
                # evaluate the polynomial with the user guess and see if it is correct
                isCorrectGuess = self.__poly.acceptCoeff(coeffs)
                if isCorrectGuess:
                    # print the winning message
                    # return them to the menu\
                    self.__games['won'] += 1
                    self.__money += 100
                    if "win 1 game" not in self.__achievements:
                        self.__achievements.append("win 1 game")
                    self.interface.displayWin()
                    self.__STATE = States.WON
                    self._handleStates()
                else:
                    self._sendMsg('300')

            # the server sends "next" msg to indicate to the player they have to wait for their turn
            if msg == "next":
                # print a waiting message to the player
                self.interface.displayWaitingMsg()
                # wait to receive a 'being' msg
                self._rcvMsg()

        if self.__STATE == States.WON:
            # send the code 200 to the server to indicate the player has won
            self._sendMsg("200")

        if self.__STATE == States.LOST:
            # print a message saying the player lost the game
            # return them to the menu
            self.__games['lost'] += 1
            self.interface.displayLost()
            self.__STATE = States.MENU
            self._handleStates()

    def saveGame(self):
        fields = ['Name', 'Money', 'Games Played', 'Games Won', 'Games Lost', 'Win-rate', 'Achievements',
                  'Unlocked Modes']

        if self.__games['total'] != 0:
            winRate = str((self.__games['won'] / self.__games['total']) * 100) + "%"
        else:
            winRate = "0%"
        modes = ""
        for mode in self.__unlockedModes:
            modes += mode + " "

        achievements = ""
        for achievement in self.__achievements:
            achievements += achievement + " "

        data = [self.__name, self.__money, self.__games['total'], self.__games['won'], self.__games['lost'], winRate,
                achievements, modes]
        filename = f"{self.__name}_save.csv"
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvwriter.writerow(data)
            csvfile.close()

        pk = f"receiver_{self.__name}.pem"
        sk = f"private_{self.__name}.pem"
        cur_dir = os.getcwd()
        fileList = os.listdir(cur_dir)
        if pk not in fileList or sk not in fileList:
            keySetup(self.__name)

        fileSignature = sign(filename, self.__name)
        self.sock.send(b'500')
        self.sock.send(fileSignature)
        print("SAVE SUCCESSFUL")
        self._askOption()

    def loadGame(self):

        try:
            if os.stat(f"{self.__name}_save.csv").st_size == 0:
                print("File is empty!")
                self._askOption()
            with open(f"{self.__name}_save.csv", 'r') as f:
                self.sock.send(b'501')
                name = self.__name
                self.sock.send(name.encode("utf-8"))
                csvread = csv.reader(f)
                _ = next(csvread)
                _ = next(csvread)
                data = next(csvread)
                self.__money = int(data[1])
                self.__games['total'] = int(data[2])
                self.__games['won'] = int(data[3])
                self.__games['lost'] = int(data[4])
                self.__achievements = re.sub('[^a-zA-Z1-9]', ' ', data[6]).split()
                self.__unlockedModes = re.sub('[^a-zA-Z]', ' ', data[7]).split()
                print(self.__money)
                print(self.__achievements)
                print(self.__unlockedModes)
                self._askOption()
        except OSError:
            print("File does not exist!")
            self._askOption()

    def closeConnection(self):
        """
        Stop the connection to the server
        :return: n/a
        """
        if self.__STATE == States.CLOSE:
            self.sock.send(b'7')
            self.sock.close()
            sys.exit(0)


if __name__ == "__main__":
    c = Client()
    c.connect()
