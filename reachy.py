import time

from reachy_sdk import ReachySDK

from posenet import config
from posenet import simple_pose
from tictactoe.reachy_tictactoe import game_launcher

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


def main(reachy):
    global first_play
    reachy.turn_on('head')
    reachy.head.look_at(0.95, 0.5, -0.2, 1.0)
    reachy.head.l_antenna.goal_position = 140.0
    reachy.head.r_antenna.goal_position = -140.0
    time.sleep(5)
    # output = simple_pose.main(reachy)
    while True:
        config.detection[0] = 2
        for i in range(len(config.detection)):

            if config.detection[i] == 1:
                happy_antennas(reachy)
            elif config.detection[i] == 0:
                sad_antennas(reachy)
            elif config.detection[i] == 2 and not first_play:
                # reachy.turn_on('head')
                # reachy.turn_on('r_arm')
                # reachy.head.look_at(0.95, -0.9, -0.5, 1.0)
                # time.sleep(3.0)
                first_play = True
                winner = game_launcher.main(reachy, '/home/reachy/reachy_mobile_reachy/gamelog')
                reachy.turn_off('head')
                reachy.turn_off('r_arm')
                return winner

if __name__ == '__main__':
    reachy = ReachySDK(host='localhost')
    main(reachy)
