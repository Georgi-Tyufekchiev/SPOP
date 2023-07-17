"""
26/01/2023 11:45
Georgi Tyufekchiev
War of F(u)nctions
A 1v1 turn based game where you try to guess the other players function
This file contains the Polynomial application, which generates polynomials, evaluates them
and plots them on a Cartesian graph
"""
import math
from random import randint
import matplotlib.pyplot as plt
import numpy as np


class Poly:
    """
    Class for polynomial operations and plotting
    """

    def __init__(self):
        self.yPoints = []
        self.xPoints = []
        self.poly = ""

    def _evalpoly(self, coeff, x):
        """
        Evaluate a polynomial
        :param coeff: the coefficients for the poly
        :param x: the point to be evaluated at
        :return: the evaluation of the poly
        """
        y = 0
        for i in range(len(coeff)):
            y += coeff[i] * x ** i
        return y

    def createGrid(self):
        """
        Create the Cartesian graph
        :return:
        """
        # Take the biggest x point and biggest y point
        xMax, yMax = abs(max(self.xPoints)), abs(max(self.yPoints))
        xMin, yMin = abs(min(self.xPoints)), abs(min(self.yPoints))
        x = xMax
        y = yMax
        if not xMax > xMin:
            x = xMin
        if not yMax > yMin:
            y = yMin

        # set the boundaries of the graph
        xmin, xmax, ymin, ymax = -x - 5, x + 5, -y - 5, y + 5
        # set the line frequency
        if ymax < 50:
            tickFreq = ymax // 5
        elif 100 >= ymax >= 50:
            tickFreq = ymax // 10
        elif 500 >= ymax > 100:
            tickFreq = ymax // 10
        elif 1000 >= ymax > 500:
            tickFreq = ymax // 10
        else:
            tickFreq = 200

        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor("#ffffff")
        ax.set(xlim=(xmin - 5, xmax + 5), ylim=(ymin - 5, ymax + 5))
        # set bottom and let spines as x and y axes
        ax.spines['bottom'].set_position('zero')
        ax.spines['left'].set_position('zero')
        # remove the top and right spine
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # create the 'x' and 'y' labels or the graph
        ax.set_xlabel('$x$', size=14, labelpad=-24, x=1.02)
        ax.set_ylabel('$y$', size=14, labelpad=-21, y=1.02, rotation=0)
        plt.text(0.49, 0.49, r"$O$", ha='right', va='top',
                 transform=ax.transAxes,
                 horizontalalignment='center', fontsize=14)
        # create the major ticks to determine position of the tick labels
        x_ticks = np.arange(xmin, xmax, math.ceil(tickFreq/2))
        y_ticks = np.arange(ymin , ymax , tickFreq)
        ax.set_xticks(x_ticks[x_ticks != 0])
        ax.set_yticks(y_ticks[y_ticks != 0])
        # create minor ticks placed at each integer
        # ax.set_xticks(np.arange(xmin, xmax, tickFreq//2), minor=True)
        # ax.set_yticks(np.arange(ymin, ymax, tickFreq//2), minor=True)
        # draw major and minor grid lines
        ax.grid(which='both', color='grey', linewidth=1, linestyle='-', alpha=0.2)

    def _plotLine(self, x, y):
        """
        Plot the points for the polynomial and the line for the guess
        :param x: the x points
        :param y: the y points
        :return: a graph
        """
        plt.plot(self.xPoints, self.yPoints, 'ro', x, y)
        plt.show()

    def acceptCoeff(self, coeff):
        """
        Take the coeff from the player and evaluate the poly
        :param coeff: a list of coeff
        :return: bool
        """
        coefficients = coeff[::-1]
        yPoints = [self._evalpoly(coefficients, x) for x in self.xPoints]
        self._plotLine(self.xPoints, yPoints)
        if yPoints == self.yPoints:
            return True
        return False

    def sendPoly(self, coeff):
        """
        Create a string for the polynomial
        :param coeff: coeff for the polynomial
        :return: n/a
        """
        coeff = coeff[::-1]
        poly = "f(x) = "
        powers = len(coeff) - 1
        for i in range(len(coeff)):
            poly += f"{coeff[i]}*x^{powers} "
            if powers > 0:
                poly += "+ "
            powers -= 1

        self.poly = poly

    def generatePoly(self, n):
        coefficients = [randint(-5, 5) for _ in range(n)]
        # force the x points to be different
        xPoints = set()
        while len(xPoints) != n:
            xPoints.add(randint(-5, 5))

        self.xPoints = list(xPoints)
        self.yPoints = [self._evalpoly(coefficients, x) for x in self.xPoints]
        return coefficients

    def linear(self):
        """
        Create a linear function
        :return: n/a
        """
        coefficients = self.generatePoly(2)
        self.sendPoly(coefficients)

    def quadratic(self):
        coefficients = self.generatePoly(3)
        self.sendPoly(coefficients)

    def cubic(self):
        coefficients = self.generatePoly(4)
        self.sendPoly(coefficients)
        print(self.poly)


if __name__ == "__main__":
    p = Poly()
    p.linear()
    p.createGrid()
    p.acceptCoeff([5, 4])
