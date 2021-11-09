from ImgToSus import ImgToSus

conv = ImgToSus(debug=False, scale=6)
conv.load_img("./static/test.jpg")
conv.convert_img()
conv.save_converted_image()
input("loaded")