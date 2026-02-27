"""
Noise generation and application service
"""
import cv2
import numpy as np
from utils.image_utils import ensure_uint8, validate_image


class NoiseService:
    """Service for applying different types of noise to images"""
    
    @staticmethod
    def apply_uniform_noise(image, intensity=30):
        """
        Apply uniform noise to an image
        
        Args:
            image: Input image (numpy array, grayscale or color)
            intensity: Noise range (0-100), controls low=-intensity, high=+intensity
            
        Returns:
            Image with uniform noise applied
        """
        if not validate_image(image):
            return None
        
        # Convert to float32 for accurate addition
        noisy = image.astype(np.float32)
        
        # Generate uniform noise in range [-intensity, +intensity]
        low = -intensity
        high = intensity
        uni = np.random.uniform(low, high, image.shape)
        noisy += uni
        
        # Clip values to valid range and convert back to uint8
        noisy = np.clip(noisy, 0, 255).astype(np.uint8)
        
        return noisy
    
    @staticmethod
    def apply_salt_pepper_noise(image, amount=5):
        """
        Apply salt and pepper noise to an image
        
        Args:
            image: Input image (numpy array, grayscale or color)
            amount: Percentage of pixels to affect (0-100), half salt, half pepper
            
        Returns:
            Image with salt and pepper noise applied
        """
        if not validate_image(image):
            return None
        
        noisy = image.copy().astype(np.float32)
        
        # Convert amount to probability (0-1)
        amount_normalized = amount / 100.0
        
        # Calculate number of pixels to be affected
        num_pixels = int(amount_normalized * image.shape[0] * image.shape[1])
        
        # Generate random coordinates
        y_coords = np.random.randint(0, image.shape[0], num_pixels)
        x_coords = np.random.randint(0, image.shape[1], num_pixels)
        
        # Create mask for salt (50% of pixels) vs pepper (50% of pixels)
        salt_mask = np.random.rand(num_pixels) < 0.5
        
        # Apply salt (white = 255) and pepper (black = 0)
        if image.ndim == 2:  # Grayscale
            noisy[y_coords[salt_mask], x_coords[salt_mask]] = 255
            noisy[y_coords[~salt_mask], x_coords[~salt_mask]] = 0
        else:  # Color image
            noisy[y_coords[salt_mask], x_coords[salt_mask], :] = 255
            noisy[y_coords[~salt_mask], x_coords[~salt_mask], :] = 0
        
        # Clip and convert back to uint8
        noisy = np.clip(noisy, 0, 255).astype(np.uint8)
        
        return noisy
    
    @staticmethod
    def apply_gaussian_noise(image, mean=0, sigma=10):
        """
        Apply Gaussian noise to an image
        
        Args:
            image: Input image (numpy array, grayscale or color)
            mean: Mean of the Gaussian distribution (default 0)
            sigma: Standard deviation (0-100), controls noise strength
            
        Returns:
            Image with Gaussian noise applied
        """
        if not validate_image(image):
            return None
        
        # Convert to float32 for accurate addition
        noisy = image.astype(np.float32)
        
        # Generate Gaussian noise with specified mean and sigma
        gauss = np.random.normal(mean, sigma, image.shape)
        noisy += gauss
        
        # Clip values to valid range and convert back to uint8
        noisy = np.clip(noisy, 0, 255).astype(np.uint8)
        
        return noisy
