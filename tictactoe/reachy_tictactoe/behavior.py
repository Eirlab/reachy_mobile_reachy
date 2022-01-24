import logging
import time
from threading import Event, Thread

import numpy as np

logger = logging.getLogger('reachy.tictactoe.behavior')


class FollowHand(object):
    def __init__(self, reachy):
        self.reachy = reachy
        self.running = Event()
        self.t = None

    def start(self):
        logger.info('Launching follow hand behavior')
        self.t = Thread(target=self.asserv)
        self.running.set()
        self.t.start()

    def stop(self):
        logger.info('Stopping follow hand behavior')
        self.running.clear()
        self.t.join()

    def asserv(self):
        while self.running.is_set():
            hand_pos = self.reachy.right_arm.forward_kinematics(
                [m.present_position for m in self.reachy.right_arm.motors]  # changer
            )[:3, 3]
            head_pos = np.array([0, 0, 0.09])
            v = np.array(hand_pos - head_pos)
            v += np.array([0.1, 0, 0.1])
            try:
                self.reachy.head.look_at(*v)
            except ValueError:
                pass
            time.sleep(0.01)


def head_home(reachy, duration):
    reachy.head.look_at(0.5, 0.0, 0, duration=duration)
    reachy.head.l_antenna.goal_position = 0
    reachy.head.r_antenna.goal_position = 0


def sad(reachy):
    logger.info('Starting behavior', extra={'behavior': 'sad'})
    pos = [(-0.5, 150), (-0.4, 110), (-0.5, 150), (-0.4, 110), (-0.5, 150), (0, 90), (0, 20), ]
    for (z, antenna_pos) in pos:
        reachy.head.look_at(0.5, 0.0, z, duration=1.0)
        reachy.head.l_antenna.goal_position = antenna_pos
        reachy.head.r_antenna.goal_position = -antenna_pos
    logger.info('Ending behavior', extra={'behavior': 'sad'})


def happy(reachy):
    logger.info('Starting behavior', extra={'behavior': 'happy'})
    reachy.head.l_antenna.speed_limit = 0.0
    reachy.head.r_antenna.speed_limit = 0.0
    for _ in range(9):
        reachy.head.l_antenna.goal_position = 10.0
        reachy.head.r_antenna.goal_position = -10.0
        time.sleep(0.1)
        reachy.head.l_antenna.goal_position = -10.0
        reachy.head.r_antenna.goal_position = 10.0
        time.sleep(0.1)
    reachy.head.l_antenna.goal_position = 0.0
    reachy.head.r_antenna.goal_position = 0.0
    time.sleep(1)
    head_home(reachy, duration=1)
    logger.info('Ending behavior', extra={'behavior': 'happy'})


def surprise(reachy):
    logger.info('Starting behavior', extra={'behavior': 'surprise'})
    reachy.head.look_at(5, 2, 0.5, duration=2)
    reachy.head.l_antenna.goal_position = -5
    reachy.head.r_antenna.goal_position = -90
    time.sleep(0.1)
    reachy.head.l_antenna.goal_position = 5
    reachy.head.r_antenna.goal_position = 90
    time.sleep(1)
    head_home(reachy, duration=1)
    logger.info('Ending behavior', extra={'behavior': 'surprise'})
