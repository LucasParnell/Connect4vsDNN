import random

import numpy as np
from scipy.signal import convolve2d


class Minimax(object):
    """ Minimax object that takes a current connect four board state
    """

    board = None

    def __init__(self, board):
        self.board = board

    def bestMove(self, depth, state, player):

        opp_player = -player

        # enumerate all legal moves
        legal_moves = {}  # will map legal move states to their alpha values
        for col in range(7):
            # if column i is a legal move...
            if self.isLegalMove(col, state):
                # make the move in column 'col' for curr_player
                temp = self.makeMove(state, col, player)
                legal_moves[col] = -self.search(depth - 1, temp, opp_player)

        best_alpha = -99999999
        best_move = None
        moves = legal_moves.items()
        random.shuffle(list(moves))
        for move, alpha in moves:
            if alpha >= best_alpha:
                best_alpha = alpha
                best_move = move

        return best_move

    def search(self, depth, state, player):
        """ Searches the tree at depth 'depth'
            By default, the state is the board, and curr_player is whomever
            called this search

            Returns the alpha value
        """

        # enumerate all legal moves from this state
        legal_moves = []
        for i in range(7):
            # if column i is a legal move...
            if self.isLegalMove(i, state):
                # make the move in column i for curr_player
                temp = self.makeMove(state, i, player)
                legal_moves.append(temp)

        # if this node (state) is a terminal node or depth == 0...
        if depth == 0 or len(legal_moves) == 0 or self.gameIsOver(state):
            # return the heuristic value of node
            return self.value(state, player)
        # determine opponent's color
        opp_player = -player

        alpha = -99999999
        for child in legal_moves:
            if child == None:
                print("child == None (search)")
            alpha = max(alpha, -self.search(depth - 1, child, opp_player))
        return alpha

    def isLegalMove(self, column, state):
        """ Boolean function to check if a move (column) is a legal move
        """

        for i in range(6):
            if state[i][column] == 0:
                # once we find the first empty, we know it's a legal move
                return True

        # if we get here, the column is full
        return False

    def gameIsOver(self, state):
        if self.checkConnected(state, 1, 4) >= 1:
            return True
        elif self.checkConnected(state, -1, 4) >= 1:
            return True
        else:
            return False

    def makeMove(self, state, column, color):
        """ Change a state object to reflect a player, denoted by color,
            making a move at column 'column'

            Returns a copy of new state array with the added move
        """

        temp = [x[:] for x in state]
        for i in range(6):
            if temp[i][column] == 0:
                temp[i][column] = color
                return temp

    def value(self, state, player):
        """ Simple heuristic to evaluate board configurations
            Heuristic is (num of 4-in-a-rows)*99999 + (num of 3-in-a-rows)*100 +
            (num of 2-in-a-rows)*10 - (num of opponent 4-in-a-rows)*99999 - (num of opponent
            3-in-a-rows)*100 - (num of opponent 2-in-a-rows)*10
        """
        opp_player = -player

        my_fours = self.checkConnected(state, player, 4)
        my_threes = self.checkConnected(state, player, 3)
        my_twos = self.checkConnected(state, player, 2)
        opp_fours = self.checkConnected(state, opp_player, 4)

        opp_threes = self.checkConnected(state, opp_player, 3)
        opp_twos = self.checkConnected(state, opp_player, 2)
        if opp_fours > 0:
            return -100000
        else:
            return (my_fours * 100000 + my_threes * 100 + my_twos) - (opp_fours * 100000 + opp_threes * 100 + opp_twos)

    def checkConnected(self, state, player, index):
        state = np.array(state)
        horizontal_kernel = np.array([[1, 1, 1, 1]])
        vertical_kernel = np.transpose(horizontal_kernel)
        diag1_kernel = np.eye(4, dtype=np.uint8)
        diag2_kernel = np.fliplr(diag1_kernel)
        detection_kernels = [horizontal_kernel, vertical_kernel, diag1_kernel, diag2_kernel]

        kernels = detection_kernels
        kernel_max = []
        for i in range(0, len(kernels)):
            k_max = convolve2d(state == player, kernels[i], mode="valid").max()
            kernel_max.append(k_max)
        return kernel_max.count(index)
