import random
import time
import unittest

import numpy as np


def random_player(board, next_player=1):
    possible_actions = np.where(np.array(board) == 0)[0]
    random.shuffle(possible_actions)
    return possible_actions[0]


def score(board):
    if get_winner(board) == 'robot':
        return 10
    elif get_winner(board) == 'human':
        return -10
    elif get_winner(board) == 'draw':
        return 0


def minmax(board, player):
    if get_winner(board) != 'nobody':
        return score(board)
    elif player == 2:
        possible_actions = np.where(np.array(board) == 0)[0]
        temp = [-1000] * 9
        for possible in possible_actions:
            next_board = board.copy()
            next_board[possible] = 2
            temp[possible] = minmax(next_board, 1)
        return max(temp)
    else:
        possible_actions = np.where(np.array(board) == 0)[0]
        temp = [1000] * 9
        for possible in possible_actions:
            next_board = board.copy()
            next_board[possible] = 1
            temp[possible] = minmax(next_board, 2)
        return min(temp)


def best_move(board, player=2):
    best = -1000
    best_move = None
    possible_actions = np.where(np.array(board) == 0)[0]
    for action in possible_actions:
        next_board = board.copy()
        next_board[action] = player
        score = minmax(next_board, 1)
        if score > best:
            best = score
            best_move = action
    return best_move


def check_winner(board):
    win_configurations = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),

        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),

        (0, 4, 8),
        (2, 4, 6),
    )
    for win_configuration in win_configurations:
        if board[win_configuration[0]] == board[win_configuration[1]] == board[win_configuration[2]] != 0:
            return board[win_configuration[0]]
    return 0


def get_winner(board):
    winner = check_winner(board)
    if winner == 1:
        return 'human'
    elif winner == 2:
        return 'robot'
    elif np.sum(board == 0) == 0:
        return 'draw'
    elif winner == 0:
        return 'nobody'


class TestMinimax(unittest.TestCase):
    def test_something(self):
        for i in range(100):
            self.board = np.zeros((3, 3), dtype=int).flatten()
            self.player = random.randint(1, 2)
            while get_winner(self.board) == 'nobody':
                if self.player == 1:
                    move = random_player(self.board)
                    self.board[move] = 1
                else:
                    move = best_move(self.board)
                    self.board[move] = 2
                if self.player == 1:
                    self.player = 2
                else:
                    self.player = 1
            result = get_winner(self.board)
            self.assertIn(result, ['robot', 'draw'])


if __name__ == '__main__':
    unittest.main()
