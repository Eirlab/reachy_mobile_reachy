"""
This file implements point endpoints to add/ delete and get a cartesian point from compliant mode or rviz
"""
import threading

from flask import Blueprint, request, send_file
from werkzeug.exceptions import NotFound
import reachy
from reachy_sdk import ReachySDK

class ReachyAPI:

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

    def index(self):
        return "Reachy API"

    def play(self):
        if request.method == 'POST':
            # thread = threading.Thread(target=reachy.main())
            # thread.start()
            winner = reachy.main()
            return winner, 200

    def head_on(self):
        if request.method == 'POST':
            self.reachy.turn_on('head')
            return 200

    def head_off(self):
        if request.method == 'POST':
            self.reachy.turn_off('head')
        return 200

    def head_lookat(self):
        if request.method == 'POST':
            data = request.get_json()
            x = data['x']
            y = data['y']
            z = data['z']
            duration = data['duration']
            self.reachy.head.look_at(x, y, z, duration)
            return 200

    def head_happy(self):
        if request.method == 'POST':
            reachy.happy_antennas(self.reachy)
            return 200

    def head_sad(self):
        if request.method == 'POST':
            reachy.sad_antennas(self.reachy)
            return 200

    def camera_left(self):
        if request.method == 'GET':
            image = self.reachy.left_camera.wait_for_new_frame()
            return send_file(image, mimetype='image/jpeg')
        return "Reachy API"

    def camera_right(self):
        if request.method == 'GET':
            image = self.reachy.right_camera.wait_for_new_frame()
            return send_file(image, mimetype='image/jpeg')
        return "Reachy API"

