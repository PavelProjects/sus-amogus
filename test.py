from ImgToSus import ImgToSus

conv = ImgToSus(debug=False)
conv.load_img("./static/pupa.jpg")
conv.convert_img()
input("loaded")