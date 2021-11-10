import cv2
import imageio
import os

HOME_PATH = os.path.abspath(os.getcwd())
CONVERTED_PATH = HOME_PATH + "/temporary/"
CONVERTED_FILENAME_TEMPLATE = "converted_$key.gif"
COLORS_PATH = HOME_PATH + "/converter_files/amogus.gif"
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

    def __increase_contrast(self, img):
        lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # Вернет подходящий sus цвет
    def __get_sus_color(self, requested_colour):
        min_colours = {}
        # эту жесть надо переделать, но я хз пока как лучше
        for b_c, g_c, r_c in self.colors_keys.keys():
            if r_c > requested_colour[2]:
                rd = (r_c - requested_colour[2]) ** 2
            else:
                rd = (requested_colour[2] - r_c) ** 2

            if g_c > requested_colour[1]:
                gd = (g_c - requested_colour[1]) ** 2
            else:
                gd = (requested_colour[1] - g_c) ** 2
            
            if b_c > requested_colour[0]:
                bd = (b_c - requested_colour[0]) ** 2
            else:
                bd = (requested_colour[0] - b_c) ** 2

            min_colours[(rd + gd + bd)] = self.colors_keys[(b_c, g_c, r_c)]
        
        # if requested_colour[1] == 255:
        #     print(requested_colour)
        #     print(min_colours)
        #     print(min(min_colours.keys()))
        return min_colours[min(min_colours.keys())]

    def __get_cell_color(self, frame):  
        img = cv2.resize(frame, (1, 1))
        b,r,g = img.astype(int)[0][0]   
        return(b,g,r)

    # Загрузка основного изображения для преобразования
    def load_img(self, path: str = None, increase_contrast: bool = True):
        if path == None or path == '':
            raise Exception("IMAGE PATH CAN'T BE EMPTY")
        
        img = cv2.imread(path)
        print("Found image")
        h, w, _ = img.shape
        ah = h // self.cell_h * self.cell_h
        aw = w // self.cell_w * self.cell_w
        img = cv2.resize(img, (aw, ah))
        if increase_contrast:
            img = self.__increase_contrast(img)
            print("Contrast increased")
        self.img = img
        print("Image loaded")
    
    # Преобразование картинки
    def convert_img(self, gif_speed: float = 0.05) -> str:
        if self.img.all() == None:
            raise Exception("NO IMAGE LOADED")

        print("Start converting image!")
        print("Generating frames...")

        frames = []
        for i in range(len(self.colors_img[0])):
            frames.append(self.img.copy())

        height, width, _ = self.img.shape
        for y in range(0, height, self.cell_h):
            for x in range(0, width, self.cell_w):
                color = self.__get_cell_color(self.img[y:y + self.cell_h, x:x + self.cell_w])
                color_key = self.__get_sus_color(color)
                if color_key != None:
                    color_img = self.colors_img[color_key]

                    for i in range(len(color_img)):
                        frames[i][y:y + self.cell_h, x:x + self.cell_w, :3] = color_img[i]

        print("Frames generated")
        print("Generating gif...")

        result_filename = CONVERTED_FILENAME_TEMPLATE
        with imageio.get_writer(CONVERTED_PATH + result_filename, mode="I", duration=gif_speed) as writer:
            for frame in frames:
                writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
        print("Gif generated! Done.")
        return result_filename