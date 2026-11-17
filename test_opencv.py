import cv2

print("OpenCV version:", cv2.__version__)

image = cv2.imread("test.jpg")
if image is not None:
    print("Image loaded successfully!")
    print("Image dimensions:", image.shape)
else:
    print("Could not load image.")