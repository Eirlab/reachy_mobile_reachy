import time
from pose_engine import PoseEngine
from PIL import Image
from PIL import ImageDraw
import cv2 as cv
import matplotlib.pyplot as plt

import numpy as np
import os
from reachy_sdk import ReachySDK


print("ok")
reachy = ReachySDK(host='localhost')

while (1):
    # cv.destroyAllWindows()
    print("ok")
    image = reachy.right_camera.last_frame
    # image=Image.fromarray(image)
    print("ok2")
    # plt.figure()
    # plt.imshow((cv.cvtColor(np.asanyarray(image), cv.COLOR_BGR2RGB)))

    cv.imshow('right_frame', image)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    
    engine = PoseEngine(
        'models/mobilenet/posenet_mobilenet_v1_075_481_641_quant_decoder_edgetpu.tflite')
    poses, inference_time = engine.DetectPosesInImage(image)
    print('Inference time: %.f ms' % (inference_time * 1000))

    for pose in poses:
        if pose.score < 0.4: continue
        print('\nPose Score: ', pose.score)
        for label, keypoint in pose.keypoints.items():
            print('  %-20s x=%-4d y=%-4d score=%.1f' %
                  (label.name, keypoint.point[0], keypoint.point[1], keypoint.score))
 
    
    time.sleep(1.0)
