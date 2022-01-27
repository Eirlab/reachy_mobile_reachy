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
    reachy.head.l_antenna.goal_position = 140.0
    reachy.head.r_antenna.goal_position = -140.0
    reachy.head.look_at(1, 0.0, 0.0, 1)
    time.sleep(3)
    # output = simple_pose.main(reachy)
    while True:
        config.detection[0] = 2
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
