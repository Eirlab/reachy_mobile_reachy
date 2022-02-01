"""
Allows you to play a game of tictactoe with the reachy
"""
import argparse
import logging
import time

import numpy as np
import zzlog
from datetime import datetime
from glob import glob

if __package__ is None or __package__ == '':
    from tictactoe_playground import TictactoePlayground
    from rl_agent import value_actions
else:
    from tictactoe.reachy_tictactoe.tictactoe_playground import TictactoePlayground
    from tictactoe.reachy_tictactoe.rl_agent import random_action

logger = logging.getLogger('reachy.tictactoe')


def run_game_loop(tictactoe_playground):
    """
    Orchestrates the game loop
    :param tictactoe_playground: an instance of TictactoePlayground
    :return: the winner of the game
    """
    logger.setLevel(logging.WARNING)
    logger.info('Game start')
    # Check that the board is empty (the 9 box of the grid have to be empty)
    logger.info('Checking if the board is completely empty.')
    # status, board = tictactoe_playground.analyze_board()
    status = False
    cpt_idle_behavior = 0
    while not status:
        status, board = tictactoe_playground.analyze_board()
        if np.any(board) or not status:
            status = False
        else:
            status = True
    # while True:
    #     logger.info('Board cleaned')
    #     if tictactoe_playground.is_ready(board):
    #         break
    #     tictactoe_playground.run_random_idle_behavior()
    last_board = tictactoe_playground.reset()
    logger.info(f'size last_board = {np.shape(last_board)}')
    logger.info(f'size last_board = {np.shape(last_board)}')
    first_round = True
    # reachy_turn = tictactoe_playground.coin_flip()
    reachy_turn = True
    first_round = True
    # if reachy_turn:
    #          tictactoe_playground.run_my_turn()
    # else:
    #     tictactoe_playground.run_your_turn()
    while True:
        tictactoe_playground.random_antenna()

        if not status:
            logger.warning('Invalid board detected')
            status, board = tictactoe_playground.analyze_board()
            logger.info(f'ok = {status}')
            continue
        if not reachy_turn:
            if tictactoe_playground.has_human_played(board, last_board):
                cpt_idle_behavior = 0
                reachy_turn = True
                if not tictactoe_playground.is_final(board):
                    logger.info('Next turn', extra={
                        'next_player': 'Reachy',
                    })
                # tictactoe_playground.run_my_turn()
            else:
                cpt_idle_behavior += 1
                tictactoe_playground.run_random_idle_behavior(cpt_idle_behavior)

        # If we have detected some cheating or any issue We reset the whole game
        if (tictactoe_playground.incoherent_board_detected(board) or
                tictactoe_playground.cheating_detected(board, last_board, reachy_turn)):
            # Check again to be sure
            logger.info('! Incoherent board detected')
            status, double_check_board = tictactoe_playground.analyze_board()
            logger.info(f'recheck board : {double_check_board}')
            # the board checked it's different that the last board (the good one)
            if np.any(double_check_board != last_board):
                # We're pretty sure something weird happened!
                tictactoe_playground.shuffle_board()
                break
            else:
                # False detection, we will check again next loop
                continue

        # When it's the robot's turn to play
        # We decide which action to take and plays it
        if (not tictactoe_playground.is_final(board)) and reachy_turn:
            if first_round:
                action = random_action(board)
                first_round = False
            else:
                action, _ = tictactoe_playground.choose_next_action(board)
            board = tictactoe_playground.play(action, board)

            last_board = board
            reachy_turn = False
            if not tictactoe_playground.is_final(board):
                # tictactoe_playground.run_your_turn()
                logger.info('Next turn', extra={
                    'next_player': 'Human',
                })

        # If the game is over, determine who is the winner
        # and behave accordingly
        if tictactoe_playground.is_final(board):
            winner = tictactoe_playground.get_winner(board)

            if winner == 'robot':
                tictactoe_playground.run_celebration()
            elif winner == 'human':
                tictactoe_playground.run_defeat_behavior()
            else:
                tictactoe_playground.run_draw_behavior()
            return winner
        status, board = tictactoe_playground.analyze_board()
        logger.info(f'ok = {status}')
    logger.info('Game end')


def main(reachy, log):
    """
    Main function to run the game
    :param reachy: an instance of Reachy sdk
    :param log: an instance of Logger
    :return: None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-file')
    args = parser.parse_args()

    if args.log_file is not None:
        n = len(glob(f'{args.log_file}*.log')) + 1

        now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')
        args.log_file = log
        args.log_file += f'-{n}-{now}.log'

    logger_reachy = zzlog.setup(
        logger_root='',
        filename=args.log_file,
    )

    logger_reachy.info(
        'Creating a Tic Tac Toe playground.'
    )

    with TictactoePlayground(reachy) as tictactoe_playground:
        tictactoe_playground.setup()
        game_played = 0
        winner = run_game_loop(tictactoe_playground)
        if tictactoe_playground.need_cooldown():
            logger_reachy.warning('Reachy needs cooldown')
            tictactoe_playground.enter_sleep_mode()
            tictactoe_playground.wait_for_cooldown()
            tictactoe_playground.leave_sleep_mode()
            logger_reachy.info('Reachy cooldown finished')
        return winner

