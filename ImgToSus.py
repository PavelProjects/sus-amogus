from re import DEBUG
import cv2
import webcolors
import numpy as np

CONVERTED_PATH = "./static/converted.jpg"
COLORS_PATH = "./static/amogus.gif"
COLORS_COUNT = 12
COLOR_PROB_X = 63
COLOR_PROB_Y = 12

class ImgToSus:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self.img = None
        self.__load_colors()

    # загружает амогус цвета
    # хранится в виде двух словарей:
    # self.colors_img - {ключ картинки: [список изображений]}
    # self.colors_keys - {brg ключ цвета: ключ цвета}
    def __load_colors(self):
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

            j = 0
            for i in range(0, width, width//COLORS_COUNT):
                current_frame = frame[ : height, i : i + w]
                _, l,_ = current_frame.shape
                if l >= w:
                    key = j % COLORS_COUNT
                    if key not in self.colors_img.keys():
                        self.colors_img.update({key: [current_frame]})
                        b, g, r = current_frame[COLOR_PROB_Y, COLOR_PROB_X]
                        self.colors_keys.update({(b, g, r): key})
                    else:
                        self.colors_img[key].append(current_frame)
                    j += 1
            
        self.cell_w = w
        self.cell_h = height
        if self.debug:
            self.__show_colors()

    # для дебага, выводит амогусов
    def __show_colors(self):
        print(self.colors_keys)
        for key in self.colors_img.keys():
            try:               
                for frame in self.colors_img[key]:
                    cv2.imshow("frame", frame)
                    cv2.waitKey()
            except Exception as e:
                print(str(e))

    # Вернет название цвета исходя из rgb кода
    def __closest_colour(self, requested_colour):
        min_colours = {}
        for key, name in webcolors.CSS21_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - requested_colour[0]) ** 2
            gd = (g_c - requested_colour[1]) ** 2
            bd = (b_c - requested_colour[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        return min_colours[min(min_colours.keys())]

    # Поиск цвета для замены клетки 
    # Возвращает bgr ключ цвета (например (197, 17, 17))
    def __get_cell_color(self, frame):
        return (17, 17, 197)

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
        for x in range(0, width, self.cell_w):
            for y in range(0, height, self.cell_h):
                color = self.__get_cell_color(self.img[x:x + self.cell_h, y:y + self.cell_w])
                color_key = self.colors_keys[color]
                if color_key != None:
                    color_img = self.colors_img[color_key]
                    try:
                        print(color_img[2].shape)
                        self.img[y:y + self.cell_h, x:x + self.cell_w, :3] = color_img[2]
                    except Exception as e:
                        print(f"#{y} - {x} | {self.img[y:y + self.cell_h, x:x + self.cell_w, :3].shape} {str(e)}")

        cv2.imshow("e", self.img)
        cv2.waitKey()
    
    # сохранение изменненого изображения
    def save_converted_image(self):
        if self.result.all() == None:
            self.convert_img()
        cv2.imwrite(CONVERTED_PATH, self.img)

