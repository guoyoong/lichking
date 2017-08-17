# -*- coding: utf-8 -*-
from PIL import Image
from PIL import ImageEnhance
from pytesseract import *


def initTable(threshold=140):
    table = []
    for i in range(256):
        if i < threshold:
         table.append(0)
        else:
         table.append(1)

    return table


def getverify(name):
    rep = {'O': '0', 'A': '8',
           'I': '1', 'L': '1',
           'Z': '2', 'S': '8',
           'E': '6', 'G': '9',
           'B': '6', ' ': ''
           }
    im = Image.open(name)
    # 彩色图像转化为灰度图
    im = im.convert('L')
    # 降噪 二值化
    binary_image = im.point(initTable(), '1')
    # 错误替换
    text = image_to_string(binary_image, config='-psm 7').upper()
    for r in rep:
        text = text.replace(r, rep[r])
    return text

# 识别率低，暂时不用
if __name__ == '__main__':
    print getverify("D:\\source\\lichking\\lichking\\util\\png\\3128.png")  # 注意这里的图片要和此文件在同一个目录，要不就传绝对路径也行