import cv2

IMAGE_WIDHT = 400
IMAGE_HEIGHT = 400
COLORS_PATH = "./static/amogus.gif"
COLORS_COUNT = 12

class ImgToSus:
    def __init__(self) -> None:
        self.img = None
        self.__load_colors()

    def __load_colors(self):
        cap = cv2.VideoCapture(COLORS_PATH)
        if not cap.isOpened():
            raise Exception("CAN'T OPEN SUS COLORS")

        self.colors = [] = []
        width, height = 0, 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if width == 0 or height == 0:
                height, width, _ = frame.shape
                w = width//COLORS_COUNT
                self.cell_size = (height, width//COLORS_COUNT)

            for i in range(0, width, width//COLORS_COUNT):
                self.colors.append(frame[ : height, i : i + w])

        # for frame in self.colors:
        #     try:
        #         cv2.imshow("frame", frame)
        #         cv2.waitKey()
        #     except Exception as e:
        #         print(str(e))

    def image_crop(self,image, n):
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
    
    def get_color_img(self):
        return self.colors[0]
    
    def save_image(self):
        if self.result.all() == None:
            self.convert_img()
        cv2.imwrite("./static/converted.jpg", self.result)

