import numpy as np
from utils.image_utils import validate_image


class FilterService:
    """Service for applying different filters to images"""

    # =========================================================
    # Core Convolution Engine (Vectorized - From Scratch)
    # =========================================================
    @staticmethod
    def _convolve2d(img, kernel):
        kH, kW = kernel.shape
        padH, padW = kH // 2, kW // 2

        img = img.astype(np.float32)

        padded = np.pad(
            img,
            ((padH, padH), (padW, padW)),
            mode='edge'
        )

        shape = (img.shape[0], img.shape[1], kH, kW)
        strides = (
            padded.strides[0],
            padded.strides[1],
            padded.strides[0],
            padded.strides[1]
        )

        windows = np.lib.stride_tricks.as_strided(
            padded,
            shape=shape,
            strides=strides
        )

        return np.einsum('ijkl,kl->ij', windows, kernel)

    # =========================================================
    # Average Filter
    # =========================================================
    @staticmethod
    def apply_average_filter(image, kernel_size=5):

        if not validate_image(image):
            return None

        ksize = max(3, kernel_size)
        # if ksize % 2 == 0:
        #     ksize += 1

        kernel = np.ones((ksize, ksize), dtype=np.float32)
        kernel /= (ksize * ksize)

        if image.ndim == 2:
            output = FilterService._convolve2d(image, kernel)
        else:
            channels = []
            for c in range(image.shape[2]):
                filtered = FilterService._convolve2d(image[:, :, c], kernel)
                channels.append(filtered)
            output = np.stack(channels, axis=2)

        return np.clip(output, 0, 255).astype(np.uint8)

    # =========================================================
    # Gaussian Kernel Generator
    # =========================================================
    @staticmethod
    def _gaussian_kernel(ksize=5, sigma=1):
        ax = np.linspace(-(ksize // 2), ksize // 2, ksize)
        xx, yy = np.meshgrid(ax, ax)
        kernel = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
        kernel /= np.sum(kernel)
        return kernel.astype(np.float32)

    # =========================================================
    # Gaussian Filter
    # =========================================================
    @staticmethod
    def apply_gaussian_filter(image, kernel_size=5, sigma=1):

        if not validate_image(image):
            return None

        ksize = max(3, kernel_size)
        # if ksize % 2 == 0:
        #     ksize += 1

        kernel = FilterService._gaussian_kernel(ksize, sigma)

        if image.ndim == 2:
            output = FilterService._convolve2d(image, kernel)
        else:
            channels = []
            for c in range(image.shape[2]):
                filtered = FilterService._convolve2d(image[:, :, c], kernel)
                channels.append(filtered)
            output = np.stack(channels, axis=2)

        return np.clip(output, 0, 255).astype(np.uint8)

    # =========================================================
    # Median Filter (Vectorized without loops)
    # =========================================================
    @staticmethod
    def apply_median_filter(image, kernel_size=5):

        if not validate_image(image):
            return None

        ksize = max(3, kernel_size)
        # if ksize % 2 == 0:
        #     ksize += 1

        pad = ksize // 2

        def median_channel(channel):
            channel = channel.astype(np.float32)

            padded = np.pad(channel, pad, mode='edge')

            shape = (channel.shape[0], channel.shape[1], ksize, ksize)
            strides = (
                padded.strides[0],
                padded.strides[1],
                padded.strides[0],
                padded.strides[1]
            )

            windows = np.lib.stride_tricks.as_strided(
                padded,
                shape=shape,
                strides=strides
            )

            return np.median(windows, axis=(2, 3))

        if image.ndim == 2:
            output = median_channel(image)
        else:
            channels = []
            for c in range(image.shape[2]):
                channels.append(median_channel(image[:, :, c]))
            output = np.stack(channels, axis=2)

        return np.clip(output, 0, 255).astype(np.uint8)

# import cv2
# import numpy as np
# from utils.image_utils import validate_image


# class FilterService:
#     """Service for applying different filters to images"""
    
#     @staticmethod
#     def apply_average_filter(image, kernel_size=5):

#         if not validate_image(image):
#             return None
        
#         # Ensure kernel size is odd and at least 3
#         ksize = max(3, kernel_size)
#         if ksize % 2 == 0:
#             ksize += 1
        
#         pad = ksize // 2
        
#         if image.ndim == 2:  # Grayscale
#             padded = np.pad(image, pad, mode='edge')
#             output = np.zeros_like(image)

#             for i in range(image.shape[0]):
#                 for j in range(image.shape[1]):
#                     region = padded[i:i+ksize, j:j+ksize]
#                     output[i, j] = np.mean(region)

#         else:  # Color image
#             output = np.zeros_like(image)
#             for c in range(image.shape[2]):
#                 padded = np.pad(image[:, :, c], pad, mode='edge')
#                 for i in range(image.shape[0]):
#                     for j in range(image.shape[1]):
#                         region = padded[i:i+ksize, j:j+ksize]
#                         output[i, j, c] = np.mean(region)

#         return output.astype(np.uint8)
    
#     @staticmethod
#     def _gaussian_kernel(ksize=5, sigma=1):
#         """  Generate a Gaussian kernel """
#         ax = np.linspace(-(ksize//2), ksize//2, ksize)
#         xx, yy = np.meshgrid(ax, ax)
#         kernel = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
#         kernel = kernel / np.sum(kernel)
#         return kernel
    

#     @staticmethod
#     def apply_gaussian_filter(image, kernel_size=5, sigma=1):
   
#         if not validate_image(image):
#             return None
        
#         # Ensure kernel size is odd and at least 3
#         ksize = max(3, kernel_size)
#         if ksize % 2 == 0:
#             ksize += 1
        
#         # Generate Gaussian kernel
#         kernel = FilterService._gaussian_kernel(ksize, sigma)
#         pad = ksize // 2

#         if image.ndim == 2:  # Grayscale
#             padded = np.pad(image, pad, mode='edge')
#             output = np.zeros_like(image)

#             for i in range(image.shape[0]):
#                 for j in range(image.shape[1]):
#                     region = padded[i:i+ksize, j:j+ksize]
#                     output[i, j] = np.sum(region * kernel)

#         else:  # Color
#             output = np.zeros_like(image)
#             for c in range(image.shape[2]):
#                 padded = np.pad(image[:, :, c], pad, mode='edge')
#                 for i in range(image.shape[0]):
#                     for j in range(image.shape[1]):
#                         region = padded[i:i+ksize, j:j+ksize]
#                         output[i, j, c] = np.sum(region * kernel)

#         return np.clip(output, 0, 255).astype(np.uint8)
    
#     @staticmethod
#     def apply_median_filter(image, kernel_size=5):
 
#         if not validate_image(image):
#             return None
        
#         # Ensure kernel size is odd and at least 3
#         ksize = max(3, kernel_size)
#         if ksize % 2 == 0:
#             ksize += 1
        
#         pad = ksize // 2

#         if image.ndim == 2:  # Grayscale
#             padded = np.pad(image, pad, mode='edge')
#             output = np.zeros_like(image)

#             for i in range(image.shape[0]):
#                 for j in range(image.shape[1]):
#                     region = padded[i:i+ksize, j:j+ksize]
#                     output[i, j] = np.median(region)

#         else:  # Color
#             output = np.zeros_like(image)
#             for c in range(image.shape[2]):
#                 padded = np.pad(image[:, :, c], pad, mode='edge')
#                 for i in range(image.shape[0]):
#                     for j in range(image.shape[1]):
#                         region = padded[i:i+ksize, j:j+ksize]
#                         output[i, j, c] = np.median(region)

#         return output.astype(np.uint8)
