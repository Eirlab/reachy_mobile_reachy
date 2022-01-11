import time
import logging
import numpy as np

from threading import Event, Thread
from pyquaternion import Quaternion


logger = logging.getLogger('reachy.tictactoe.behavior')


class FollowHand(object):
    def __init__(self, reachy):
        self.reachy = reachy
        self.running = Event()

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
                [m.present_position for m in self.reachy.right_arm.motors]#changer 
            )[:3, 3]
            head_pos = np.array([0, 0, 0.09])

            v = np.array(hand_pos - head_pos)
            v = v + np.array([0.1, 0, 0.1])

            try:
                self.reachy.head.look_at(*v)
            except ValueError:
                pass

            time.sleep(0.01)

def head_home(reachy, duration):
    reachy.head.look_at(0.5, 0.0, 0, duration=duration)
    #TC reachy.goto({
    #    'head.l_antenna': 0,
    #    'head.r_antenna': 0,
    #}, duration=duration, wait=True, interpolation_mode='minjerk')
    reachy.head.l_antenna.goal_position = 0
    reachy.head.r_antenna.goal_position = 0


def sad(reachy):
    logger.info('Starting behavior', extra={'behavior': 'sad'})

    pos = [
        (-0.5, 150),
        (-0.4, 110),
        (-0.5, 150),
        (-0.4, 110),
        (-0.5, 150),
        (0, 90),
        (0, 20),
    ]

    for (z, antenna_pos) in pos:
        reachy.head.look_at(0.5, 0.0, z, duration=1.0)
        #TC reachy.goto({
        #    'head.left_antenna': antenna_pos,#changer
        #    'head.right_antenna': -antenna_pos,
        #}, duration=1.5, wait=True, interpolation_mode='minjerk')
        reachy.head.l_antenna.goal_position = antenna_pos
        reachy.head.r_antenna.goal_position = -antenna_pos
    logger.info('Ending behavior', extra={'behavior': 'sad'})


def happy(reachy):
    logger.info('Starting behavior', extra={'behavior': 'happy'})

    #TC q = Quaternion(axis=[1, 0, 0], angle=np.deg2rad(-15))
    # reachy.head.neck.orient(q, duration=1)

    #dur = 3
    #t = np.linspace(0, dur, dur * 100)
    #pos = 10 * np.sin(2 * np.pi * 5 * t)

    #for p in pos:
        #TC reachy.head.left_antenna.goal_position = p#changer
        #TC reachy.head.right_antenna.goal_position = -p
    #    reachy.head.l_antenna.goal_position = p
    #    reachy.head.r_antenna.goal_position = -p
    #    time.sleep(0.01)
    
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
    logger.info('Starting behavior', extra={'behavior': 'suprise'})

    #TC q = Quaternion(axis=[1, 0, 0], angle=np.deg2rad(22))
    #reachy.head.neck.orient(q, duration=1)
    reachy.head.look_at(5, 2, 0.5, duration=2)

    #TC reachy.goto({
    #    'head.left_antenna': -5,#changer
    #    'head.right_antenna': -90,
    #    }, duration=0.3, wait=True,
    #)
    reachy.head.l_antenna.goal_position = -5
    reachy.head.r_antenna.goal_position = -90
    time.sleep(0.1)
    reachy.head.l_antenna.goal_position = 5
    reachy.head.r_antenna.goal_position = 90

    time.sleep(1)
    head_home(reachy, duration=1)

    logger.info('Ending behavior', extra={'behavior': 'suprise'})
