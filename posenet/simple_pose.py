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

if __package__ is None or __package__ == '':
    from pose_engine import PoseEngine

else:
    from .pose_engine import PoseEngine
    from .pose_engine import KeypointType
    from . import config

from PIL import Image
from PIL import ImageDraw
import numpy as np
import os


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

def main(reachy):
    while(True):
        numpy_image = reachy.right_camera.wait_for_new_frame()
        #pil_image = Image.open(f'/home/reachy/reachy_mobile_reachy/posenet/images/509.jpg')
        pil_image = Image.fromarray(numpy_image, 'RGB')
        #pil_image.show()
        engine = PoseEngine(
            'posenet/models/mobilenet/posenet_mobilenet_v1_075_481_641_quant_decoder_edgetpu.tflite')
        poses, inference_time = engine.DetectPosesInImage(pil_image)
        reachy.head.l_antenna.speed_limit = 85.0
        reachy.head.r_antenna.speed_limit = 85.0
        #print(config.counter)
        for pose in poses:
            #if pose.score < 0.4: continue    #a quoi ça sert ?
            pose = pose.keypoints
            shoulder = pose[KeypointType.LEFT_SHOULDER]
            wrist = pose[KeypointType.LEFT_WRIST]
            difference = shoulder.point.y - wrist.point.y
            #print(difference)
            if difference > 0:
                config.detection = 1
                config.counter += 1
                if config.counter==2:
                    reachy.head.l_antenna.goal_position = 0.0
                elif config.counter == 3:
                    reachy.head.r_antenna.goal_position = 0.0
                if config.counter >= 5: #passe de 30 a 5
                    happy_antennas(reachy)
                    config.counter = 0
                    config.detection = 2
                    print("YOUPI")
                    return
            else:
                config.detection = 0
        time.sleep(1)

