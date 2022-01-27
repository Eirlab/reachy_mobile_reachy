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


def pose_net(reachy):
    numpy_image = reachy.right_camera.wait_for_new_frame()
    pil_image = Image.fromarray(numpy_image, 'RGB')
    engine = PoseEngine(
        'posenet/models/mobilenet/posenet_mobilenet_v1_075_481_641_quant_decoder_edgetpu.tflite')
    poses, inference_time = engine.DetectPosesInImage(pil_image)
    for i in range(len(poses)):
        pose = poses[i].keypoints
        shoulder = pose[KeypointType.LEFT_SHOULDER]
        wrist = pose[KeypointType.LEFT_WRIST]
        difference = shoulder.point.y - wrist.point.y
        print(difference)
        if difference > 0:
            reachy.head.l_antenna.goal_position = 0.0
            counter_change = True
            config.detection[i] = 1
            config.counter[i] += 1
            if config.counter[i] == 2:
                reachy.head.r_antenna.goal_position = 0.0
            if config.counter[i] == 3:
                happy_antennas(reachy)
                config.counter[i] = 0
                config.detection[i] = 2
                return

        else:
            config.detection[i] = 0
            counter_change = False
        return counter_change


def main(reachy):
    y = 0
    turn_right = True
    counter_change = True
    reachy.head.l_antenna.speed_limit = 0.0
    reachy.head.r_antenna.speed_limit = 0.0
    # previous_counter = [0] * 20
    while True:
        time.sleep(0.5)
        for i in range(20):
            # if previous_counter[i] != config.counter[i]:
            #     counter_change = True
            if config.detection[i] == 2:
                return
        # previous_counter = config.counter
        if counter_change:
            print("counter changed")
            counter_change = pose_net(reachy)
            # time.sleep(4.0)
        else:
            print("counter NOT changed")
            if y < 0.5 and turn_right:
                y += 0.65
            else:
                turn_right = False
                if y > -0.5:
                    y -= 0.65
                else:
                    turn_right = True
                    y += 0.65
            reachy.head.l_antenna.goal_position = 140.0
            reachy.head.r_antenna.goal_position = -140.0
            reachy.head.look_at(0.95, y, -0, 0.5)
            time.sleep(0.5)
            config.counter = [0] * 20
            counter_change = pose_net(reachy)

# def main(reachy):
#     while True:
#         numpy_image = reachy.right_camera.wait_for_new_frame()
#         pil_image = Image.fromarray(numpy_image, 'RGB')
#         engine = PoseEngine(
#             'posenet/models/mobilenet/posenet_mobilenet_v1_075_481_641_quant_decoder_edgetpu.tflite')
#         poses, inference_time = engine.DetectPosesInImage(pil_image)
#         reachy.head.l_antenna.speed_limit = 85.0
#         reachy.head.r_antenna.speed_limit = 85.0
#         for i in range(len(poses)):
#             pose = poses[i].keypoints
#             shoulder = pose[KeypointType.LEFT_SHOULDER]
#             wrist = pose[KeypointType.LEFT_WRIST]
#             difference = shoulder.point.y - wrist.point.y
#             if difference > 0:
#                 config.detection[i] = 1
#                 config.counter[i] += 1
#                 if config.counter[i] == 2:
#                     reachy.head.l_antenna.goal_position = 0.0
#                 elif config.counter[i] == 3:
#                     reachy.head.r_antenna.goal_position = 0.0
#                 if config.counter[i] >= 2:
#                     happy_antennas(reachy)
#                     config.counter[i] = 0
#                     config.detection[i] = 2
#                     return
#                 config.detection[i] = 0
#         time.sleep(1.0)
