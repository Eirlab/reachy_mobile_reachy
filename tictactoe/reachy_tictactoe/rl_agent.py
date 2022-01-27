import logging
import os
import random

import numpy as np

from tictactoe.reachy_tictactoe.utils import id2piece, piece2player

logger = logging.getLogger('reachy.tictactoe')

q = os.path.join(os.path.dirname(__file__), 'Q-value.npz')
Q = np.load(q)

Q = {1: Q['QX'], 2: Q['QO']}


def value_actions(board, next_player=1):
    # return random(board, next_player);
    return best_move(board)


def random_action(board, next_player=1):
    possible_actions = np.where(np.array(board) == 0)[0]
    logger.info(possible_actions)
    random.shuffle(possible_actions)
    logger.info(possible_actions)
    return possible_actions[0]


def score(board):
    if get_winner(board) == 'robot':
        return 10
    elif get_winner(board) == 'human':
        return -10
    elif get_winner(board) == 'draw':
        return 0


def minimax(board, player):
    if get_winner(board) != 'nobody':
        return score(board)
    elif player == 2:
        possible_actions = np.where(np.array(board) == 0)[0]
        temp = [-1000] * 9
        for possible in possible_actions:
            next_board = board.copy()
            next_board[possible] = 2
            temp[possible] = minimax(next_board, 1)
        return max(temp)
    else:
        possible_actions = np.where(np.array(board) == 0)[0]
        temp = [1000] * 9
        for possible in possible_actions:
            next_board = board.copy()
            next_board[possible] = 1
            temp[possible] = minimax(next_board, 2)
        return min(temp)


def best_move(board, player=2):
    best = -1000
    best_move = None
    possible_actions = np.where(np.array(board) == 0)[0]
    for action in possible_actions:
        next_board = board.copy()
        next_board[action] = player
        score = minimax(next_board, 1)
        if score > best:
            best = score
            best_move = action
    logger.warning(best)
    logger.warning(best_move)
    return best_move


def get_winner(board):
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

    for c in win_configurations:
        trio = set(board[i] for i in c)
        for identifier in id2piece.keys():
            if trio == {identifier}:
                winner = piece2player[id2piece[identifier]]
                if winner in ('robot', 'human'):
                    return winner
    if np.sum(board == 0) == 0:
        return 'draw'
    return 'nobody'