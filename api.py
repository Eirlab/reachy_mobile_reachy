"""
This file implements endpoints for Reachy API allowing to control rechy mobile robot
"""
from flask import Blueprint, request, send_file
from reachy_sdk import ReachySDK

import reachy


class ReachyAPI:
    """
    This class implements endpoints for Reachy API allowing to control rechy mobile robot
    """
    def __init__(self):
        self.bp = Blueprint('reachy_api', __name__)

        self.bp.route('/', methods=['GET'])(self.index)
        self.bp.route('/play', methods=['POST'])(self.play)
        self.bp.route('/head/on', methods=['POST'])(self.head_on)
        self.bp.route('/head/off', methods=['POST'])(self.head_off)
        self.bp.route('/head/lookat', methods=['POST'])(self.head_lookat)
        self.bp.route('/head/happy', methods=['POST'])(self.head_happy)
        self.bp.route('/head/sad', methods=['POST'])(self.head_sad)
        self.bp.route('/camera/left', methods=['GET'])(self.camera_left)
        self.bp.route('/camera/right', methods=['GET'])(self.camera_right)

        self.reachy = ReachySDK(host='localhost')

    @staticmethod
    def index():
        """
        METHOD : GET
        ROUTE : /
        BRIEF : Home  page for reachy API
        TODO : improve home page
        :return: {'status': "Success"}
        """
        return {'status': "Success"}, 200

    def play(self):
        """
        METHOD : POST
        ROUTE : /play
        PARAMETERS : {}
        BRIEF : Play a tictactoe game (blocking function)
        :return: {'status': "Success", 'data' : 'winner'} at the end of the game
        """
        if request.method == 'POST':
            winner = reachy.main(self.reachy)
            return {'status': "Success", 'data': winner}, 200

    def head_on(self):
        """
        METHOD : POST
        ROUTE : /head/on
        PARAMETERS : {}
        BRIEF : Power on the head
        :return: {'status': "Success"}
        """
        if request.method == 'POST':
            self.reachy.turn_on('head')
            return {'status': "Success"}, 200

    def head_off(self):
        """
        METHOD : POST
        ROUTE : /head/off
        PARAMETERS : {}
        BRIEF : Power off the head
        :return: {'status': "Success"}
        """
        if request.method == 'POST':
            self.reachy.turn_off('head')
        return {'status': "Success"}, 200

    def head_lookat(self):
        """
        METHOD : POST
        ROUTE : /head/lookat
        PARAMETERS : {'x': float, 'y': float, 'z': float, 'duration': float}
        BRIEF : Look at a point in space with the head (blocking function)
        :return: {'status': "Success"} at the end of the action
        """
        if request.method == 'POST':
            data = request.get_json()
            x = float(data['x'])
            y = float(data['y'])
            z = float(data['z'])
            duration = float(data['duration'])
            self.reachy.head.look_at(x=x, y=y, z=z, duration=duration)
            return {'status': "Success"}, 200

    def head_happy(self):
        """
        METHOD : POST
        ROUTE : /head/happy
        PARAMETERS : {}
        BRIEF : Make the robot happy
        :return: {'status': "Success"}
        """
        if request.method == 'POST':
            reachy.happy_antennas(self.reachy)
            return {'status': "Success"}, 200

    def head_sad(self):
        """
        METHOD : POST
        ROUTE : /head/sad
        PARAMETERS : {}
        BRIEF : Make the robot sad
        :return: {'status': "Success"}
        """
        if request.method == 'POST':
            reachy.sad_antennas(self.reachy)
            return {'status': "Success"}, 200

    def camera_left(self):
        """
        METHOD : GET
        ROUTE : /camera/left
        Take a picture from the left camera
        :return: a flask response with the image
        """
        if request.method == 'GET':
            image = self.reachy.left_camera.wait_for_new_frame()
            image.save('left.jpg')
            return send_file('left.jpg', mimetype='image/jpeg')
        return "Reachy API"

    def camera_right(self):
        """
        METHOD : GET
        ROUTE : /camera/right
        Take a picture from the right camera
        :return: a flask response with the image
        """
        if request.method == 'GET':
            image = self.reachy.right_camera.wait_for_new_frame()
            image.save('right.jpg')
            return send_file('right.jpg', mimetype='image/jpeg')
        return "Reachy API"
