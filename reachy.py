import threading
import time

from requests import post, get

from playsound import playsound
from posenet import config, simple_pose
from tictactoe.reachy_tictactoe import game_launcher
from reachy_sdk import ReachySDK

import config

first_play = False
playing = False


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
    global playing

    nav_goals = [
        {'x': 8.52, 'y': -1.57, 'theta': 1.57},
        {'x': 5.76, 'y': 0.661, 'theta': 0.0},
        {'x': -9.31, 'y': 4.84, 'theta': 0.0},
        {'x': 3.91, 'y': -0.385, 'theta': 0.0}
    ]

    while True:
        i = 0
        while i < len(nav_goals):
            print("Navigate to coordinates: ", nav_goals[i])

            post(url='http://10.10.0.1:5000/goal', json=nav_goals[i])
            i += 1

            response = get(url='http://10.10.0.1:5000/status')
            time_1s = time.time()
            while response.text == 'Running':
                if time_1s + 0.5 < time.time():
                    response = get(url='http://10.10.0.1:5000/status')
                    time_1s = time.time()

            if response.text == 'Preempted':
                i -= 1
                time.sleep(10)

            while playing:
                post(url='http://10.10.0.1:5000/cancel')
                time.sleep(1)

def main_global(reachy, posenet=True, tictactoe=True, navigation=True):
    global playing

    if navigation:
        print("launch navigation")
        thread = threading.Thread(target=navigation_function, daemon=True)
        thread.start()
    if tictactoe:
        print("launch tictactoe")

        while config.running:
            reachy.turn_on('head')
            print("head ON")

            reachy.head.l_antenna.goal_position = -140.0
            reachy.head.r_antenna.goal_position = 140.0
            time.sleep(1)
            reachy.head.look_at(1, 0.0, 0.0, 1)
            reachy.head.l_antenna.goal_position = 140.0
            reachy.head.r_antenna.goal_position = -140.0
            playsound('/home/reachy/reachy_mobile_reachy/sounds/sonBB8_content.mp3')

            print("waiting for a player")
            if posenet:
                output = simple_pose.main(reachy, navigation)

            print("Playing Reachy Tic Tac Toe")
            playing = True
            winner = game_launcher.main(reachy, '/home/reachy/reachy_mobile_reachy/gamelog')
            print("quitting...")
            print("waiting for 10 seconds")
            time.sleep(10)

            reachy.turn_off_smoothly('r_arm')
            playing = False



if __name__ == '__main__':
    reachy = ReachySDK(host='localhost')
    config.running = True
    main_global(reachy)
