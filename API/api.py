"""
This file implements endpoints for Reachy API allowing to control rechy mobile robot
"""
import sys
import time

from PIL import Image
from flask import Blueprint, request, render_template
from reachy_sdk import ReachySDK
from requests import post, get

sys.path.insert(0, "../")

import reachy


class ReachyAPI:
    """
    This class implements endpoints for Reachy API allowing to control rechy mobile robot
    """

    def __init__(self):
        self.bp = Blueprint('reachy_api', __name__)
        self.bp.app_errorhandler(404)(self.error_404)
        self.bp.app_errorhandler(500)(self.error_500)

        self.bp.route('/', methods=['GET'])(self.index)
        self.bp.route('/404', methods=['GET'])(self.error_404)
        self.bp.route('/500', methods=['GET'])(self.error_500)

        self.bp.route('/reachy', methods=['GET'])(self.reachy)
        self.bp.route('/reachy/play', methods=['POST'])(self.play)
        self.bp.route('/reachy/head/on', methods=['POST'])(self.head_on)
        self.bp.route('/reachy/head/off', methods=['POST'])(self.head_off)
        self.bp.route('/reachy/head/lookat', methods=['POST'])(self.head_lookat)
        self.bp.route('/reachy/head/happy', methods=['POST'])(self.head_happy)
        self.bp.route('/reachy/head/sad', methods=['POST'])(self.head_sad)
        self.bp.route('/reachy/camera/left', methods=['GET'])(self.camera_left)
        self.bp.route('/reachy/camera/right', methods=['GET'])(self.camera_right)
        self.bp.route('/reachy/camera/left/autofocus', methods=['POST'])(self.camera_left_autofocus)
        self.bp.route('/reachy/camera/right/autofocus', methods=['POST'])(self.camera_right_autofocus)

        self.bp.route('/ezwheel', methods=['GET'])(self.ezwheel)
        self.bp.route('/ezwheel/goal', methods=['POST'])(self.ezwheel_goal)
        self.bp.route('/ezwheel/cancel', methods=['POST'])(self.ezwheel_cancel)
        self.bp.route('/ezwheel/status', methods=['GET'])(self.ezwheel_status)

        self.reachy = ReachySDK(host='localhost')
        # self.reachy = "reachy"
        self.ezwheel_url = "http://10.10.0.1:5000/"

    @staticmethod
    def index():
        """
        METHOD : GET
        ROUTE : /
        BRIEF : Home  page for reachy API
        :return: {'status': "Success"}
        """
        return render_template(
            template_name_or_list='index.html')

    @staticmethod
    def error_404(e=None):
        """
        METHOD : GET
        ROUTE : /404
        BRIEF : Error page for reachy API
        """
        return render_template(template_name_or_list='404.html'), 404

    @staticmethod
    def error_500(e=None):
        """
        METHOD : GET
        ROUTE : /500
        BRIEF : Error page for reachy API
        """
        return render_template(template_name_or_list='500.html'), 500

    @staticmethod
    def reachy():
        """
        METHOD : GET
        ROUTE : /reachy
        BRIEF : Home  page for reachy API
        """
        return render_template(template_name_or_list='reachy.html')

    @staticmethod
    def ezwheel():
        """
        METHOD : GET
        ROUTE : /ezwheel
        BRIEF : Home  page for ezwheel API
        """
        return render_template(template_name_or_list='ezwheel.html', statut="Undefined")

    def play(self):
        """
        METHOD : POST
        ROUTE : /play
        PARAMETERS : {}
        BRIEF : Play a tictactoe game (blocking function)
        """
        if request.method == 'POST':
            posenet = bool(request.form.get('posenet'))
            tictactoe = bool(request.form.get('tictactoe'))
            navigation = bool(request.form.get('navigation'))
            winner = reachy.main(self.reachy, posenet, tictactoe, navigation)
            return render_template(template_name_or_list='index.html', win=winner)

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
            return render_template(template_name_or_list='reachy.html')

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
            return render_template(template_name_or_list='reachy.html')

    def head_lookat(self):
        """
        METHOD : POST
        ROUTE : /head/lookat
        PARAMETERS : {'x': float, 'y': float, 'z': float, 'duration': float}
        BRIEF : Look at a point in space with the head (blocking function)
        :return: {'status': "Success"} at the end of the action
        """
        if request.method == 'POST':
            self.reachy.turn_on('head')
            x = float(request.form.get('lookat_x'))
            y = float(request.form.get('lookat_y'))
            z = float(request.form.get('lookat_z'))
            duration = float(request.form.get('lookat_duration'))
            self.reachy.head.look_at(x=x, y=y, z=z, duration=duration)
            return render_template(template_name_or_list='reachy.html')

    def head_happy(self):
        """
        METHOD : POST
        ROUTE : /head/happy
        PARAMETERS : {}
        BRIEF : Make the robot happy
        :return: {'status': "Success"}
        """
        if request.method == 'POST':
            self.set_head_on()
            reachy.happy_antennas(self.reachy)
            return render_template(template_name_or_list='reachy.html')

    def head_sad(self):
        """
        METHOD : POST
        ROUTE : /head/sad
        PARAMETERS : {}
        BRIEF : Make the robot sad
        :return: {'status': "Success"}
        """
        if request.method == 'POST':
            self.set_head_on()
            reachy.sad_antennas(self.reachy)
            return render_template(template_name_or_list='reachy.html')

    def camera_left(self):
        """
        METHOD : GET
        ROUTE : /camera/left
        Take a picture from the left camera
        :return: a flask response with the image
        """
        if request.method == 'GET':
            image = self.reachy.left_camera.wait_for_new_frame()
            image = Image.fromarray(image)
            image.save('static/left.jpg')
            return render_template(template_name_or_list='reachy.html')

    def camera_left_autofocus(self):
        """
        METHOD : POST
        ROUTE : /camera/left/autofocus
        PARAMETERS : {}
        BRIEF : Autofocus the left camera
        :return: {'status': "Success"}
        """
        if request.method == 'POST':
            self.reachy.left_camera.start_autofocus()
            time.sleep(10.0)
            return render_template(template_name_or_list='reachy.html', autofocus_left="Autofocus done")

    def camera_right(self):
        """
        METHOD : GET
        ROUTE : /camera/right
        Take a picture from the right camera
        :return: a flask response with the image
        """
        if request.method == 'GET':
            image = self.reachy.right_camera.wait_for_new_frame()
            image = Image.fromarray(image)
            image.save('static/right.jpg')
            return render_template(template_name_or_list='reachy.html')

    def camera_right_autofocus(self):
        """
        METHOD : POST
        ROUTE : /camera/right/autofocus
        PARAMETERS : {}
        BRIEF : Autofocus the right camera
        :return: {'status': "Success"}
        """
        if request.method == 'POST':
            self.reachy.right_camera.start_autofocus()
            time.sleep(10.0)
            return render_template(template_name_or_list='reachy.html', autofocus_right="Autofocus done")

    def ezwheel_goal(self):
        """
        METHOD : POST
        ROUTE : /ezwheel/goal
        PARAMETERS : {'x': float, 'y': float, 'theta': float}
        BRIEF : Do a POST request on 10.10.0.1:5000/goal with data from
        :return:
        """
        if request.method == 'POST':
            x = request.form.get('goal_x')
            y = request.form.get('goal_y')
            theta = request.form.get('goal_theta')
            data = {'x': float(x), 'y': float(y), 'theta': float(theta)}
            post(url=self.ezwheel_url + '/goal', json=data)
            return render_template(template_name_or_list='ezwheel.html', statut="Running")

    def ezwheel_status(self):
        """
        METHOD : GET
        ROUTE : /ezwheel/status
        PARAMETERS : {}
        BRIEF : Do a GET request on 10.10.0.1:5000/status
        """
        if request.method == 'GET':
            response = get(url=self.ezwheel_url + 'status')
            print(response.text)
            return render_template(template_name_or_list='ezwheel.html', statut=response.text)

    def ezwheel_cancel(self):
        """
        METHOD : POST
        ROUTE : /ezwheel/cancel
        PARAMETERS : {}
        BRIEF : Do a POST request on 10.10.0.1:5000/cancel
        """
        if request.method == 'POST':
            get(url=self.ezwheel_url + 'cancel')
            return render_template(template_name_or_list='ezwheel.html', statut="Cancelled")

    def set_head_on(self):
        """
        Allow the robot to move the head
        """
        if self.reachy.head.joints.neck_disk_bottom.compliant and \
                self.reachy.head.joints.neck_disk_middle.compliant and \
                self.reachy.head.joints.neck_disk_middle.compliant:
            self.reachy.turn_on('head')
