import logging
import operator
import os
import random

import numpy as np

logger = logging.getLogger('reachy.tictactoe')

q = os.path.join(os.path.dirname(__file__), 'Q-value.npz')
Q = np.load(q)

Q = {1: Q['QX'], 2: Q['QO']}


# Deprecated agent for random agent
# TODO : create smart agent
def value_actions_2(board, next_player=1):
    possible_actions = np.where(np.array(board) == 0)[0]

    possibilities = {}
    for action in possible_actions:
        next_board = board.copy()
        next_board[action] = next_player

        val = Q[next_player][tuple(next_board)]
        logger.info(val)
        possibilities[action] = val

    possibilities = sorted(possibilities.items(), key=operator.itemgetter(1))
    logger.error(possibilities)
    return possibilities


def value_actions(board, next_player=1):
    possible_actions = np.where(np.array(board) == 0)[0]
    logger.info(possible_actions)
    random.shuffle(possible_actions)
    logger.info(possible_actions)
    return possible_actions
