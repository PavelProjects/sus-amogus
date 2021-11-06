from re import DEBUG
import cv2
import webcolors
from webcolors import rgb_to_name

IMAGE_WIDHT = 400
IMAGE_HEIGHT = 400
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
                        color = self.__closest_colour((r, g, b))
                        self.colors_keys.update({color: key})
                    else:
                        self.colors_img[key].append(current_frame)
                    j += 1
            
        if self.debug:
            self.__show_colors()

    def __show_colors(self):
        print(self.colors_keys)
        for key in self.colors_img.keys():
            try:               
                for frame in self.colors_img[key]:
                    cv2.imshow("frame", frame)
                    cv2.waitKey()
            except Exception as e:
                print(str(e))

    def __closest_colour(self, requested_colour):
        min_colours = {}
        for key, name in webcolors.CSS21_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - requested_colour[0]) ** 2
            gd = (g_c - requested_colour[1]) ** 2
            bd = (b_c - requested_colour[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        return min_colours[min(min_colours.keys())]

    def image_crop(self, n):
        images = []  
        width, height, _ = self.img.shape

        for i in range(0, width, width//n):
            for j in range(0, height, height//n):
                images.append(self.img[i:i + width//n, j:j + height//n])
        return images

    def get_color_img(self):
        return self.colors_img[0]

    def image_crop(self, image, n):
        pass

    def load_img(self, path: str, resize: bool = True):
        if path == None or path == '':
            raise Exception("IMAGE PATH CAN'T BE EMPTY")
        
        self.img = cv2.imread(path)
        if resize:
            self.img = cv2.resize(self.img, (IMAGE_WIDHT, IMAGE_HEIGHT))
    
    def convert_img(self):
        if self.img.all() == None:
            raise Exception("NO IMAGE LOADED")
        
        self.result = self.img
        img = self.get_color_img()
        h, w = self.cell_size
        print(f"{self.img.shape} {img.shape}")
        self.result[:h, :w, :3] = img

        return self.result
    
    def save_converted_image(self):
        if self.result.all() == None:
            self.convert_img()
        cv2.imwrite(CONVERTED_PATH, self.result)

