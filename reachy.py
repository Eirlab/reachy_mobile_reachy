import os
import time
from threading import Thread

from reachy_sdk import ReachySDK

from posenet import pose_camera
from posenet import config
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


def main():
    global first_play
    camera = Thread(target=pose_camera.main, daemon=True)
    camera.start()
    config.detection = 2
    while True:
        if config.detection == 1:
            happy_antennas(reachy)
        elif config.detection == 0:
            sad_antennas(reachy)
        elif config.detection == 2 and not first_play:
            reachy = "reachy"
            reachy = ReachySDK(host='localhost')
            reachy.turn_on('head')
            reachy.turn_on('r_arm')
            reachy.head.look_at(0.95, -0.9, -0.3, 1.0)
            sad_antennas(reachy)
            reachy.head.l_antenna.goal_position = 0.0
            reachy.head.r_antenna.goal_position = 0.0
            print("Play !")
            first_play = True
            game_launcher.main(reachy, '/home/reachy/reachy_mobile_reachy/gamelog')
            reachy.turn_off('head')
            reachy.turn_off('r_arm')

if __name__ == '__main__':
    main()
