# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import time
from io import BytesIO

import numpy as np
from cv2 import cv2

import cairosvg
import svgwrite
from PIL import ImageDraw
from playsound import playsound

from requests import post

if __package__ is None or __package__ == '':
    from pose_engine import PoseEngine

else:
    from .pose_engine import PoseEngine
    from .pose_engine import KeypointType
    from . import config

from PIL import Image

EDGES = (
    (KeypointType.NOSE, KeypointType.LEFT_EYE),
    (KeypointType.NOSE, KeypointType.RIGHT_EYE),
    (KeypointType.NOSE, KeypointType.LEFT_EAR),
    (KeypointType.NOSE, KeypointType.RIGHT_EAR),
    (KeypointType.LEFT_EAR, KeypointType.LEFT_EYE),
    (KeypointType.RIGHT_EAR, KeypointType.RIGHT_EYE),
    (KeypointType.LEFT_EYE, KeypointType.RIGHT_EYE),
    (KeypointType.LEFT_SHOULDER, KeypointType.RIGHT_SHOULDER),
    (KeypointType.LEFT_SHOULDER, KeypointType.LEFT_ELBOW),
    (KeypointType.LEFT_SHOULDER, KeypointType.LEFT_HIP),
    (KeypointType.RIGHT_SHOULDER, KeypointType.RIGHT_ELBOW),
    (KeypointType.RIGHT_SHOULDER, KeypointType.RIGHT_HIP),
    (KeypointType.LEFT_ELBOW, KeypointType.LEFT_WRIST),
    (KeypointType.RIGHT_ELBOW, KeypointType.RIGHT_WRIST),
    (KeypointType.LEFT_HIP, KeypointType.RIGHT_HIP),
    (KeypointType.LEFT_HIP, KeypointType.LEFT_KNEE),
    (KeypointType.RIGHT_HIP, KeypointType.RIGHT_KNEE),
    (KeypointType.LEFT_KNEE, KeypointType.LEFT_ANKLE),
    (KeypointType.RIGHT_KNEE, KeypointType.RIGHT_ANKLE),
)

def happy_antennas(reachy):
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

def draw_pose(dwg, pose, src_size, inference_box, color='yellow', threshold=0.2):
    box_x, box_y, box_w, box_h = inference_box
    scale_x, scale_y = src_size[0] / box_w, src_size[1] / box_h
    xys = {}
    for label, keypoint in pose.keypoints.items():
        if keypoint.score < threshold: continue
        # Offset and scale to source coordinate space.
        kp_x = int((keypoint.point[0] - box_x) * scale_x)
        kp_y = int((keypoint.point[1] - box_y) * scale_y)

        xys[label] = (kp_x, kp_y)
        dwg.add(dwg.circle(center=(int(kp_x), int(kp_y)), r=5,
                           fill='cyan', fill_opacity=keypoint.score, stroke=color))

    for a, b in EDGES:
        if a not in xys or b not in xys: continue
        ax, ay = xys[a]
        bx, by = xys[b]
        dwg.add(dwg.line(start=(ax, ay), end=(bx, by), stroke=color, stroke_width=2))


def main(reachy, navigation):
    counter_not_change = 0
    counter_img = 0     #images taken counter
    # reachy.head.l_antenna.speed_limit = 0.0
    # reachy.head.r_antenna.speed_limit = 0.0
    while True:
        counter_img += 1
        numpy_image = reachy.left_camera.wait_for_new_frame()
        pil_image = Image.fromarray(numpy_image, 'RGB')
        engine = PoseEngine(
            '/home/reachy/reachy_mobile_reachy/posenet/models/mobilenet/posenet_mobilenet_v1_075_481_641_quant_decoder_edgetpu.tflite')
        poses, inference_time = engine.DetectPosesInImage(pil_image)
        if counter_img == 50:  #save draw outputs every 50 images
            counter_img = 0
            svg_canvas = svgwrite.Drawing('', size=pil_image.size)
            for pose in poses:
                draw_pose(svg_canvas, pose, pil_image.size, (0, 0, 480, 640))
            out = BytesIO()
            cairosvg.svg2png(svg_canvas.tostring(), write_to=out)
            out = Image.open(out)
            photo_id = "_".join([time.strftime("%y-%m-%d_%H-%M-%S")])
            out.save(f'/home/reachy/reachy_mobile_reachy/posenet/images/{photo_id}.png')
        for i in range(len(poses)):
            pose = poses[i].keypoints
            shoulder_left = pose[KeypointType.LEFT_SHOULDER]
            wrist_left = pose[KeypointType.LEFT_WRIST]
            shoulder_right = pose[KeypointType.RIGHT_SHOULDER]
            wrist_right = pose[KeypointType.RIGHT_WRIST]
            difference_left = shoulder_left.point.y - wrist_left.point.y
            difference_right = shoulder_right.point.y - wrist_right.point.y
            if difference_left > 0 or difference_right > 0:
                counter_not_change = 0
                config.detection[i] = 1
                config.counter[i] += 1
                if config.counter[i] == 15:
                    if navigation:
                        post(url='http://10.10.0.1:5000/cancel')
                    reachy.head.l_antenna.speed_limit = 0.0
                    reachy.head.l_antenna.goal_position = 0.0
                elif config.counter[i] == 30:
                    if navigation:
                        post(url='http://10.10.0.1:5000/cancel')
                    reachy.head.r_antenna.speed_limit = 0.0
                    reachy.head.r_antenna.goal_position = 0.0
                if config.counter[i] >= 45:
                    if navigation:
                        post(url='http://10.10.0.1:5000/cancel')
                    playsound('/home/reachy/reachy_mobile_reachy/sounds/sonBB8_content2.mp3')
                    happy_antennas(reachy)
                    config.counter[i] = 0
                    config.detection[i] = 2
                    return
                config.detection[i] = 0
            else:
                counter_not_change += 1
                if counter_not_change == 20:
                    config.counter[i] = 0
                    reachy.head.l_antenna.speed_limit = 70.0
                    reachy.head.r_antenna.speed_limit = 70.0
                    reachy.head.l_antenna.goal_position = 140.0
                    reachy.head.r_antenna.goal_position = -140.0
