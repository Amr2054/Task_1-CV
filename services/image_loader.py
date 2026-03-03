"""
Image loading and management service
"""
import cv2
import numpy as np
from pathlib import Path


class ImageLoader:
    """Service for loading and managing images"""
    
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self.file_path = None
        self.history = []  # Stack to store previous states
        self.max_history = 20  # Maximum number of undo steps
    
    def load_image(self, file_path):
        """
        Load an image from file path
        
        Args:
            file_path: Path to the image file
            
        Returns:
            tuple: (success: bool, image: numpy.ndarray or None, error_message: str)
        """
        try:
            # Validate file exists
            if not Path(file_path).exists():
                return False, None, "File does not exist"
            
            # Load image using OpenCV
            image = cv2.imread(file_path)
            
            if image is None:
                return False, None, "Failed to load image. Make sure it's a valid image format."
            
            # Auto-detect: if 3D with identical channels, convert to 2D grayscale
            if image.ndim == 3 and image.shape[2] == 3:
                # Check if all channels are the same (true grayscale)
                if np.allclose(image[:,:,0], image[:,:,1]) and np.allclose(image[:,:,1], image[:,:,2]):
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Store the loaded image
            self.original_image = image.copy()
            self.current_image = image.copy()
            self.file_path = file_path
            self.history = []  # Clear history when loading new image
            
            return True, image, ""
            
        except Exception as e:
            return False, None, f"Error loading image: {str(e)}"
    
    def get_original_image(self):
        """Get the original unmodified image"""
        return self.original_image.copy() if self.original_image is not None else None
    
    def get_current_image(self):
        """Get the current processed image"""
        return self.current_image.copy() if self.current_image is not None else None
    
    def update_current_image(self, image):
        """Update the current processed image and save to history"""
        if image is not None:
            # Save current state to history before updating
            if self.current_image is not None:
                self.history.append(self.current_image.copy())
                # Limit history size
                if len(self.history) > self.max_history:
                    self.history.pop(0)
            
            self.current_image = image.copy()
    
    def reset_to_original(self):
        """Reset current image to original"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.history = []  # Clear history on reset
            return True
        return False
    
    def has_image(self):
        """Check if an image is loaded"""
        return self.original_image is not None
    
    def is_image_modified(self):
        """Check if current image is different from original (noise or filter applied)"""
        if self.original_image is None or self.current_image is None:
            return False
        # Compare images to see if they're different
        return not np.array_equal(self.original_image, self.current_image)
    
    def undo(self):
        """Undo the last operation and return the previous image"""
        if not self.can_undo():
            return None
        
        # Get previous state from history
        previous_image = self.history.pop()
        self.current_image = previous_image.copy()
        
        return self.current_image.copy()
    
    def can_undo(self):
        """Check if undo is available"""
        return len(self.history) > 0
