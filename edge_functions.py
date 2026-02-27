# import numpy as np
# import cv2
#
# def sobel_edge(img, direction='x'):
#     """
#     Sobel edge detection (from scratch)
#     direction: 'x', 'y', or 'both'
#     """
#     # تعريف ماسكات Sobel
#     Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
#     Ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
#
#     img = img.astype(np.float32)
#
#     if direction == 'x':
#         return convolve2d(img, Kx)
#     elif direction == 'y':
#         return convolve2d(img, Ky)
#     elif direction == 'both':
#         Gx = convolve2d(img, Kx)
#         Gy = convolve2d(img, Ky)
#         return np.sqrt(Gx ** 2 + Gy ** 2).astype(np.uint8)
#     else:
#         raise ValueError("direction must be 'x', 'y', or 'both'")
#
#
# def prewitt_edge(img, direction='x'):
#     """
#     Prewitt edge detection (from scratch)
#     """
#     Kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
#     Ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
#
#     img = img.astype(np.float32)
#
#     if direction == 'x':
#         return convolve2d(img, Kx)
#     elif direction == 'y':
#         return convolve2d(img, Ky)
#     elif direction == 'both':
#         Gx = convolve2d(img, Kx)
#         Gy = convolve2d(img, Ky)
#         return np.sqrt(Gx ** 2 + Gy ** 2).astype(np.uint8)
#     else:
#         raise ValueError("direction must be 'x', 'y', or 'both'")
#
#
# def roberts_edge(img, direction='x'):
#     """
#     Roberts edge detection (from scratch)
#     """
#     Kx = np.array([[1, 0], [0, -1]])
#     Ky = np.array([[0, 1], [-1, 0]])
#
#     img = img.astype(np.float32)
#
#     if direction == 'x':
#         return convolve2d(img, Kx)
#     elif direction == 'y':
#         return convolve2d(img, Ky)
#     elif direction == 'both':
#         Gx = convolve2d(img, Kx)
#         Gy = convolve2d(img, Ky)
#         return np.sqrt(Gx ** 2 + Gy ** 2).astype(np.uint8)
#     else:
#         raise ValueError("direction must be 'x', 'y', or 'both'")
#
#
# def canny_edge(img, low_thresh=50, high_thresh=150):
#     """
#     Canny edge detection using OpenCV
#     """
#     edges = cv2.Canny(img, low_thresh, high_thresh)
#     return edges
#
#
# # ===========================
# # دالة Convolution 2D
# # ===========================
# def convolve2d(img, kernel):
#     """
#     Simple 2D convolution from scratch (grayscale)
#     """
#     kH, kW = kernel.shape
#     padH, padW = kH // 2, kW // 2
#     padded = np.pad(img, ((padH, padH), (padW, padW)), mode='edge')
#     output = np.zeros_like(img, dtype=np.float32)
#
#     for i in range(img.shape[0]):
#         for j in range(img.shape[1]):
#             region = padded[i:i + kH, j:j + kW]
#             output[i, j] = np.sum(region * kernel)
#
#     # Clip to 0-255
#     output = np.clip(output, 0, 255).astype(np.uint8)
#     return output
#
#
# # ===========================
# # مثال على الاستخدام
# # ===========================
# if __name__ == "__main__":
#     img = np.load("filter/img1_avg.npy")  # الصورة بعد النويز
#     cv2.imshow("Original", img)
#
#     sobel_x = sobel_edge(img, 'x')
#     sobel_y = sobel_edge(img, 'y')
#     prewitt_x = prewitt_edge(img, 'x')
#     roberts_xy = roberts_edge(img, 'both')
#     canny = canny_edge(img, 50, 150)
#
#     cv2.imshow("Sobel X", sobel_x)
#     cv2.imshow("Sobel Y", sobel_y)
#     cv2.imshow("Prewitt X", prewitt_x)
#     cv2.imshow("Roberts XY", roberts_xy)
#     cv2.imshow("Canny", canny)
#
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()


import numpy as np
import cv2

# ===========================
# Convolution From Scratch
# ===========================
def convolve2d(img, kernel):
    kH, kW = kernel.shape
    padH, padW = kH//2, kW//2
    padded = np.pad(img, ((padH,padH),(padW,padW)), mode='edge')
    output = np.zeros_like(img, dtype=np.float32)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            region = padded[i:i+kH, j:j+kW]
            output[i,j] = np.sum(region * kernel)
    return output

# ===========================
# Gaussian Kernel & Blur From Scratch
# ===========================
def gaussian_kernel(size=5, sigma=1.0):
    ax = np.linspace(-(size//2), size//2, size)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2)/(2*sigma**2))
    kernel = kernel / np.sum(kernel)
    return kernel

def gaussian_blur(img, size=5, sigma=1.0):
    kernel = gaussian_kernel(size, sigma)
    return convolve2d(img.astype(np.float32), kernel)

# ===========================
# Sobel Edge
# ===========================
def sobel_edge(img):
    Kx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
    Ky = np.array([[-1,-2,-1],[0,0,0],[1,2,1]])
    Gx = convolve2d(img, Kx)
    Gy = convolve2d(img, Ky)
    magnitude = np.sqrt(Gx**2 + Gy**2)
    return np.clip(magnitude,0,255).astype(np.uint8)

# ===========================
# Prewitt Edge
# ===========================
def prewitt_edge(img):
    Kx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
    Ky = np.array([[-1,-1,-1],[0,0,0],[1,1,1]])
    Gx = convolve2d(img, Kx)
    Gy = convolve2d(img, Ky)
    magnitude = np.sqrt(Gx**2 + Gy**2)
    return np.clip(magnitude,0,255).astype(np.uint8)

# ===========================
# Roberts Edge
# ===========================
def roberts_edge(img):
    Kx = np.array([[1,0],[0,-1]])
    Ky = np.array([[0,1],[-1,0]])
    Gx = convolve2d(img, Kx)
    Gy = convolve2d(img, Ky)
    magnitude = np.sqrt(Gx**2 + Gy**2)
    return np.clip(magnitude,0,255).astype(np.uint8)

# ===========================
# Canny Edge (OpenCV)
# ===========================
def canny_edge(img, low=50, high=150):
    return cv2.Canny(img.astype(np.uint8), low, high)

# ===========================
# MAIN
# ===========================
if __name__ == "__main__":
    # تحميل الصورة
    # تحميل الصورة
    img = np.load("matrices/img_1.npy").astype(np.float32)

    # Gaussian smoothing (from scratch)
    img_blur = gaussian_blur(img, 5, 1.0)

    # Edge detection
    sobel = sobel_edge(img_blur)
    prewitt = prewitt_edge(img_blur)
    roberts = roberts_edge(img_blur)
    canny = canny_edge(img_blur, 50, 150)

    # عرض كل فلتر في نافذة منفصلة
    cv2.imshow("Sobel Edge", sobel)
    cv2.imshow("Prewitt Edge", prewitt)
    cv2.imshow("Roberts Edge", roberts)
    cv2.imshow("Canny Edge", canny)

    cv2.waitKey(0)
    cv2.destroyAllWindows()