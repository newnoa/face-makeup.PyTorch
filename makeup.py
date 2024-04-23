import cv2
import os
import numpy as np
from skimage.filters import gaussian
from test import evaluate
import torch
import argparse
import ast
from PIL import Image

def parse_args():
    parse = argparse.ArgumentParser()
    parse.add_argument('--img-path', default='imgs/116.jpg')
    parse.add_argument('--colors', default='[[230, 50, 20], [120, 70, 180], [20, 70, 180]]')
    parse.add_argument('--save-path', default='imgs/116t.jpg')
    return parse.parse_args()


def sharpen(img):
    img = img * 1.0
    gauss_out = gaussian(img, sigma=5)

    alpha = 1.5
    img_out = (img - gauss_out) * alpha + img

    img_out = img_out / 255.0

    mask_1 = img_out < 0
    mask_2 = img_out > 1

    img_out = img_out * (1 - mask_1)
    img_out = img_out * (1 - mask_2) + mask_2
    img_out = np.clip(img_out, 0, 1)
    img_out = img_out * 255
    return np.array(img_out, dtype=np.uint8)


def hair(image, parsing, part=17, color=[230, 50, 20]):
    b, g, r = color      #[10, 50, 250]       # [10, 250, 10]
    tar_color = np.zeros_like(image)
    tar_color[:, :, 0] = b
    tar_color[:, :, 1] = g
    tar_color[:, :, 2] = r

    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    tar_hsv = cv2.cvtColor(tar_color, cv2.COLOR_BGR2HSV)

    if part == 12 or part == 13:
        image_hsv[:, :, 0:2] = tar_hsv[:, :, 0:2]
    else:
        image_hsv[:, :, 0:1] = tar_hsv[:, :, 0:1]

    changed = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)

    if part == 17:
        changed = sharpen(changed)

    changed[parsing != part] = image[parsing != part]
    return changed


if __name__ == '__main__':
    # 1  face
    # 11 teeth
    # 12 upper lip
    # 13 lower lip
    # 17 hair

    if torch.cuda.is_available():
        device = torch.device("cuda")
        print('There are %d GPU(s) available.' % torch.cuda.device_count())
        print('We will use the GPU:', torch.cuda.get_device_name(0))
    else:
        print('No GPU available, using the CPU instead.')
        device = torch.device("cpu")

    args = parse_args()

    table = {
        'hair': 17,
        'upper_lip': 12,
        'lower_lip': 13
    }

    image_path = args.img_path
    cp = 'cp/79999_iter.pth'

    image = cv2.imread(image_path)
    ori = image.copy()
    parsing = evaluate(image_path, cp)
    parsing = cv2.resize(parsing, image.shape[0:2], interpolation=cv2.INTER_NEAREST)

    parts = [table['hair'], table['upper_lip'], table['lower_lip']]

    colors = ast.literal_eval(args.colors)

    for part, color in zip(parts, colors):
        image = hair(image, parsing, part, color)

    # print(image.dtype)
    # imageFile = Image.fromarray(np.uint8(cv2.resize(image, (512, 512))))
    # imageFile.save("D:/face-makeup.PyTorch/1.jpg")
    cv2.imwrite(args.save_path, image)
    # cv2.imshow('image', cv2.resize(ori, (512, 512)))
    # cv2.imshow('color', cv2.resize(image, (512, 512)))

    cv2.waitKey(0)
    cv2.destroyAllWindows()















