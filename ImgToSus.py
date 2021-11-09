from re import DEBUG
import cv2
import webcolors
import numpy as np

CONVERTED_PATH = "./static/converted.jpg"
COLORS_PATH = "./static/amogus.gif"
COLORS_COUNT = 12
COLOR_PROB_X = 63
COLOR_PROB_Y = 12
COLOR_SCALE = 3

class ImgToSus:
    def __init__(self, debug: bool = False, scale: int = COLOR_SCALE) -> None:
        self.debug = debug
        self.img = None
        self.__load_colors(scale)

    # загружает амогус цвета
    # хранится в виде двух словарей:
    # self.colors_img - {ключ картинки: [список изображений]}
    # self.colors_keys - {brg ключ цвета: ключ цвета}
    def __load_colors(self, scale: int):
        cap = cv2.VideoCapture(COLORS_PATH)
        if not cap.isOpened():
            raise Exception("CAN'T OPEN SUS COLORS")

        self.colors_img = {}
        self.colors_keys = {}
        width, height = 0, 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if width == 0 or height == 0:
                height, width, _ = frame.shape
                w = width//COLORS_COUNT
                self.cell_size = (height, width//COLORS_COUNT)
                cell_w = w//scale
                cell_h = height//scale

            j = 0
            for i in range(0, width, width//COLORS_COUNT):
                current_frame = frame[ : height, i : i + w]
                _, l,_ = current_frame.shape
                if l >= w:
                    key = j % COLORS_COUNT
                    current_frame_r = cv2.resize(current_frame, (cell_w, cell_h))
                    if key not in self.colors_img.keys():
                        self.colors_img.update({key: [current_frame_r]})
                        b, g, r = current_frame[COLOR_PROB_Y, COLOR_PROB_X]
                        self.colors_keys.update({(b, g, r): key})
                    else:
                        self.colors_img[key].append(current_frame_r)
                    j += 1
            
        self.cell_w = cell_w
        self.cell_h = cell_h

    # Вернет подходящий sus цвет
    def __get_sus_color(self, requested_colour):
        min_colours = {}
        for b_c, g_c, r_c in self.colors_keys.keys():
            rd = (r_c - requested_colour[0]) ** 2
            gd = (g_c - requested_colour[1]) ** 2
            bd = (b_c - requested_colour[2]) ** 2
            min_colours[(rd + gd + bd)] = self.colors_keys[(b_c, g_c, r_c)]
        return min_colours[min(min_colours.keys())]

    #TODO
    # Поиск цвета для замены клетки 
    # Возвращает bgr ключ цвета (например (197, 17, 17))
    def __get_cell_color(self, frame):
        h, w, _ = frame.shape
        # if h <= 2 or w <= 2:
        #     return (0,0,0)
        print((h, w))
        return frame[h//2, w//2]

    # Загрузка основного изображения для преобразования
    def load_img(self, path: str):
        if path == None or path == '':
            raise Exception("IMAGE PATH CAN'T BE EMPTY")
        
        self.img = cv2.imread(path)
        h, w, _ = self.img.shape
        ah = h // self.cell_h * self.cell_h
        aw = w // self.cell_w * self.cell_w
        self.img = cv2.resize(self.img, (aw, ah))
    
    # Преобразование картинки
    def convert_img(self):
        if self.img.all() == None:
            raise Exception("NO IMAGE LOADED")

        height, width, _ = self.img.shape
        for y in range(0, height, self.cell_h):
            for x in range(0, width, self.cell_w):
                print((y, y + self.cell_w))
                print((height, width))
                color = self.__get_cell_color(self.img[y:y + self.cell_h, x:x + self.cell_w])
                color_key = self.__get_sus_color(color)
                print((color, color_key))
                if color_key != None:
                    color_img = self.colors_img[color_key]
                    self.img[y:y + self.cell_h, x:x + self.cell_w, :3] = color_img[2]

        # cv2.imshow("e", self.img)
        # cv2.waitKey()
    
    # сохранение изменненого изображения
    def save_converted_image(self):
        cv2.imwrite(CONVERTED_PATH, self.img)

