import threading
import time

from requests import post

from posenet import config, simple_pose
from tictactoe.reachy_tictactoe import game_launcher
from reachy_sdk import ReachySDK
first_play = False


def happy_antennas(reachy):
    reachy.head.l_antenna.speed_limit = 0.0
    reachy.head.r_antenna.speed_limit = 0.0

    reachy.head.l_antenna.goal_position = 0.0
    reachy.head.r_antenna.goal_position = 0.0


def sad_antennas(reachy):
    reachy.head.l_antenna.speed_limit = 70.0
    reachy.head.r_antenna.speed_limit = 70.0

    reachy.head.l_antenna.goal_position = 140.0
    reachy.head.r_antenna.goal_position = -140.0

    time.sleep(5.0)

    reachy.head.l_antenna.goal_position = 0.0
    reachy.head.r_antenna.goal_position = 0.0


def navigation_function():
    while True:
        print("Navigate to 5.76")
        data = {'x': 5.76, 'y': 0.661, 'theta': 0.0}
        post(url='http://10.10.0.1:5000/' + '/goal', json=data)
        time.sleep(30)
        print("Navigate to 9.46")
        data = {'x': 9.46, 'y': -1.47, 'theta': 0.0}
        post(url='http://10.10.0.1:5000/' + '/goal', json=data)
        time.sleep(30)


def main(reachy, posenet=1, tictactoe=1, navigation=True):
    global first_play
    if navigation:
        print("launch navigation")
        thread = threading.Thread(target=navigation_function, daemon=True)
        thread.start()
    if tictactoe:
        reachy.turn_on('head')
        print("Reachy Tic Tac Toe")
        reachy.head.l_antenna.goal_position = 140.0
        print("Reachy Tic Tac Toe")
        reachy.head.r_antenna.goal_position = -140.0
        print("Reachy Tic Tac Toe")
        reachy.head.look_at(1, 0.0, 0.0, 1)
        output = simple_pose.main(reachy)
        # config.detection[0] = 2
    print("Reachy Tic Tac Toe")
    while True:
        print("Reachy Tic Tac Toe")
        for i in range(len(config.detection)):
            if config.detection[i] == 1:
                happy_antennas(reachy)
            elif config.detection[i] == 0:
                sad_antennas(reachy)
            elif config.detection[i] == 2 and not first_play:
                first_play = True
                winner = game_launcher.main(reachy, '/home/reachy/reachy_mobile_reachy/gamelog')
                reachy.turn_off_smoothly('head')
                reachy.turn_off_smoothly('r_arm')
                return winner

    return None


if __name__ == '__main__':
    reachy = ReachySDK(host='localhost')
    main(reachy)
