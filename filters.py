import cv2
import numpy as np

def blur(img):
    blurred_img = cv2.blur(img, (11, 11))
    return blurred_img

def checkered_Face(img):
    rows, cols, _ = img.shape
    for i in range(0, rows, 8):
        for j in range(0, cols, 8):
            img[i:i+8, j:j+8, :] = img[i, j, :]
    return img

def edge_mask(img, line_size, blur_value):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, blur_value)
    edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
    return edges

def color_quantization(img, k):
    data = np.float32(img).reshape((-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    ret, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    result = center[label.flatten()]
    result = result.reshape(img.shape)
    return result

def img2cartoon(img):
    line_size = 7
    blur_value = 7
    edges = edge_mask(img, line_size, blur_value)
    
    total_color = 9
    img = color_quantization(img, total_color)
    blurred = cv2.bilateralFilter(img, d=7, sigmaColor=200, sigmaSpace=200)
    cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)
    return cartoon

def invert_Filter(img):
    img = cv2.bitwise_not(img)
    return img

def sharpen(img):
    kernel = np.array([[-1, -1, -1], [-1, 9.5, -1], [-1, -1, -1]])
    img_sharpen = cv2.filter2D(img, -1, kernel)
    return img_sharpen

def pencil_sketch_gray(img):
    sk_gray, _ = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.1) 
    return  sk_gray

def redFilter(img):
    B, G, R = cv2.split(img)
    G = np.ones_like(G)
    B = np.ones_like(B)
    result = cv2.merge((B,G,R))
    return result

def cyanFilter(img):
    B, G, R = cv2.split(img)
    R = np.zeros_like(R)
    result = cv2.merge((B,G,R))
    return result