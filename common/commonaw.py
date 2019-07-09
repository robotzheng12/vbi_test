import cv2
import numpy as np
from matplotlib import pyplot as plt


def compare_image(image1, image2, method='ahash'):
    """
    对比图片

    :param image1:用于对比的图片1
    :param image2:用于对比的图片2
    :return 图片相似度
    """
    method_dict = {'grayhist': 'classify_gray_hist', 'splithist': 'classify_hist_with_split',
                   'ahash': 'classify_aHash', 'phash': 'classify_pHash'}
    size = dismantle_image_arithmetic((len(image1[0]), len(image1)))
    print(size)
    return eval(method_dict.get(method))(image1, image2, size)


def classify_gray_hist(image1, image2, size=(256, 256)):
    """
    以灰度直方图作为相似比较的实现

    :param image1:用于对比的图片1
    :param image2:用于对比的图片1
    :param size:请求的大小(以像素为单位)
    :return: 图片相似度
    """
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    plt.plot(range(256), hist1, 'r')
    plt.plot(range(256), hist2, 'b')
    plt.show()
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    similarity = degree / len(hist1)
    return similarity


def calculate(image1, image2):
    """
    计算直方图的重合度

    :param image1: 用于对比的图片1
    :param image2: 用于对比的图片2
    :return: 图片相似度
    """
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree


def classify_hist_with_split(image1, image2, size=(256, 256)):
    """
    将图像resize后，分离为三个通道，再计算每个通道的相似值

    :param image1: 用于对比的图片1
    :param image2: 用于对比的图片2
    :param size: 请求的大小(以像素为单位)
    :return: 图片相似度
    """
    # 将图像resize后，分离为三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    similarity = sub_data / 3
    return similarity[0]


def hamming_distance(hash1, hash2):
    """
    计算汉明距离

    :param hash1: type(list)
    :param hash2:
    :return:
    """
    num = 0
    for index in range(len(hash1)):
        if hash1[index] != hash2[index]:
            num += 1
    return num


def getHash(image):
    """
    获取灰度图hash表

    :param image: 灰度图
    :return: hash表
    """
    average = np.mean(image)
    hash = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i, j] > average:
                hash.append(1)
            else:
                hash.append(0)
    return hash


def classify_aHash(image1, image2, size=(256, 256)):
    """
    平均哈希算法计算

    :param image1:用于对比的图片1
    :param image2:用于对比的图片2
    :param size:请求的大小(以像素为单位)
    :return:相似度
    """
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    hash1 = getHash(gray1)
    hash2 = getHash(gray2)
    return 1 - hamming_distance(hash1, hash2) / (size[0] * size[1])


def classify_pHash(image1, image2, size=(32, 32)):
    """
    灰度图转为浮点型,进行平均哈希算法计算

    :param image1:用于对比的图片1
    :param image2:用于对比的图片2
    :param size:请求的大小(以像素为单位)
    :return:相似度
    """
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct1 = cv2.dct(np.float32(gray1))
    dct2 = cv2.dct(np.float32(gray2))
    # 取左上角的8*8，这些代表图片的最低频率
    # 这个操作等价于c++中利用opencv实现的掩码操作
    # 在python中进行掩码操作，可以直接这样取出图像矩阵的某一部分
    dct1_roi = dct1[0:size[0], 0:size[1]]
    dct2_roi = dct2[0:size[0], 0:size[1]]
    hash1 = getHash(dct1_roi)
    hash2 = getHash(dct2_roi)
    return 1 - hamming_distance(hash1, hash2) / (size[0] * size[1])


def dismantle_image_arithmetic(imagesize):
    """
    图片按原始比例拆解
    :param imagesize: 图片像素
    :return: (横向拆解份数，纵向拆解份数)tuple
    """
    x, y = imagesize[0], imagesize[1]
    i = 1
    while True:
        if x / i < 256 or y / i < 256:
            if x % i == 0 and y % i == 0:
                return (int(x / i), int(y / i))
            else:
                if int(x / i) < 128 or (y / i) < 128:
                    if x > y:
                        return (320, 180)
                    else:
                        return (180, 320)
        else:
            i += 1


if __name__ == '__main__':
    img1 = cv2.imread(r'E:\workspace\python_project\vbitest\data\images\chrome_target_image.png')
    num = dismantle_image_arithmetic((len(img1[0]), len(img1)))
    img2 = cv2.resize(img1, dsize=num)
    print(num)

# if __name__ == '__main__t':
#     #t = dismantle_image_arithmetic((1920, 1080))
#     img1 = cv2.imread(r'E:\workspace\python_project\vbitest\data\images\chrome_target_image.png')
#     img2 = cv2.resize(img1, (144, 256))
#     img3 = cv2.resize(img2, (9, 16))
#     # img2 = cv2.imread(r'E:/workspace/python_project/vbitest/data/images/TC_SCREEN_RESTORE_5.png')
#     degree = compare_image(img1, img2, method='ahash')
#     print(degree)
