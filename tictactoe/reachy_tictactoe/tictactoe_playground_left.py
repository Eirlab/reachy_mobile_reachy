import numpy as np
import logging
import time
import os


from threading import Thread, Event

from reachy_sdk import ReachySDK
#TC from reachy_sdk.arm import RightArm
#TC from reachy_sdk.head import Head
#TC from reachy_sdk.trajectory import TrajectoryPlayer
from reachy_sdk.trajectory import goto
from reachy_sdk.trajectory.interpolation import InterpolationMode

from .vision import get_board_configuration, is_board_valid
from .utils import piece2id, id2piece, piece2player
#TC from .moves import moves, rest_pos, base_pos
from .rl_agent import value_actions
from . import behavior


logger = logging.getLogger('reachy.tictactoe')


class TictactoePlayground(object):
    def __init__(self):
        logger.info('Creating the playground')

        self.reachy = ReachySDK('localhost')

        self.pawn_played = 0

    def setup(self):
        logger.info('Setup the playground')

        #TC for antenna in self.reachy.head.motors: 
        #    antenna.compliant = False
        #    antenna.goto(
        #        goal_position=0, duration=2,
        #        interpolation_mode='minjerk',
        #    )
        self.reachy.turn_on('head')
        self.reachy.head.look_at(x=1, y=0, z=0, duration=1.5) 
        self.reachy.head.l_antenna.speed_limit = 50.0
        self.reachy.head.r_antenna.speed_limit = 50.0
        self.reachy.head.l_antenna.goal_position = 0
        self.reachy.head.r_antenna.goal_position = 0
        self.goto_rest_position()
        

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        logger.info(
            'Closing the playground',
            extra={
                'exc': exc,
            }
        )
        #TC self.reachy.close()

    # Playground and game functions

    def reset(self):
        logger.info('Resetting the playground')

        self.pawn_played = 0
        empty_board = np.zeros((3, 3), dtype=np.uint8).flatten()

        return empty_board

    def is_ready(self, board):
        return np.sum(board) == 0

    def random_look(self):
        dy = 0.4
        y = np.random.rand() * dy - (dy / 2)

        dz = 0.75
        z = np.random.rand() * dz - 0.5

        self.reachy.head.look_at(0.5, y, z, duration=1.5)

    def run_random_idle_behavior(self):
        logger.info('Reachy is playing a random idle behavior')
        time.sleep(2)

    def coin_flip(self):
        coin = np.random.rand() > 0.5
        logger.info(
            'Coin flip',
            extra={
                'first player': 'reachy' if coin else 'human',
            },
        )
        return coin

    def analyze_board(self):
        #TC for disk in self.reachy.head.neck.disks:
        #    disk.compliant = False
        self.reachy.turn_on('head')
        time.sleep(0.1)

        self.reachy.head.look_at(x=1, y=0, z=0, duration=1.5) 
        #TC self.reachy.head.look_at(0.5, 0, z=-0.6, duration=1)
        self.reachy.head.look_at(x=0.8, y=0, z=-0.6, duration=1) 

        time.sleep(3)

        # Wait an image from the camera
        #TC self.wait_for_img()
        #TC success, img = self.reachy.head.right_camera.read() 
        img = self.reachy.right_camera.wait_for_new_frame()
        logger.info(
            'pouet'
        )
        # TEMP:
        import cv2 as cv
        i = np.random.randint(1000)
        path = f'/tmp/snap.{i}.jpg'
        cv.imwrite(path, img)

        logger.info(
            'Getting an image from camera',
            #TC extra={
            #    'img_path': path,
            #    'disks': [d.rot_position for d in self.reachy.head.neck.disks], #changer
            #},
        )

        #if not is_board_valid(img):
        #    logger.info('BOARD PAS VALIDE')
        #    self.reachy.head.compliant = False
        #    time.sleep(0.1)
        #    self.reachy.head.look_at(1, 0, 0, duration=0.75)
        #    return

        tic = time.time()
        
        #TC success, img = self.reachy.head.right_camera.read() 
        img = self.reachy.right_camera.wait_for_new_frame()
        ok, board, _ = get_board_configuration(img)

        # TEMP
        logger.info(
            'Board analyzed',
            extra={
                'board': board,
                'img_path': path,
            },
        )

        #TC self.reachy.head.compliant = False
        self.reachy.turn_on('head')
        time.sleep(0.1)
        self.reachy.head.look_at(1, 0, 0, duration=0.75)

        return ok, board

    def incoherent_board_detected(self, board):
        nb_cubes = len(np.where(board == piece2id['cube'])[0])
        nb_cylinders = len(np.where(board == piece2id['cylinder'])[0])

        if abs(nb_cubes - nb_cylinders) <= 1:
            return False
        else : 
            logger.warning('Incoherent board detected', extra={
            'current_board': board})
            return True


    def cheating_detected(self, board, last_board, reachy_turn):
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

        self.goto_base_position()
        self.reachy.head.look_at(0.5, 0, -0.4, duration=1)
        #TC TrajectoryPlayer(self.reachy, moves['shuffle-board']).play(wait=True)
        path = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left_left/shuffle-board.npz'
        self.trajectoryPlayer(path)
        self.goto_rest_position()
        self.reachy.head.look_at(1, 0, 0, duration=1)
        t.join()

    def choose_next_action(self, board):
        actions = value_actions(board)

        # If empty board starts with a random actions for diversity
        if np.all(board == 0):
            while True:
                i = np.random.randint(0, 9)
                a, _ = actions[i]
                if a != 8:
                    break

        elif np.sum(board) == piece2id['cube']:
            a, _ = actions[0]
            if a == 8:
                i = 1
            else:
                i = 0
        else:
            i = 0

        best_action, value = actions[i]

        logger.info(
            'Selecting Reachy next action',
            extra={
                'board': board,
                'actions': actions,
                'selected action': best_action,
            },
        )

        return best_action, value

    def play(self, action, actual_board):
        board = actual_board.copy()
        logger.info('JE PASSE DANS PLAY')

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
        self.reachy.head.look_at(
            0.3, 0.3, -0.3,
            duration=0.85,
        )

        self.reachy.l_arm.l_gripper.speed_limit = 60
        self.reachy.l_arm.l_gripper.compliant = False

        logger.info(f'BOX_INDEX = {box_index}')

        # Goto base position
        self.goto_base_position() 

        # if grab_index >= 4: #bizarre
        #     #TC self.goto_position(
        #     #    moves['grab_3'],
        #     #    duration=1,
        #     #    wait=True,
        #     #)
        #     logger.info('JE PASSE LA C BIZARRE')
        #     path = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left/grab_3.npz'
        #     self.goto_position(path)

        # Grab the pawn at grab_index
        
        #TC self.goto_position(
        #    moves[f'grab_{grab_index}'],
        #    duration=1,
        #    wait=True,
        #)

        logger.info('JE PASSE DANS PLAY_PAWN')
        self.reachy.l_arm.l_gripper.goal_position = 40 #open the gripper 
        path = f'/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left/grab_{grab_index}.npz'
        self.goto_position(path)
        time.sleep(2)
        self.reachy.l_arm.l_gripper.compliant = False 
        self.reachy.l_arm.l_gripper.goal_position = 5 #close the gripper to take the cylinder 
        time.sleep(2)
        #TC self.reachy.right_arm.hand.close() 

        #TC self.reachy.head.left_antenna.goto(45, 1, interpolation_mode='minjerk')
        self.reachy.head.l_antenna.goal_position = 45
        #TC self.reachy.head.right_antenna.goto(-45, 1, interpolation_mode='minjerk')
        self.reachy.head.r_antenna.goal_position = -45

        if grab_index >= 4:
            #TC self.reachy.goto({
                #TC 'right_arm.shoulder_pitch': self.reachy.right_arm.shoulder_pitch.goal_position + 10,
                #TC 'right_arm.elbow_pitch': self.reachy.right_arm.elbow_pitch.goal_position - 30,
            #}, duration=1,
            #   wait=True,
            #   interpolation_mode='minjerk',
            #   starting_point='goal_position',
            #)
            goto(
            goal_positions = {
            	self.reachy.l_arm.l_shoulder_pitch : self.reachy.l_arm.l_shoulder_pitch.goal_position+10, 
            	self.reachy.l_arm.l_elbow_pitch : self.reachy.l_arm.l_elbow_pitch.goal_position+10, 
            	},
            	duration =1.0,
            	interpolation_mode=InterpolationMode.MINIMUM_JERK
            )

        # Lift it
        #TC self.goto_position(
        #    moves['lift'],
        #    duration=1,
        #    wait=True,
        #)
        path = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left/lift.npz'
        self.goto_position(path)

        self.reachy.head.look_at(0.5, 0, -0.35, duration=0.5)
        time.sleep(0.1)

        # Put it in box_index

        #TC put = moves[f'put_{box_index}_smooth_10_kp']
        #j = {
        #    m: j
        #    for j, m in zip(
        #        np.array(list(put.values()))[:, 0],
        #        list(put.keys())
        #    )
        #}
        #self.goto_position(j, duration=0.5, wait=True)
        #TrajectoryPlayer(self.reachy, put).play(wait=True)
        path = f'/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left/put_{box_index}.npz'
        self.trajectoryPlayer(path)

        #TC self.reachy.right_arm.hand.open()
        self.reachy.l_arm.l_gripper.compliant = False
        self.reachy.l_arm.l_gripper.goal_position = 40
        time.sleep(2)

        # Go back to rest position
        #TC self.goto_position(
        #    moves[f'back_{box_index}_upright'],
        #    duration=1,
        #    wait=True,
        #)
        path = f'/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left/back_{box_index}_upright.npz'
        self.goto_position(path)

        #TC self.reachy.head.left_antenna.goto(0, 0.2, interpolation_mode='minjerk')
        self.reachy.head.l_antenna.goal_position = 0
        #TC self.reachy.head.right_antenna.goto(0, 0.2, interpolation_mode='minjerk')
        self.reachy.head.r_antenna.goal_position = 0

        self.reachy.head.look_at(1, 0, 0, duration=1)

        if box_index in (8, 9):
            #TC self.goto_position(
            #    moves['back_to_back'],
            #    duration=1,
            #    wait=True,
            #)
            path = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left/back_to_back.npz'
            self.goto_position(path)

        #TC self.goto_position(
        #    moves['back_rest'],
        #    duration=2,
        #    wait=True,
        #)
        path = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left/back_rest.npz'
        self.goto_position(path)

        self.goto_rest_position()

    def is_final(self, board):
        winner = self.get_winner(board)
        if winner in ('robot', 'human'):
            return True
        else:
            return 0 not in board

    def has_human_played(self, current_board, last_board):
        cube = piece2id['cube']

        return (
            np.any(current_board != last_board) and
            np.sum(current_board == cube) > np.sum(last_board == cube)
        )

    def get_winner(self, board):
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
            for id in id2piece.keys():
                if trio == set([id]):
                    winner = piece2player[id2piece[id]]
                    if winner in ('robot', 'human'):
                        return winner

        return 'nobody'

    def run_celebration(self):
        logger.info('Reachy is playing its win behavior')
        behavior.happy(self.reachy)

    def run_draw_behavior(self):
        logger.info('Reachy is playing its draw behavior')
        behavior.surprise(self.reachy)

    def run_defeat_behavior(self):
        logger.info('Reachy is playing its defeat behavior')
        behavior.sad(self.reachy)

    def run_my_turn(self):
        self.goto_base_position()
        #TC TrajectoryPlayer(self.reachy, moves['my-turn']).play(wait=True) 
        logger.info('OOOOO my turn')
        path = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left/my-turn.npz'
        self.trajectoryPlayer(path)
        logger.info('OOOOOOOOOOOOOOOOO my turn')
        self.goto_rest_position()

    def run_your_turn(self):
        self.goto_base_position()
        logger.info('OOOOOOOO your turn')
        #TC TrajectoryPlayer(self.reachy, moves['your-turn']).play(wait=True) 
        path = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/moves-2021_left/your-turn.npz'
        self.trajectoryPlayer(path)
        logger.info('OOOOOOOOOOOOOOOOO your  turn')
        self.goto_rest_position()

    # Robot lower-level control functions

    #def goto_position(self, goal_positions, duration, wait):
    #    self.reachy.goto(
    #        goal_positions=goal_positions,
    #        duration=duration,
    #        wait=wait,
    #        interpolation_mode='minjerk',
    #        starting_point='goal_position',
    #    )

    def goto_position(self, path): 

        self.reachy.turn_on('l_arm')
        move = np.load(path)
        move.allow_pickle=1
        listMoves = move['move'].tolist()
        logger.info('JE PASSE DANS GOTO')
        listTraj = {}
        #listTraj = { eval('self.'+key):float(val) for key,val in listMoves.items() }
        for key,val in listMoves.items():
            logger.info('self.'+key + '')
            listTraj[eval('self.'+key)] = float(val)

        logger.info('JE PASSE DANS GOTO')
    
        goto(
            goal_positions=listTraj, 
            duration=2.0,
            interpolation_mode=InterpolationMode.MINIMUM_JERK
        )

    def goto_base_position(self, duration=2.0):
        #TC for m in self.reachy.right_arm.motors:
            #TC m.compliant = False
        self.reachy.turn_on('l_arm')

        time.sleep(0.1)

        #TC self.reachy.right_arm.shoulder_pitch.torque_limit = 75
        self.reachy.l_arm.l_shoulder_pitch.torque_limit = 75
        #TC self.reachy.right_arm.elbow_pitch.torque_limit = 75
        self.reachy.l_arm.l_elbow_pitch.torque_limit = 75
        time.sleep(0.1)

        #TC self.goto_position(base_pos, duration, wait=True) 
        goto(
            goal_positions=
                    {self.reachy.l_arm.l_shoulder_pitch: 60,
                    self.reachy.l_arm.l_shoulder_roll: -15,
                    self.reachy.l_arm.l_arm_yaw: 0,
                    self.reachy.l_arm.l_elbow_pitch: -95,
                    self.reachy.l_arm.l_forearm_yaw: -15,
                    self.reachy.l_arm.l_wrist_pitch: -50,
                    self.reachy.l_arm.l_wrist_roll: 0},
                duration=1.0,
                interpolation_mode=InterpolationMode.MINIMUM_JERK
            )

    def goto_rest_position(self, duration=2.0):
        # FIXME: Why is it needed?
        time.sleep(0.1)

        self.goto_base_position(0.6 * duration)
        time.sleep(0.1)

        self.reachy.turn_on('l_arm')
        #TC self.goto_position(rest_pos, 0.4 * duration, wait=True)

        goto(
            goal_positions=
                    {self.reachy.l_arm.l_shoulder_pitch: 50,
                    self.reachy.l_arm.l_shoulder_roll: -15,
                    self.reachy.l_arm.l_arm_yaw: 0,
                    self.reachy.l_arm.l_elbow_pitch: -100,
                    self.reachy.l_arm.l_forearm_yaw: -15,
                    self.reachy.l_arm.l_wrist_pitch: -60,
                    self.reachy.l_arm.l_wrist_roll: 0},
                duration=1.0,
                interpolation_mode=InterpolationMode.MINIMUM_JERK
            )
        time.sleep(1)
        logger.info('je passe la')
        #TC self.reachy.right_arm.shoulder_pitch.torque_limit = 0
        #TC self.reachy.right_arm.elbow_pitch.torque_limit = 0

        time.sleep(0.25)

        #TC for m in self.reachy.right_arm.motors:
            #if m.name != 'right_arm.shoulder_pitch':
                #m.compliant = True
        self.reachy.l_arm.l_shoulder_roll.comliant = True
        self.reachy.l_arm.l_arm_yaw.comliant = True
        self.reachy.l_arm.l_elbow_pitch.comliant = True
        self.reachy.l_arm.l_forearm_yaw.comliant = True
        self.reachy.l_arm.l_wrist_pitch.comliant = True
        self.reachy.l_arm.l_wrist_roll.comliant = True
        self.reachy.l_arm.l_gripper.comliant = True

        time.sleep(0.25)
    
    def trajectoryPlayer(self , path):
        self.reachy.turn_on('l_arm')
        move = np.load(path)
        move.allow_pickle=1
        logger.info(list(move.keys()))

        listMoves = move['move'].tolist()
        listTraj = [ val for key,val in listMoves.items()]
        listTraj = np.array(listTraj).T.tolist()

        sampling_frequency = 100  #en hertz

        recorded_joints = [
            self.reachy.l_arm.l_shoulder_pitch,
            self.reachy.l_arm.l_shoulder_roll,
            self.reachy.l_arm.l_arm_yaw,
            self.reachy.l_arm.l_elbow_pitch,
            self.reachy.l_arm.l_forearm_yaw,
            self.reachy.l_arm.l_wrist_pitch,
            self.reachy.l_arm.l_wrist_roll,
            self.reachy.l_arm.l_gripper, 
        ]

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
            #TC success, img = self.reachy.head.right_camera.read()
            img = self.reachy.right_camera.wait_for_new_frame()
            if img != []:
                return
        logger.warning('No image received for 30 sec, going to reboot.')
        os.system('sudo reboot')

    def need_cooldown(self):
        listNameJoints = [
                'l_shoulder_pitch',
                'l_shoulder_roll',
                'l_arm_yaw',
                'l_elbow_pitch',
                'l_forearm_yaw',
                'l_wrist_pitch',
                'l_wrist_roll',
                'l_gripper',
                'neck_disk_top', 
                'neck_disk_middle', 
                'neck_disk_bottom'
            ]
        listObj = []
        for joints in listNameJoints:
            if 'neck' in joints : 
                fullName = 'self.reachy.head.'+joints+'.temperature'
            elif 'l_' in joints: 
                fullName = 'self.reachy.l_arm.'+joints+'.temperature'
            listObj.append(fullName)

        temperatures = {key:eval(obj) for key,obj in zip(listNameJoints,listObj)}

        logger.info(
            'Checking Reachy motors temperature',
            extra={
                'temperatures': temperatures
            }
        )
        #TC return np.any(motor_temperature > 50) or np.any(orbita_temperature > 45)
        listMotor=[]
        for key,obj in temperatures.items() : 
            if obj > 45 : 
                listMotor.append(key)
        return listMotor 

    def wait_for_cooldown(self):
        self.goto_rest_position()
        self.reachy.head.look_at(0.5, 0, -0.65, duration=1.25)
        #TC self.reachy.head.compliant = True
        self.reachy.turn_off('reachy')

        while True:
            #TC motor_temperature = np.array([
            #    m.temperature for m in self.reachy.motors
            #])
            #orbita_temperature = np.array([
            #    d.temperature for d in self.reachy.head.neck.disks
            #])

            #temperatures = {}
            #temperatures.update({m.name: m.temperature for m in self.reachy.motors})
            #temperatures.update({d.name: d.temperature for d in self.reachy.head.neck.disks})
            listNameJoints = [
                'l_shoulder_pitch',
                'l_shoulder_roll',
                'l_arm_yaw',
                'l_elbow_pitch',
                'l_forearm_yaw',
                'l_wrist_pitch',
                'l_wrist_roll',
                'l_gripper',
                'neck_disk_top', 
                'neck_disk_middle', 
                'neck_disk_bottom'
            ]
            listObj = []
            for joints in listNameJoints:
                if 'neck' in joints : 
                    fullName = 'self.reachy.head.'+joints+'.temperature'
                elif 'l_' in joints: 
                    fullName = 'self.reachy.l_arm.'+joints+'.temperature'
                listObj.append(fullName)

            temperatures = {key:eval(obj) for key,obj in zip(listNameJoints,listObj)}

            logger.warning(
                'Motors cooling down...',
                extra={
                    'temperatures': temperatures
                },
            )

            #TC if np.all(motor_temperature < 45) and np.all(orbita_temperature < 40):
            listMotor=[]
            for key,obj in temperatures.items() : 
                if obj < 40 : 
                    listMotor.append(key)
            # if np.all(motor_temperature[1].astype(float) < 40): 
            #     break
            count = 0
            for key,obj in temperatures.items() : 
                if obj < 50 :
                        count = count+1
            if count == len(listNameJoints):
                break

            time.sleep(30)

    def enter_sleep_mode(self):
        self.reachy.head.look_at(0.5, 0, -0.65, duration=1.25)
        #TC self.reachy.head.compliant = True
        self.reachy.turn_off('head')

        self._idle_running = Event()
        self._idle_running.set()

        def _idle():
            f = 0.15
            amp = 30
            offset = 30

            while self._idle_running.is_set():
                p = offset + amp * np.sin(2 * np.pi * f * time.time())
                #TC self.reachy.head.left_antenna.goal_position = p
                self.reachy.head.l_antenna.goal_position = p
                #TC self.reachy.head.right_antenna.goal_position = -p
                self.reachy.head.r_antenna.goal_position = -p
                time.sleep(0.01)

        self._idle_t = Thread(target=_idle)
        self._idle_t.start()

    def leave_sleep_mode(self):
        #TC self.reachy.head.compliant = False
        self.reachy.turn_on('head')
        time.sleep(0.1)
        self.reachy.head.look_at(1, 0, 0, duration=1)

        self._idle_running.clear()
        self._idle_t.join()
