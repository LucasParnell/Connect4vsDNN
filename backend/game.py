# AI Randomly Places Piece
import random

import numpy as np
from scipy.signal import convolve2d

GRID_SIZE = [6, 7]
infinity = float('inf')

class Game(object):

    def __init__(self):
        self.grid = [[], [], [], [], [], []]
        self.horizontal_kernel = np.array([[1, 1, 1, 1]])
        self.vertical_kernel = np.transpose(self.horizontal_kernel)
        self.diag1_kernel = np.eye(4, dtype=np.uint8)
        self.diag2_kernel = np.fliplr(self.diag1_kernel)
        self.detection_kernels = [self.horizontal_kernel, self.vertical_kernel, self.diag1_kernel, self.diag2_kernel]

        for row in range(GRID_SIZE[0]):
            for col in range(GRID_SIZE[1]):
                self.grid[row].append(0)


    def update_only(self, last, player):

        if last is not None:
            lowestPoint = GRID_SIZE[0]

            column = last
            for row in range(0, 6, 1):
                if self.grid[row][column] == 0:
                    lowestPoint = row
                else:
                    break
            if lowestPoint == 6:
                return
            self.grid[lowestPoint][last] = player
        else:
            # Finds lowest point in chosen column
            lowestPoint = GRID_SIZE[0]
            aiSpot = [0, 0]

            while lowestPoint == GRID_SIZE[0]:
                column = random.randint(0, GRID_SIZE[1] - 1)
                for row in range(0, 6, 1):

                    if self.grid[row][column] == 0:
                        lowestPoint = row
                    else:
                        break

                # TODO(Add Board Full Check)

            aiSpot = [lowestPoint, column]

            self.grid[aiSpot[0]][aiSpot[1]] = player

    def checkWin(self, player):
        board = np.array(self.grid)
        for kernel in self.detection_kernels:
            if (convolve2d(board == player, kernel, mode="valid") == 4).any():
                return True
        return False



