import logging
import operator
import os
import random

import numpy as np

logger = logging.getLogger('reachy.tictactoe')

q = os.path.join(os.path.dirname(__file__), 'Q-value.npz')
Q = np.load(q)

Q = {1: Q['QX'], 2: Q['QO']}


def value_actions(board, next_player=1):
    # return random(board, next_player);
    return best_move(board, next_player)

def random(board, next_player=1):
    possible_actions = np.where(np.array(board) == 0)[0]
    logger.info(possible_actions)
    random.shuffle(possible_actions)
    logger.info(possible_actions)
    return possible_actions

def next_move(board, move, next_player=1):
    next_board = board.copy()
    next_board[move] = next_player
    return next_board


def score(board):
    if board.get_winner() == 'robot':
        return 10
    elif board.get_winner() == 'human':
        return -10
    else:
        return 0


def minimax(board, next_player=1):
    if board.is_end():
        return score(board)
    elif next_player == 1:
        possible_actions = np.where(np.array(board) == 0)[0]
        temp = []
        for possible in possible_actions:
            next_board = board.copy()
            next_board[possible] = next_move(board, possible, next_player)
            next_player = 2
            temp[possible] = minimax(next_board, next_player)
            return max(temp)
    elif next_player == 2:
        possible_actions = np.where(np.array(board) == 0)[0]
        temp = []
        for possible in possible_actions:
            next_board = board.copy()
            next_board[possible] = next_move(board, possible, next_player)
            next_player = 1
            temp[possible] = minimax(next_board, next_player)
            return min(temp)

def best_move(board, player=2):
    best = -1000
    best_move = None
    possible_actions = np.where(np.array(board) == 0)[0]
    for action in possible_actions:
        next_board = board.copy()
        next_board[action] = player
        score = minimax(next_board, player)
        if score > best:
            best = score
            best_move = action
    return best_move