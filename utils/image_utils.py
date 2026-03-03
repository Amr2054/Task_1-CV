"""
Image utility functions for common operations
"""
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt


def cv_to_qpixmap(cv_image):
    """
    Convert OpenCV image (BGR) to QPixmap for display in PyQt5
    """
    if cv_image is None:
        return QPixmap()
    
    # Handle grayscale images
    if len(cv_image.shape) == 2:
        height, width = cv_image.shape
        bytes_per_line = width
        q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
    else:
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_image.shape
        bytes_per_line = channels * width
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
    
    return QPixmap.fromImage(q_image)


def qpixmap_to_cv(qpixmap):
    """
    Convert QPixmap to OpenCV image (BGR)
    
    Args:
        qpixmap: QPixmap object
        
    Returns:
        OpenCV image in BGR format (numpy array)
    """
    if qpixmap.isNull():
        return None
    
    # Convert QPixmap to QImage
    q_image = qpixmap.toImage()
    
    # Get image dimensions
    width = q_image.width()
    height = q_image.height()
    
    # Convert QImage to numpy array
    ptr = q_image.bits()
    ptr.setsize(q_image.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  # RGBA format
    
    # Convert RGBA to BGR
    bgr_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    
    return bgr_image


def scale_pixmap(pixmap, label_width, label_height):
    """
    Scale pixmap to fit within label dimensions while maintaining aspect ratio
    """
    if pixmap.isNull():
        return pixmap
    
    return pixmap.scaled(
        label_width, 
        label_height, 
        Qt.KeepAspectRatio, 
        Qt.SmoothTransformation
    )


def validate_image(image):
    """
    Validate that image is a valid numpy array
    """
    return isinstance(image, np.ndarray) and image.size > 0


def ensure_uint8(image):

    if image.dtype != np.uint8:
        # Normalize to 0-255 range
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
        image = image.astype(np.uint8)
    return image
