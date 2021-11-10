from cv2 import FlannBasedMatcher
from ImgToSus import ImgToSus
import time
start_time = time.time()

conv = ImgToSus(debug=False, scale=7)
conv.load_img("./static/test.jpg", increase_contrast=True)
print(conv.convert_img())
print("--- %s seconds ---" % (time.time() - start_time))
