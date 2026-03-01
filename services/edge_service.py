import numpy as np
import cv2
from utils.image_utils import validate_image
from services.filter_service import FilterService

# ===========================
# Gaussian Blur (uses FilterService)
# ===========================
def gaussian_blur(img, size=5, sigma=1.0):
    """Apply Gaussian blur using FilterService"""
    kernel = FilterService._gaussian_kernel(size, sigma)
    return FilterService._convolve2d(img.astype(np.float32), kernel)

# ===========================
# Sobel Edge
# ===========================
def sobel_kernel(size):
    if size == 3:
        Kx = np.array([
            [-1,0,1],
            [-2,0,2],
            [-1,0,1]
        ], dtype=np.float32)

        Ky = np.array([
            [-1,-2,-1],
            [ 0, 0, 0],
            [ 1, 2, 1]
        ], dtype=np.float32)
        return Kx, Ky

    # dynamic kernel
    k = size // 2
    x = np.arange(-k, k+1)
    y = np.arange(-k, k+1)
    xx, yy = np.meshgrid(x, y)

    Kx = xx / (xx**2 + yy**2 + 1e-5)
    Ky = yy / (xx**2 + yy**2 + 1e-5)

    return Kx, Ky

def sobel_edge(img, size=3, weight=1.0, kx_scale=1.0, ky_scale=1.0):
    Kx, Ky = sobel_kernel(size)
    Kx *= kx_scale
    Ky *= ky_scale
    Gx = FilterService._convolve2d(img, Kx)
    Gy = FilterService._convolve2d(img, Ky)

    if kx_scale == 0 and ky_scale == 0:
        result = np.zeros_like(img)
    elif kx_scale == 0:
        result = np.abs(Gy) * weight
    elif ky_scale == 0:
        result = np.abs(Gx) * weight
    else:
        result = np.sqrt(Gx**2 + Gy**2) * weight

    return np.clip(result, 0, 255).astype(np.uint8)

# ===========================
# Prewitt Edge
# ===========================
def prewitt_kernel(size):
    if size == 3:
        Kx = np.array([
            [-1,0,1],
            [-1,0,1],
            [-1,0,1]
        ], dtype=np.float32)

        Ky = np.array([
            [-1,-1,-1],
            [ 0, 0, 0],
            [ 1, 1, 1]
        ], dtype=np.float32)

        return Kx, Ky

    # dynamic
    Kx = np.tile(np.linspace(-1,1,size), (size,1))
    Ky = Kx.T

    Kx = Kx / np.max(np.abs(Kx))
    Ky = Ky / np.max(np.abs(Ky))

    return Kx, Ky
def prewitt_edge(img, size=3, weight=1.0, kx_scale=1.0, ky_scale=1.0):
    Kx, Ky = prewitt_kernel(size)
    Kx *= kx_scale
    Ky *= ky_scale
    Gx = FilterService._convolve2d(img, Kx)
    Gy = FilterService._convolve2d(img, Ky)

    if kx_scale == 0 and ky_scale == 0:
        result = np.zeros_like(img)
    elif kx_scale == 0:
        result = np.abs(Gy) * weight
    elif ky_scale == 0:
        result = np.abs(Gx) * weight
    else:
        result = np.sqrt(Gx**2 + Gy**2) * weight

    return np.clip(result, 0, 255).astype(np.uint8)

# ===========================
# Roberts Edge
# ===========================
def roberts_edge(img, weight=1.0, kx_scale=1.0, ky_scale=1.0):
    Kx = np.array([[1, 0], [0, -1]]) * kx_scale
    Ky = np.array([[0, 1], [-1, 0]]) * ky_scale
    Gx = FilterService._convolve2d(img, Kx)
    Gy = FilterService._convolve2d(img, Ky)

    if kx_scale == 0 and ky_scale == 0:
        result = np.zeros_like(img)
    elif kx_scale == 0:
        result = np.abs(Gy) * weight
    elif ky_scale == 0:
        result = np.abs(Gx) * weight
    else:
        result = np.sqrt(Gx**2 + Gy**2) * weight

    return np.clip(result, 0, 255).astype(np.uint8)

def canny_edge_scaled(img, threshold=100, weight=1.0, kx_scale=1.0, ky_scale=1.0):
    gray = img if len(img.shape) == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = gaussian_blur(gray, 5, 1.0)

    Kx, Ky = sobel_kernel(3)
    Gx = FilterService._convolve2d(blurred, Kx) * kx_scale
    Gy = FilterService._convolve2d(blurred, Ky) * ky_scale
    scaled_img = np.sqrt(Gx**2 + Gy**2) * weight
    scaled_img = np.clip(scaled_img, 0, 255).astype(np.uint8)

    return cv2.Canny(scaled_img, int(0.4*threshold), threshold)

# ===========================
# Edge Service
# ===========================
class EdgeService:

    @staticmethod
    def apply_canny(img, threshold=100, blur_size=5, blur_sigma=1.0, weight=1.0, kx=1.0, ky=1.0):
        if not validate_image(img): return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
        blurred = gaussian_blur(gray, blur_size, blur_sigma)
        return canny_edge_scaled(blurred, threshold, weight, kx, ky)

    @staticmethod
    def apply_sobel(img, kernel_size=3, blur_sigma=1.0, weight=1.0, kx=1.0, ky=1.0):
        if not validate_image(img): return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
        blurred = gaussian_blur(gray, kernel_size, blur_sigma)
        return sobel_edge(blurred, kernel_size, weight, kx, ky)

    @staticmethod
    def apply_prewitt(img, kernel_size=3, blur_sigma=1.0, weight=1.0, kx=1.0, ky=1.0):
        if not validate_image(img): return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
        blurred = gaussian_blur(gray, kernel_size, blur_sigma)
        return prewitt_edge(blurred, kernel_size, weight, kx, ky)

    @staticmethod
    def apply_roberts(img, blur_sigma=1.0, weight=1.0, kx=1.0, ky=1.0):
        if not validate_image(img): return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
        blurred = gaussian_blur(gray, 3, blur_sigma)
        return roberts_edge(blurred, weight, kx, ky)
    

# import numpy as np
# import cv2
# from utils.image_utils import validate_image

# # ===========================
# # Convolution From Scratch
# # ===========================
# def convolve2d(img, kernel):
#     kH, kW = kernel.shape
#     padH, padW = kH // 2, kW // 2
#     padded = np.pad(img, ((padH, padH), (padW, padW)), mode='edge')
#     out = np.zeros_like(img, dtype=np.float32)
#     for i in range(img.shape[0]):
#         for j in range(img.shape[1]):
#             out[i, j] = np.sum(padded[i:i+kH, j:j+kW] * kernel)
#     return out

# # ===========================
# # Gaussian Blur
# # ===========================
# def gaussian_kernel(size=5, sigma=1.0):
#     ax = np.linspace(-(size//2), size//2, size)
#     xx, yy = np.meshgrid(ax, ax)
#     k = np.exp(-(xx**2 + yy**2) / (2*sigma**2))
#     return k / np.sum(k)

# def gaussian_blur(img, size=5, sigma=1.0):
#     return convolve2d(img.astype(np.float32), gaussian_kernel(size, sigma))

# # ===========================
# # Sobel Edge
# # ===========================
# def sobel_kernel(size):
#     if size == 3:
#         Kx = np.array([
#             [-1,0,1],
#             [-2,0,2],
#             [-1,0,1]
#         ], dtype=np.float32)

#         Ky = np.array([
#             [-1,-2,-1],
#             [ 0, 0, 0],
#             [ 1, 2, 1]
#         ], dtype=np.float32)
#         return Kx, Ky

#     # dynamic kernel
#     k = size // 2
#     x = np.arange(-k, k+1)
#     y = np.arange(-k, k+1)
#     xx, yy = np.meshgrid(x, y)

#     Kx = xx / (xx**2 + yy**2 + 1e-5)
#     Ky = yy / (xx**2 + yy**2 + 1e-5)

#     return Kx, Ky

# def sobel_edge(img, size=3, weight=1.0, kx_scale=1.0, ky_scale=1.0):
#     Kx, Ky = sobel_kernel(size)
#     Kx *= kx_scale
#     Ky *= ky_scale
#     Gx = convolve2d(img, Kx)
#     Gy = convolve2d(img, Ky)

#     if kx_scale == 0 and ky_scale == 0:
#         result = np.zeros_like(img)
#     elif kx_scale == 0:
#         result = np.abs(Gy) * weight
#     elif ky_scale == 0:
#         result = np.abs(Gx) * weight
#     else:
#         result = np.sqrt(Gx**2 + Gy**2) * weight

#     return np.clip(result, 0, 255).astype(np.uint8)

# # ===========================
# # Prewitt Edge
# # ===========================
# def prewitt_kernel(size):
#     if size == 3:
#         Kx = np.array([
#             [-1,0,1],
#             [-1,0,1],
#             [-1,0,1]
#         ], dtype=np.float32)

#         Ky = np.array([
#             [-1,-1,-1],
#             [ 0, 0, 0],
#             [ 1, 1, 1]
#         ], dtype=np.float32)

#         return Kx, Ky

#     # dynamic
#     Kx = np.tile(np.linspace(-1,1,size), (size,1))
#     Ky = Kx.T

#     Kx = Kx / np.max(np.abs(Kx))
#     Ky = Ky / np.max(np.abs(Ky))

#     return Kx, Ky
# def prewitt_edge(img, size=3, weight=1.0, kx_scale=1.0, ky_scale=1.0):
#     Kx, Ky = prewitt_kernel(size)
#     Kx *= kx_scale
#     Ky *= ky_scale
#     Gx = convolve2d(img, Kx)
#     Gy = convolve2d(img, Ky)

#     if kx_scale == 0 and ky_scale == 0:
#         result = np.zeros_like(img)
#     elif kx_scale == 0:
#         result = np.abs(Gy) * weight
#     elif ky_scale == 0:
#         result = np.abs(Gx) * weight
#     else:
#         result = np.sqrt(Gx**2 + Gy**2) * weight

#     return np.clip(result, 0, 255).astype(np.uint8)

# # ===========================
# # Roberts Edge
# # ===========================
# def roberts_edge(img, weight=1.0, kx_scale=1.0, ky_scale=1.0):
#     Kx = np.array([[1, 0], [0, -1]]) * kx_scale
#     Ky = np.array([[0, 1], [-1, 0]]) * ky_scale
#     Gx = convolve2d(img, Kx)
#     Gy = convolve2d(img, Ky)

#     if kx_scale == 0 and ky_scale == 0:
#         result = np.zeros_like(img)
#     elif kx_scale == 0:
#         result = np.abs(Gy) * weight
#     elif ky_scale == 0:
#         result = np.abs(Gx) * weight
#     else:
#         result = np.sqrt(Gx**2 + Gy**2) * weight

#     return np.clip(result, 0, 255).astype(np.uint8)

# def canny_edge_scaled(img, threshold=100, weight=1.0, kx_scale=1.0, ky_scale=1.0):
#     gray = img if len(img.shape) == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blurred = gaussian_blur(gray, 5, 1.0)

#     Kx, Ky = sobel_kernel(3)
#     Gx = convolve2d(blurred, Kx) * kx_scale
#     Gy = convolve2d(blurred, Ky) * ky_scale
#     scaled_img = np.sqrt(Gx**2 + Gy**2) * weight
#     scaled_img = np.clip(scaled_img, 0, 255).astype(np.uint8)

#     return cv2.Canny(scaled_img, int(0.4*threshold), threshold)

# # ===========================
# # Edge Service
# # ===========================
# class EdgeService:

#     @staticmethod
#     def apply_canny(img, threshold=100, blur_size=5, blur_sigma=1.0, weight=1.0, kx=1.0, ky=1.0):
#         if not validate_image(img): return None
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
#         blurred = gaussian_blur(gray, blur_size, blur_sigma)
#         return canny_edge_scaled(blurred, threshold, weight, kx, ky)

#     @staticmethod
#     def apply_sobel(img, kernel_size=3, blur_sigma=1.0, weight=1.0, kx=1.0, ky=1.0):
#         if not validate_image(img): return None
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
#         blurred = gaussian_blur(gray, kernel_size, blur_sigma)
#         return sobel_edge(blurred, kernel_size, weight, kx, ky)

#     @staticmethod
#     def apply_prewitt(img, kernel_size=3, blur_sigma=1.0, weight=1.0, kx=1.0, ky=1.0):
#         if not validate_image(img): return None
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
#         blurred = gaussian_blur(gray, kernel_size, blur_sigma)
#         return prewitt_edge(blurred, kernel_size, weight, kx, ky)

#     @staticmethod
#     def apply_roberts(img, blur_sigma=1.0, weight=1.0, kx=1.0, ky=1.0):
#         if not validate_image(img): return None
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
#         blurred = gaussian_blur(gray, 3, blur_sigma)
#         return roberts_edge(blurred, weight, kx, ky)