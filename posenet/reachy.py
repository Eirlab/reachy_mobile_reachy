import os
import time
from threading import Thread

from reachy_sdk import ReachySDK

import config
import pose_camera

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
    reachy = ReachySDK(host='localhost')
    reachy.turn_on('head')
    reachy.turn_on('r_arm')
    reachy.head.look_at(0.95, -0.9, -0.3, 1.0)
    camera = Thread(target=pose_camera.main, daemon=True)
    camera.start()
    sad_antennas(reachy)
    while True:
        if config.detection == 1:
            happy_antennas(reachy)
        elif config.detection == 0:
            sad_antennas(reachy)
        elif config.detection == 2 and not first_play:
            reachy.head.l_antenna.goal_position = 0.0
            reachy.head.r_antenna.goal_position = 0.0
            print("Play !")
            first_play = True
            play()
    reachy.turn_off('head')
    reachy.turn_off('r_arm')

def play():
    os.system("echo -e 'reachy\n' | sudo -S systemctl start tictactoe_launcher.service")

if __name__ == '__main__':
    main()
