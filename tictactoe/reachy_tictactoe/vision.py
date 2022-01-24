import numpy as np
import cv2 as cv
import logging
import os
import matplotlib.pyplot as plt

from PIL import Image
from PIL import ImageDraw

# TC from edgetpu.utils import dataset_utils
# from utils import dataset

# TC from edgetpu.classification.engine import ClassificationEngine
# TC from adapters import classify, common
# TC from utils.edgetpu import make_interpreter
# TC from utils.dataset import read_label_file

from pycoral.adapters import classify, common, detect
# from pycoral.utils.edgetpu import make_interpreter
# from pycoral.utils.dataset import read_label_file

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

# TC
dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(dir_path, 'models')

# TC boxes_classifier = ClassificationEngine(os.path.join(model_path, 'ttt-boxes.tflite'))
# TC boxes_labels = dataset_utils.read_label_file(os.path.join(model_path, 'ttt-boxes.txt'))
# path_model_box = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/models/ttt_classif.tflite'
# path_label_box = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/models/ttt_classif.txt'
# path_model_board = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/models/ttt-valid-board.tflite'
# path_label_board = '/home/reachy/dev/reachy-tictactoe/reachy_tictactoe/models/ttt-valid-board.txt'



# TC valid_classifier = ClassificationEngine(os.path.join(model_path, 'ttt-valid-board.tflite'))
# TC valid_labels = dataset_utils.read_label_file(os.path.join(model_path, 'ttt-valid-board.txt'))


board_cases = np.array((
    ((81, 166, 260, 340),  # Coordinates first board cases (top-left corner) (Xbl, Xbr, Ytr, Ybr)
     (166, 258, 260, 340),  # Coordinates second board cases
     (258, 349, 260, 340),),

    ((74, 161, 340, 432),
     (161, 261, 340, 432),
     (261, 360, 340, 432),),

    ((65, 161, 432, 522),
     (161, 266, 432, 522),
     (266, 365, 432, 522),),
))

# left, right, top, bottom
board_rect = np.array((
    62, 372, 250, 508,
))

shape = (224, 224)


def draw_objects(draw, objs, labels):
    # Draws the bounding box and label for each object.
    for obj in objs:
        bbox = obj.bbox
        draw.rectangle([(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax)],
                       outline='red')
        draw.text((bbox.xmin + 10, bbox.ymin + 10),
                  '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score),
                  fill='red')


def get_board_configuration(image):
    board = np.zeros((3, 3), dtype=np.uint8)
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    # boardEmpty = np.zeros((3, 3), dtype=np.uint8)

    # size for crop the image taking by the reachy's camera
    # y1 = 150
    # y2 = 450
    # x1 = 90
    # x2 = 420
    y1 = 360
    y2 = 650
    x1 = 50
    x2 = 410
    # dim = (300,300)
    image = image[y1:y2, x1:x2]

    # image = cv.resize(image, dim)

    # try:
    #     custom_board_cases = get_board_cases(img)
    # except Exception as e:
    #     logger.warning('Board detection failed', extra={'error': e})
    #     custom_board_cases = board_cases
    # custom_board_cases = board_cases #grille personnalisé avec notebook (coordonnées)
    sanity_check = True

    # for row in range(3):
    #    for col in range(3):
    #        lx, rx, ly, ry = custom_board_cases[row, col]
    #        #img = img.convert('RGB')
    #        #img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    #       #img = img.resize(shape, Image.NEAREST)
    #        #TC piece, score = identify_box(img[ly:ry, lx:rx])
    #        piece, score = identify_box(img[ly:ry, lx:rx])
    # if score < 0.9:
    #    sanity_check = False
    #    return [], sanity_check
    # We invert the board to present it from the Human point of view
    #        if score < 0.9: #tolerance à changer
    #            piece = 0
    #        board[2 - row, 2 - col] = piece

    # TRAITEMENT DE L'IMAGE POUR CROP

    # Load image and convert to grayscale
    # gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    # blur = cv.medianBlur(gray, 5)
    #
    # # filter out noise, then threshold
    # sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    # sharpen = cv.filter2D(blur, -1, sharpen_kernel)
    # thresh = cv.threshold(sharpen, 140, 255, cv.THRESH_BINARY_INV)[1]
    #
    # # morphology treatment then find contours
    # kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    # close = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel, iterations=2)
    # cnts = cv.findContours(close, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    #
    # # find the largest contour
    # max_cnt = None
    # max_area = 0
    # maximum = 100000
    # for c in cnts:
    #     area = cv.contourArea(c)
    #     if max_area < area < maximum:
    #         max_area = area
    #         max_cnt = c
    #
    # # crop the largest contour
    # x, y, w, h = cv.boundingRect(max_cnt)
    # x = x - 10 if x - 10 > 0 else x
    # y = y - 10 if y - 10 > 0 else y
    # h = h + 10 if h + 10 < image.shape[0] else h
    # w = w + 10 if w + 10 < image.shape[1] else w
    # image = image[y:y + h, x:x + w]
    # plt.imshow(image)
    # plt.show()

    # PASSAGE DANS LE RESEAU DE NEURONES
    path_model = '/home/reachy/reachy_mobile_reachy/tictactoe/reachy_tictactoe/models/tfliteV6/output_tflite_graph_edgetpu.tflite'
    path_label = '/home/reachy/reachy_mobile_reachy/tictactoe/reachy_tictactoe/models/tfliteV6/label.txt'


    labels = read_label_file(path_label) if path_label else {}
    interpreter = make_interpreter(path_model)
    interpreter.allocate_tensors()

    image = Image.fromarray(image)

    _, scale = common.set_resized_input(interpreter, image.size, lambda size: image.resize(size, Image.ANTIALIAS))

    args_threshold = 0.6

    # for _ in range(args_count):
    interpreter.invoke()
    objs = detect.get_objects(interpreter, args_threshold, scale)

    if not objs:
        logger.info('No objects detected')

    for obj in objs:
        logger.info(f'id : {obj.id}')

    image = image.convert('RGB')
    draw_objects(ImageDraw.Draw(image), objs, labels)
    id = "_".join([time.strftime("%y-%m-%d_%H-%M-%S")])
    image.save(f'/home/reachy/reachy_mobile_reachy/tictactoe/images/{id}.png')

    ok = False
    logger.info(f'Taille objs = {len(objs)}')
    if (len(objs) == 9):  # la détection doit détecter 9 objets dans l'image (1 par cases) si ce n'est pas le cas il faut recommencer la détection
        ok = True
        Ly = [e.bbox.ymin for e in objs]
        index_y_all = np.argsort(Ly)[::-1]
        objs_sorted_y = np.array(objs, dtype=object)[index_y_all]
        # print(objs_sorted_y)

        for i in range(0, 7, 3):
            Ly_row = objs_sorted_y[i:i + 3]
            Lx = [e[2][0] for e in Ly_row]  # liste des xmin des 3 obj
            index_x = np.argsort(Lx)[::-1]  # tri décroissant
            np.array(Lx)[index_x]
            Ly_row = Ly_row[index_x]  # tri sur X pemiere ligne

            board[int(i / 3)] = Ly_row[:, :1].flatten()
        board = board[::-1, ::-1]
        logger.info(f'board AVANT RETOURNEEEEEEEEEEEEEE : {board}')
        for i in range(3):
            a = np.flip(board[i, :])
            board[i, :] = a

        board = board[::-1]
        board = board.flatten()
        logger.info(f'board RETOURNEEEEEEEEEEEEEE : {board}')
        logger.info(f'taille board = {np.shape(board)}')

        # if board.any():
        #    ok = False 
        # if np.array_equal(board,boardEmpty)==False: #board is not equal to a array of zero (not empty)
        #     logger.info('JE PASSE DANS LE FALSE EQUAL => PAS EGAUX LES DEUX MATRICE ')
        #     ok = False 
        # else : 
        #     ok = True
    else:
        ok = False
        # board[::-1, ::-1]

    return ok, board, sanity_check


# TC def identify_box(box_img):

# TC res = boxes_classifier.classify_with_image(img_as_pil(box_img), top_k=1)
# box_img = cv.cvtColor(box_img, cv.COLOR_BGR2RGB)
# box_img = cv.resize(box_img , (224,224))
# pil_img = Image.fromarray(box_img).convert('RGB').resize(sizeInterpreterBox, Image.ANTIALIAS)
# common.set_input(interpreterBox, img_as_pil(box_img))
# common.set_input(interpreterBox, pil_img)
# interpreterBox.invoke()
# result = classify.get_classes(interpreterBox, top_k=1, score_threshold=0.1)
# label = labelsBox.get(result[0].id)

# box_image = Image.fromarray(box_img)
# _, scale = common.set_resized_input(interpreter, box_img.size, lambda size: image.resize(size, Image.ANTIALIAS))

# args_count = 5
# args_threshold = 0.5

# for _ in range(args_count):
#   start = time.perf_counter()
#    interpreter.invoke()
#    inference_time = time.perf_counter() - start
#    objs = detect.get_objects(interpreter, args_threshold, scale)
#    print('%.2f ms' % (inference_time * 1000))

# if not objs:
#    print('No objects detected')

# for obj in objs:
# obj = objs[0]
#    print(labels.get(obj.id, obj.id))
#    print('  id:    ', obj.id)
#    print('  score: ', obj.score)
#    print('  bbox:  ', obj.bbox)


# logger.info(f'label : {label}')
# assert result

# label, score = result[0]

# return label, score


def is_board_valid(img):
    # TC lx, rx, ly, ry = board_rect
    # board_img = img[ly:ry, lx:rx]
    # board_img = img[ly:ry, lx:rx]
    # img = img.convert('RGB')
    # board_img = cv.cvtColor(board_img, cv.COLOR_BGR2RGB)
    # board_img = board_img.resize(shape, Image.NEAREST)
    # board_img = cv.resize(board_img , shape)
    # TC res = valid_classifier.classify_with_image(img_as_pil(board_img), top_k=1)
    pil_img = Image.fromarray(img[ly:ry, lx:rx]).convert('RGB').resize(sizeInterpreterBoard, Image.ANTIALIAS)
    # common.set_input(interpreterBoard, img_as_pil(board_img))
    common.set_input(interpreterBoard, pil_img)
    interpreterBoard.invoke()
    result = classify.get_classes(interpreterBoard, top_k=1, score_threshold=0.1)
    assert result
    label = labelsBoard.get(result[0].id)

    label_index, score = result[0]
    # TC label = valid_labels[label_index]
    logger.info('pouetteeeee')
    logger.info('Board validity check', extra={
        'label': label,
        'score': score,
    })

    return label == 'valid' and score > 0.65


def img_as_pil(img):
    return Image.fromarray(cv.cvtColor(img.copy(), cv.COLOR_BGR2RGB))
