"""
26/01/2023 11:45
Georgi Tyufekchiev
War of F(u)nctions
A 1v1 turn based game where you try to guess the other players function
This file contains the Interface application, which will print messages to the player
"""


class Interface:

    def __init__(self):
        self.__name = None

    def setName(self, name):
        self.__name = name

    @staticmethod
    def askUsername():
        return input("Enter username: ")

    @staticmethod
    def displayPoly(poly):
        print("Your polynomial is %s" % poly)

    def welcomeMessage(self):
        print("Welcome %s" % self.__name)

    @staticmethod
    def displayLockedModes(unlockedModes):
        modes = ['quadratic', 'cubic', 'all']
        cost = ["150", "250", "350"]

        for i, mode in enumerate(modes, start=1):
            if mode not in unlockedModes:
                print(f"{i}.{mode} - {cost[i-1]}")

    @staticmethod
    def displayProgressOptions():
        options = ['Money', 'Achievements']
        for i, option in enumerate(options, start=1):
            print(f"{i}.{option}")

    @staticmethod
    def displayModes(modes):
        print("MODES:")
        for i, mode in enumerate(modes, start=1):
            print(f"{i}.{mode}")

    @staticmethod
    def displayOptions():
        options = ['Play', 'Save', 'Load', 'Unlock', 'Progress', 'Exit']
        print("OPTIONS:")
        for i, option in enumerate(options, start=1):
            print(f"{i}.{option}")

    @staticmethod
    def selectOption():
        return int(input("Pick an option:"))

    @staticmethod
    def playerTurn():
        guess = input("It is your turn. Enter your guess: ").split()
        coeff = [int(number) for number in guess]
        return coeff

    def displayWin(self):
        print(f"Your guess was right! {self.__name} won!")

    def displayWaitingMsg(self):
        print(f"{self.__name} you will play next turn.")

    def displayLost(self):
        print(f"The other player guess' was right! {self.__name} you lost.")
