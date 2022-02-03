import numpy as np
import logging
import os
import matplotlib.pyplot as plt
from cv2 import cv2 as cv
from PIL import Image
from PIL import ImageDraw

from pycoral.adapters import classify, common, detect

from tflite_runtime.interpreter import Interpreter
from tflite_runtime.interpreter import load_delegate

from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

if __package__ is None or __package__ == '':
    from utils import piece2id
    from detect_board import get_board_cases
else:
    from tictactoe.reachy_tictactoe.utils import piece2id
    from tictactoe.reachy_tictactoe.detect_board import get_board_cases

import time

logger = logging.getLogger('reachy.tictactoe')

dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(dir_path, 'models')

board_cases = np.array((((81, 166, 260, 340),  # Coordinates first board cases (top-left corner) (Xbl, Xbr, Ytr, Ybr)
                         (166, 258, 260, 340),  # Coordinates second board cases
                         (258, 349, 260, 340),),

                        ((74, 161, 340, 432), (161, 261, 340, 432), (261, 360, 340, 432),),

                        ((65, 161, 432, 522), (161, 266, 432, 522), (266, 365, 432, 522),),))

# left, right, top, bottom
board_rect = np.array((62, 372, 250, 508,))

shape = (224, 224)


def draw_objects(draw, objs, labels):
    # Draws the bounding box and label for each object.
    for obj in objs:
        bbox = obj.bbox
        draw.rectangle([(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax)], outline='red')
        draw.text((bbox.xmin + 10, bbox.ymin + 10), '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score), fill='red')


def get_board_configuration(image):
    board = np.zeros((3, 3), dtype=np.uint8)
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    y1 = 125
    y2 = 405
    x1 = 75
    x2 = 367
    image = image[y1:y2, x1:x2]
    sanity_check = True
    path_model = '/home/reachy/reachy_mobile_reachy/tictactoe/reachy_tictactoe/models/tfliteV6' \
                 '/output_tflite_graph_edgetpu.tflite'
    path_label = '/home/reachy/reachy_mobile_reachy/tictactoe/reachy_tictactoe/models/tfliteV6/label.txt'
    labels = read_label_file(path_label) if path_label else {}
    interpreter = make_interpreter(path_model)
    interpreter.allocate_tensors()
    image = Image.fromarray(image)
    _, scale = common.set_resized_input(interpreter, image.size, lambda size: image.resize(size, Image.ANTIALIAS))
    args_threshold = 0.6
    interpreter.invoke()
    objs = detect.get_objects(interpreter, args_threshold, scale)
    if not objs:
        logger.info('No objects detected')
    for obj in objs:
        logger.info(f'photo_id : {obj.id}')
    image = image.convert('RGB')
    draw_objects(ImageDraw.Draw(image), objs, labels)
    photo_id = "_".join([time.strftime("%y-%m-%d_%H-%M-%S")])
    image.save(f'/home/reachy/reachy_mobile_reachy/tictactoe/images/{photo_id}.png')
    logger.info(f'Taille objs = {len(objs)}')
    if (len(objs) == 9):  # la détection doit détecter 9 objets dans l'image (1 par cases) si ce n'est pas le cas
        status = True
        Ly = [e.bbox.ymin for e in objs]
        index_y_all = np.argsort(Ly)[::-1]
        objs_sorted_y = np.array(objs, dtype=object)[index_y_all]
        for i in range(0, 7, 3):
            Ly_row = objs_sorted_y[i:i + 3]
            Lx = [e[2][0] for e in Ly_row]  # liste des xmin des 3 obj
            index_x = np.argsort(Lx)[::-1]  # tri décroissant
            Ly_row = Ly_row[index_x]  # tri sur X premiere ligne
            board[int(i / 3)] = Ly_row[:, :1].flatten()
        board = board[::-1, ::-1]
        logger.info(f'board forward returned : {board}')
        for i in range(3):
            a = np.flip(board[i, :])
            board[i, :] = a
        board = board[::-1]
        board = board.flatten()
        logger.info(f'board returned : {board}')
        logger.info(f'board size = {np.shape(board)}')
    else:
        status = False  # board[::-1, ::-1]

    return status, board, sanity_check


def is_board_valid(img):
    pil_img = Image.fromarray(img[ly:ry, lx:rx]).convert('RGB').resize(sizeInterpreterBoard, Image.ANTIALIAS)
    common.set_input(interpreterBoard, pil_img)
    interpreterBoard.invoke()
    result = classify.get_classes(interpreterBoard, top_k=1, score_threshold=0.1)
    assert result
    label = labelsBoard.get(result[0].id)
    label_index, score = result[0]
    logger.info('Board validity check', extra={'label': label, 'score': score, })
    return label == 'valid' and score > 0.65


def img_as_pil(img):
    return Image.fromarray(cv.cvtColor(img.copy(), cv.COLOR_BGR2RGB))
