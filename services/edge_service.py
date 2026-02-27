"""
Edge detection service with all functions included (from scratch + Canny)
"""
import numpy as np
import cv2
from utils.image_utils import validate_image

# ===========================
# Convolution
# ===========================
def convolve2d(img, kernel):
    kH, kW = kernel.shape
    padH, padW = kH // 2, kW // 2
    padded = np.pad(img, ((padH, padH), (padW, padW)), mode='edge')
    output = np.zeros_like(img, dtype=np.float32)

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            region = padded[i:i+kH, j:j+kW]
            output[i,j] = np.sum(region * kernel)

    return output


# ===========================
# Gaussian
# ===========================
def gaussian_kernel(size=5, sigma=1.0):
    ax = np.linspace(-(size//2), size//2, size)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2)/(2*sigma**2))
    return kernel / np.sum(kernel)


def gaussian_blur(img, size=5, sigma=1.0):
    return convolve2d(img.astype(np.float32), gaussian_kernel(size, sigma))


# ===========================
# Edge Operators
# ===========================
def sobel_edge(img, weight=1.0, kx_scale=1.0, ky_scale=1.0):

    Kx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]], dtype=np.float32) * kx_scale
    Ky = np.array([[-1,-2,-1],[0,0,0],[1,2,1]], dtype=np.float32) * ky_scale

    Gx = convolve2d(img, Kx)
    Gy = convolve2d(img, Ky)

    mag = np.sqrt(Gx**2 + Gy**2) * weight
    return np.clip(mag,0,255).astype(np.uint8)


def prewitt_edge(img, weight=1.0, kx_scale=1.0, ky_scale=1.0):

    Kx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], dtype=np.float32) * kx_scale
    Ky = np.array([[-1,-1,-1],[0,0,0],[1,1,1]], dtype=np.float32) * ky_scale

    Gx = convolve2d(img, Kx)
    Gy = convolve2d(img, Ky)

    mag = np.sqrt(Gx**2 + Gy**2) * weight
    return np.clip(mag,0,255).astype(np.uint8)


def roberts_edge(img, weight=1.0, kx_scale=1.0, ky_scale=1.0):

    Kx = np.array([[1,0],[0,-1]], dtype=np.float32) * kx_scale
    Ky = np.array([[0,1],[-1,0]], dtype=np.float32) * ky_scale

    Gx = convolve2d(img, Kx)
    Gy = convolve2d(img, Ky)

    mag = np.sqrt(Gx**2 + Gy**2) * weight
    return np.clip(mag,0,255).astype(np.uint8)


# ===========================
# Canny
# ===========================
def canny_edge(img, threshold=100):
    low = int(0.4*threshold)
    return cv2.Canny(img.astype(np.uint8), low, threshold)


# ===========================
# Service Class
# ===========================
class EdgeService:

    @staticmethod
    def apply_canny(image, threshold=100, blur_size=5, blur_sigma=1.0):

        if not validate_image(image):
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape)==3 else image
        blurred = gaussian_blur(gray, blur_size, blur_sigma)

        return canny_edge(blurred, threshold)


    @staticmethod
    def apply_sobel(image, blur_size, blur_sigma, weight, kx, ky):

        if not validate_image(image):
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape)==3 else image
        blurred = gaussian_blur(gray, blur_size, blur_sigma)

        return sobel_edge(blurred, weight, kx, ky)


    @staticmethod
    def apply_prewitt(image, blur_size, blur_sigma, weight, kx, ky):

        if not validate_image(image):
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape)==3 else image
        blurred = gaussian_blur(gray, blur_size, blur_sigma)

        return prewitt_edge(blurred, weight, kx, ky)


    @staticmethod
    def apply_roberts(image, blur_size, blur_sigma, weight, kx, ky):

        if not validate_image(image):
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape)==3 else image
        blurred = gaussian_blur(gray, blur_size, blur_sigma)

        return roberts_edge(blurred, weight, kx, ky)