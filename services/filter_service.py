"""
Image filtering service with manual implementations
"""
import cv2
import numpy as np
from utils.image_utils import validate_image


class FilterService:
    """Service for applying different filters to images"""
    
    @staticmethod
    def apply_average_filter(image, kernel_size=5):
        """
        Apply average (mean) filter to smooth an image using manual convolution
        
        Args:
            image: Input image (numpy array)
            kernel_size: Size of the averaging kernel (must be odd)
            
        Returns:
            Filtered image
        """
        if not validate_image(image):
            return None
        
        # Ensure kernel size is odd and at least 3
        ksize = max(3, kernel_size)
        if ksize % 2 == 0:
            ksize += 1
        
        pad = ksize // 2
        
        if image.ndim == 2:  # Grayscale
            padded = np.pad(image, pad, mode='edge')
            output = np.zeros_like(image)

            for i in range(image.shape[0]):
                for j in range(image.shape[1]):
                    region = padded[i:i+ksize, j:j+ksize]
                    output[i, j] = np.mean(region)

        else:  # Color image
            output = np.zeros_like(image)
            for c in range(image.shape[2]):
                padded = np.pad(image[:, :, c], pad, mode='edge')
                for i in range(image.shape[0]):
                    for j in range(image.shape[1]):
                        region = padded[i:i+ksize, j:j+ksize]
                        output[i, j, c] = np.mean(region)

        return output.astype(np.uint8)
    
    @staticmethod
    def _gaussian_kernel(ksize=5, sigma=1):
        """
        Generate a Gaussian kernel
        
        Args:
            ksize: Kernel size
            sigma: Standard deviation
            
        Returns:
            Gaussian kernel matrix
        """
        ax = np.linspace(-(ksize//2), ksize//2, ksize)
        xx, yy = np.meshgrid(ax, ax)
        kernel = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
        kernel = kernel / np.sum(kernel)
        return kernel
    
    @staticmethod
    def apply_gaussian_filter(image, kernel_size=5, sigma=1):
        """
        Apply Gaussian filter for smoothing with manual convolution
        
        Args:
            image: Input image (numpy array)
            kernel_size: Size of the Gaussian kernel (must be odd)
            sigma: Standard deviation (default: 1)
            
        Returns:
            Filtered image
        """
        if not validate_image(image):
            return None
        
        # Ensure kernel size is odd and at least 3
        ksize = max(3, kernel_size)
        if ksize % 2 == 0:
            ksize += 1
        
        # Generate Gaussian kernel
        kernel = FilterService._gaussian_kernel(ksize, sigma)
        pad = ksize // 2

        if image.ndim == 2:  # Grayscale
            padded = np.pad(image, pad, mode='edge')
            output = np.zeros_like(image)

            for i in range(image.shape[0]):
                for j in range(image.shape[1]):
                    region = padded[i:i+ksize, j:j+ksize]
                    output[i, j] = np.sum(region * kernel)

        else:  # Color
            output = np.zeros_like(image)
            for c in range(image.shape[2]):
                padded = np.pad(image[:, :, c], pad, mode='edge')
                for i in range(image.shape[0]):
                    for j in range(image.shape[1]):
                        region = padded[i:i+ksize, j:j+ksize]
                        output[i, j, c] = np.sum(region * kernel)

        return np.clip(output, 0, 255).astype(np.uint8)
    
    @staticmethod
    def apply_median_filter(image, kernel_size=5):
        """
        Apply median filter, excellent for removing salt and pepper noise
        Manual implementation with loop
        
        Args:
            image: Input image (numpy array)
            kernel_size: Size of the median kernel (must be odd)
            
        Returns:
            Filtered image
        """
        if not validate_image(image):
            return None
        
        # Ensure kernel size is odd and at least 3
        ksize = max(3, kernel_size)
        if ksize % 2 == 0:
            ksize += 1
        
        pad = ksize // 2

        if image.ndim == 2:  # Grayscale
            padded = np.pad(image, pad, mode='edge')
            output = np.zeros_like(image)

            for i in range(image.shape[0]):
                for j in range(image.shape[1]):
                    region = padded[i:i+ksize, j:j+ksize]
                    output[i, j] = np.median(region)

        else:  # Color
            output = np.zeros_like(image)
            for c in range(image.shape[2]):
                padded = np.pad(image[:, :, c], pad, mode='edge')
                for i in range(image.shape[0]):
                    for j in range(image.shape[1]):
                        region = padded[i:i+ksize, j:j+ksize]
                        output[i, j, c] = np.median(region)

        return output.astype(np.uint8)
