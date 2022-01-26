"""
Define the TicTacToePlayground class.
"""
import logging
import os
import time
from threading import Thread, Event

import numpy as np
from cv2 import cv2 as cv
from reachy_sdk.trajectory import goto
from reachy_sdk.trajectory.interpolation import InterpolationMode

if __package__ is None or __package__ == '':
    from utils import piece2id, id2piece, piece2player
    from rl_agent import value_actions
    import behavior
else:
    from tictactoe.reachy_tictactoe.vision import get_board_configuration
    from tictactoe.reachy_tictactoe.utils import piece2id, id2piece, piece2player
    from tictactoe.reachy_tictactoe.rl_agent import value_actions
    from tictactoe.reachy_tictactoe import behavior

logger = logging.getLogger('reachy.tictactoe')


# noinspection PyTypeChecker
class TictactoePlayground(object):
    def __init__(self, reachy):
        self._idle_t = None
        self._idle_running = None
        logger.info('Creating the playground')

        self.reachy = reachy

        self.pawn_played = 0

    def setup(self):
        self.reachy.turn_on('head')
        self.reachy.turn_on('r_arm')
        self.reachy.head.l_antenna.speed_limit = 50.0
        self.reachy.head.r_antenna.speed_limit = 50.0

        self.reachy.head.l_antenna.goal_position = 0
        self.reachy.head.r_antenna.goal_position = 0
        time.sleep(1)
        self.reachy.head.look_at(0.95, -0.9, -0.7, 1.0)
        time.sleep(1)
        self.goto_rest_position()
        time.sleep(1)
        # self.reachy.head.look_at(0.95, -0.5, -0.2, 1.0)
        logger.info('Setup the playground')
        self.reachy.head.look_at(x=1, y=0, z=-0.8, duration=1)
        time.sleep(1)
        self.reachy.turn_off('head')

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        logger.info(
            'Closing the playground',
            extra={
                'exc': exc,
            }
        )

    def reset(self):
        logger.info('Resetting the playground')

        self.pawn_played = 0
        empty_board = np.zeros((3, 3), dtype=np.uint8).flatten()

        return empty_board

    @staticmethod
    def is_ready(board):
        return np.sum(board) == 0

    def random_look(self):
        dy = 0.4
        y = np.random.rand() * dy - (dy / 2)
        dz = 0.75
        z = np.random.rand() * dz - 0.5
        self.reachy.head.look_at(0.5, y, z, duration=1.5)

    @staticmethod
    def run_random_idle_behavior():
        logger.info('Reachy is playing a random idle behavior')
        time.sleep(2)

    @staticmethod
    def coin_flip():
        coin = np.random.rand() > 0.5
        logger.info(
            'Coin flip',
            extra={
                'first player': 'reachy' if coin else 'human',
            },
        )
        return coin

    def analyze_board(self):
        # time.sleep(6)
        time.sleep(2)
        print("Waiting for image")
        img = self.reachy.right_camera.wait_for_new_frame()
        print("Receiving new frame")
        # time.sleep(3)
        time.sleep(1)
        i = np.random.randint(1000)
        path = f'/home/reachy/reachy_mobile_reachy/tictactoe/images/{i}.jpg'
        cv.imwrite(path, img)
        logger.info(
            'Getting an image from camera',
        )
        ok, board, _ = get_board_configuration(img)
        logger.info(
            'Board analyzed',
            extra={
                'board': board,
                'img_path': path,
            },
        )
        self.reachy.turn_on('head')
        return ok, board

    @staticmethod
    def incoherent_board_detected(board):
        nb_cubes = len(np.where(board == piece2id['cube'])[0])
        nb_cylinders = len(np.where(board == piece2id['cylinder'])[0])

        if abs(nb_cubes - nb_cylinders) <= 1:
            return False
        else:
            logger.warning('Incoherent board detected', extra={
                'current_board': board})
            return True

    @staticmethod
    def cheating_detected(board, last_board, reachy_turn):
        # last is just after the robot played
        logger.info(f'last board = {last_board}')
        logger.info(f'current board = {board}')
        delta = board - last_board
        # Nothing changed
        if np.all(delta == 0):
            return False
        # A single cube was added
        if len(np.where(delta == piece2id['cube'])[0]) == 1:
            return False
        # A single cylinder was added
        if len(np.where(delta == piece2id['cylinder'])[0]) == 1:
            # If the human added a cylinder
            if not reachy_turn:
                return True
            return False

        logger.warning('Cheating detected', extra={
            'last_board': last_board,
            'current_board': board,
        })

        return True

    def shuffle_board(self):
        def ears_no():
            d = 3
            f = 2
            time.sleep(2.5)
            t = np.linspace(0, d, d * 100)
            p = 25 + 25 * np.sin(2 * np.pi * f * t)
            for pp in p:
                self.reachy.head.l_antenna.goal_position = pp
                time.sleep(0.01)

        t = Thread(target=ears_no)
        t.start()

        self.reachy.turn_on('r_arm')
        self.reachy.turn_on('head')
        self.reachy.head.l_antenna.speed_limit = 70.0
        self.reachy.head.r_antenna.speed_limit = 70.0
        self.goto_base_position()
        self.reachy.turn_on('r_arm')
        self.reachy.turn_on('head')
        self.reachy.head.look_at(0.5, 0, -0.4, duration=1)
        path = '/home/reachy/dev/reachy-tictactoe_2021/reachy_tictactoe/moves-2021_nemo/shuffle-board.npz'
        self.trajectoryPlayer(path)
        self.goto_rest_position()
        self.reachy.head.look_at(1, 0, 0, duration=1)
        t.join()

    @staticmethod
    def choose_next_action(board):
        actions = value_actions(board)
        # If empty board starts with a random actions for diversity
        best_action = actions
        logger.info(
            'Selecting Reachy next action',
            extra={
                'board': board,
                'actions': actions,
                'selected action': best_action,
            },
        )
        return best_action, None

    def play(self, action, actual_board):
        board = actual_board.copy()
        self.play_pawn(
            grab_index=self.pawn_played + 1,
            box_index=action + 1,
        )
        self.pawn_played += 1
        board[action] = piece2id['cylinder']
        logger.info(
            'Reachy playing pawn',
            extra={
                'board-before': actual_board,
                'board-after': board,
                'action': action + 1,
                'pawn_played': self.pawn_played + 1,
            },
        )
        return board

    def play_pawn(self, grab_index, box_index):
        self.reachy.r_arm.r_gripper.speed_limit = 80
        self.reachy.r_arm.r_gripper.compliant = False
        self.reachy.turn_on('head')
        self.reachy.turn_on('r_arm')
        logger.info(f'BOX_INDEX = {box_index}')
        # Goto base position
        self.reachy.head.look_at(0.95, 0, 0, 1.0)

        time.sleep(1)
        self.reachy.head.look_at(0.95, -0.9, -0.7, 1.0)
        self.goto_base_position()
        self.reachy.r_arm.r_gripper.goal_position = -40  # open the gripper
        path = f'/home/reachy/dev/reachy-tictactoe_2021/reachy_tictactoe/moves-2021_nemo/grab_{grab_index}.npz'
        self.goto_position(path)
        time.sleep(2)
        self.reachy.r_arm.r_gripper.compliant = False
        self.reachy.r_arm.r_gripper.goal_position = -5  # close the gripper to take the cylinder
        time.sleep(2)
        self.reachy.head.l_antenna.goal_position = 45
        self.reachy.head.r_antenna.goal_position = -45
        self.reachy.head.look_at(0.95, 0, -0.7, 1.0)
        self.reachy.turn_off('head')
        if grab_index >= 4:
            goto(
                goal_positions={
                    self.reachy.r_arm.r_shoulder_pitch: self.reachy.r_arm.r_shoulder_pitch.goal_position + 10,
                    self.reachy.r_arm.r_elbow_pitch: self.reachy.r_arm.r_elbow_pitch.goal_position + 10,
                },
                duration=1.0,
                interpolation_mode=InterpolationMode.MINIMUM_JERK
            )
        path = '/home/reachy/dev/reachy-tictactoe_2021/reachy_tictactoe/moves-2021_nemo/lift.npz'
        self.goto_position(path)
        time.sleep(0.1)
        # Put it in box_index
        path = f'/home/reachy/dev/reachy-tictactoe_2021/reachy_tictactoe/moves-2021_nemo/put_{box_index}.npz'
        self.trajectoryPlayer(path)
        time.sleep(1)
        self.reachy.r_arm.r_gripper.compliant = False
        self.reachy.r_arm.r_gripper.goal_position = -40
        time.sleep(2)
        # Go back to rest position
        path = f'/home/reachy/dev/reachy-tictactoe_2021/reachy_tictactoe/moves-2021_nemo/back_{box_index}_upright.npz'
        self.goto_position(path)
        self.reachy.head.l_antenna.goal_position = 0
        self.reachy.head.r_antenna.goal_position = 0
        if box_index in (8, 9):
            path = '/home/reachy/dev/reachy-tictactoe_2021/reachy_tictactoe/moves-2021_nemo/back_to_back.npz'
            self.goto_position(path)
        path = '/home/reachy/dev/reachy-tictactoe_2021/reachy_tictactoe/moves-2021_nemo/back_rest.npz'
        self.goto_position(path)
        self.goto_base_position()
        # self.goto_rest_position()

    def is_final(self, board):
        winner = self.get_winner(board)
        if winner in ('robot', 'human'):
            return True
        else:
            return 0 not in board

    @staticmethod
    def has_human_played(current_board, last_board):
        cube = piece2id['cube']

        return (
                np.any(current_board != last_board) and
                np.sum(current_board == cube) > np.sum(last_board == cube)
        )

    @staticmethod
    def get_winner(board):
        win_configurations = (
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),

            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),

            (0, 4, 8),
            (2, 4, 6),
        )

        for c in win_configurations:
            trio = set(board[i] for i in c)
            for identifier in id2piece.keys():
                if trio == {identifier}:
                    winner = piece2player[id2piece[identifier]]
                    if winner in ('robot', 'human'):
                        return winner

        return 'nobody'

    @staticmethod
    def is_end(board):
        if np.sum(board == 0) == 0:
            return True
        else:
            return False

    def run_celebration(self):
        logger.info('Reachy is playing its win behavior')
        self.reachy.turn_on('head')
        self.reachy.head.look_at(x=1, y=0, z=-0.0, duration=1)
        time.sleep(1)
        behavior.happy(self.reachy)

    def run_draw_behavior(self):
        self.reachy.turn_on('head')
        logger.info('Reachy is playing its draw behavior')
        behavior.surprise(self.reachy)

    def run_defeat_behavior(self):
        self.reachy.turn_on('head')
        logger.info('Reachy is playing its defeat behavior')
        behavior.sad(self.reachy)

    def run_my_turn(self):
        self.goto_base_position()
        self.reachy.turn_on('r_arm')
        self.reachy.turn_on('head')
        self.reachy.head.look_at(x=1, y=0, z=-0.0, duration=1)
        logger.info('My turn')
        path = '/home/reachy/dev/reachy-tictactoe_2021/reachy_tictactoe/moves-2021_nemo/my-turn.npz'
        self.trajectoryPlayer(path)
        logger.info('My turn')
        self.goto_rest_position()
        self.reachy.head.look_at(x=1, y=0, z=-0.7, duration=0.7)
        self.reachy.turn_off('head')

    def run_your_turn(self):
        self.goto_base_position()
        self.reachy.turn_on('r_arm')
        self.reachy.turn_on('head')
        self.reachy.head.look_at(x=1, y=0, z=-0.0, duration=1)
        logger.info('Your turn')
        path = '/home/reachy/dev/reachy-tictactoe_2021/reachy_tictactoe/moves-2021_nemo/your-turn.npz'
        self.trajectoryPlayer(path)
        logger.info('Your  turn')
        self.goto_rest_position()
        self.reachy.head.look_at(x=1, y=0, z=-0.7, duration=0.7)
        self.reachy.turn_off('head')

    # Robot lower-level control functions
    def goto_position(self, path):

        self.reachy.turn_on('r_arm')
        move = np.load(path)
        move.allow_pickle = 1
        listMoves = move['move'].tolist()
        listTraj = {}
        for key, val in listMoves.items():
            # logger.info('self.' + key + '')
            listTraj[eval('self.' + key)] = float(val)

        goto(
            goal_positions=listTraj,
            duration=2.0,
            interpolation_mode=InterpolationMode.MINIMUM_JERK
        )

    def goto_base_position(self):
        self.reachy.turn_on('r_arm')
        time.sleep(0.1)
        goto(
            goal_positions={self.reachy.r_arm.r_shoulder_pitch: 60,
                            self.reachy.r_arm.r_shoulder_roll: -15,
                            self.reachy.r_arm.r_arm_yaw: 0,
                            self.reachy.r_arm.r_elbow_pitch: -95,
                            self.reachy.r_arm.r_forearm_yaw: -15,
                            self.reachy.r_arm.r_wrist_pitch: -50,
                            self.reachy.r_arm.r_wrist_roll: 0},
            duration=1.0,
            interpolation_mode=InterpolationMode.MINIMUM_JERK
        )
        time.sleep(0.1)
        self.reachy.r_arm.r_shoulder_pitch.torque_limit = 75
        self.reachy.r_arm.r_elbow_pitch.torque_limit = 75

    def goto_rest_position(self):
        time.sleep(0.1)
        self.goto_base_position()
        time.sleep(0.1)
        self.reachy.turn_on('r_arm')
        goto(
            goal_positions={self.reachy.r_arm.r_shoulder_pitch: 50,
                            self.reachy.r_arm.r_shoulder_roll: -15,
                            self.reachy.r_arm.r_arm_yaw: 0,
                            self.reachy.r_arm.r_elbow_pitch: -100,
                            self.reachy.r_arm.r_forearm_yaw: -15,
                            self.reachy.r_arm.r_wrist_pitch: -60,
                            self.reachy.r_arm.r_wrist_roll: 0},
            duration=1.0,
            interpolation_mode=InterpolationMode.MINIMUM_JERK
        )
        # time.sleep(1.25)
        self.reachy.r_arm.r_shoulder_roll.comliant = True
        self.reachy.r_arm.r_arm_yaw.comliant = True
        self.reachy.r_arm.r_elbow_pitch.comliant = True
        self.reachy.r_arm.r_forearm_yaw.comliant = True
        self.reachy.r_arm.r_wrist_pitch.comliant = True
        self.reachy.r_arm.r_wrist_roll.comliant = True
        self.reachy.r_arm.r_gripper.comliant = True
        self.reachy.turn_off_smoothly('r_arm')
        time.sleep(0.25)

    def trajectoryPlayer(self, path):
        self.reachy.turn_on('r_arm')
        move = np.load(path)
        move.allow_pickle = 1
        # logger.info(list(move.keys()))
        listMoves = move['move'].tolist()
        listTraj = [val for key, val in listMoves.items()]
        listTraj = np.array(listTraj).T.tolist()
        sampling_frequency = 100  # en hertz
        recorded_joints = []
        for joint, val in listMoves.items():
            if 'neck' in joint:
                fullName = 'self.' + joint
            elif 'r_' in joint:
                fullName = 'self.' + joint
            elif 'l_' in joint:
                fullName = 'self.' + joint
            recorded_joints.append(eval(fullName))
        for joint in recorded_joints:
            joint.compliant = False
        first_point = dict(zip(recorded_joints, listTraj[0]))
        goto(first_point, duration=3.0)
        for joints_positions in listTraj:
            for joint, pos in zip(recorded_joints, joints_positions):
                joint.goal_position = pos
            time.sleep(1 / sampling_frequency)

    def wait_for_img(self):
        start = time.time()
        while time.time() - start <= 30:
            img = self.reachy.right_camera.wait_for_new_frame()
            if img:
                return
        logger.warning('No image received for 30 sec, going to reboot.')
        os.system('sudo reboot')

    @staticmethod
    def need_cooldown():
        listNameJoints = [
            'r_shoulder_pitch',
            'r_shoulder_roll',
            'r_arm_yaw',
            'r_elbow_pitch',
            'r_forearm_yaw',
            'r_wrist_pitch',
            'r_wrist_roll',
            'r_gripper',
            'neck_disk_top',
            'neck_disk_middle',
            'neck_disk_bottom'
        ]
        listObj = []
        for joints in listNameJoints:
            if 'neck' in joints:
                fullName = 'self.reachy.head.' + joints + '.temperature'
            elif 'r_' in joints:
                fullName = 'self.reachy.r_arm.' + joints + '.temperature'
            listObj.append(fullName)

        temperatures = {key: temp for key, temp in zip(listNameJoints, listObj)}
        logger.info(
            'Checking Reachy motors temperature',
            extra={
                'temperatures': temperatures
            }
        )
        listMotor = []
        for key, obj in temperatures.items():
            try:
                if obj > 45:
                    listMotor.append(key)
            except TypeError:
                pass
        return listMotor

    def wait_for_cooldown(self):
        self.goto_rest_position()
        self.reachy.head.look_at(0.5, 0, -0.65, duration=1.25)
        self.reachy.turn_off('reachy')
        while True:
            listNameJoints = [
                'r_shoulder_pitch',
                'r_shoulder_roll',
                'r_arm_yaw',
                'r_elbow_pitch',
                'r_forearm_yaw',
                'r_wrist_pitch',
                'r_wrist_roll',
                'r_gripper',
                'neck_disk_top',
                'neck_disk_middle',
                'neck_disk_bottom'
            ]
            listObj = []
            for joints in listNameJoints:
                if 'neck' in joints:
                    fullName = 'self.reachy.head.' + joints + '.temperature'
                elif 'l_' in joints:
                    fullName = 'self.reachy.r_arm.' + joints + '.temperature'
                listObj.append(eval(fullName))
            temperatures = {key: temp for key, temp in zip(listNameJoints, listObj)}
            logger.warning(
                'Motors cooling down...',
                extra={
                    'temperatures': temperatures
                },
            )
            listMotor = []
            for key, obj in temperatures.items():
                if obj < 40:
                    listMotor.append(key)
            count = 0
            for key, obj in temperatures.items():
                if obj < 50:
                    count += 1
            if count == len(listNameJoints):
                break
            time.sleep(30)

    def enter_sleep_mode(self):
        self.reachy.head.look_at(0.5, 0, -0.65, duration=1.25)
        self.reachy.turn_off('head')
        self._idle_running = Event()
        self._idle_running.set()

        def _idle():
            f = 0.15
            amp = 30
            offset = 30
            while self._idle_running.is_set():
                p = offset + amp * np.sin(2 * np.pi * f * time.time())
                self.reachy.head.l_antenna.goal_position = p
                self.reachy.head.r_antenna.goal_position = -p
                time.sleep(0.01)

        self._idle_t = Thread(target=_idle)
        self._idle_t.start()

    def leave_sleep_mode(self):
        self.reachy.turn_on('head')
        time.sleep(0.1)
        self.reachy.head.look_at(1, 0, 0, duration=1)
        self._idle_running.clear()
        self._idle_t.join()
