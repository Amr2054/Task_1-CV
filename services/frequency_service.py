"""
Frequency domain filtering service using FFT
"""
import numpy as np
import cv2
from utils.image_utils import validate_image


def _make_low_pass_mask(shape, cutoff):
    rows, cols = shape
    crow, ccol = rows // 2, cols // 2
    Y, X = np.ogrid[:rows, :cols]
    dist = np.sqrt((Y - crow) ** 2 + (X - ccol) ** 2)
    return (dist <= cutoff).astype(np.float32)


def _make_high_pass_mask(shape, cutoff):
    return 1.0 - _make_low_pass_mask(shape, cutoff)


def _apply_fft_filter(gray, mask):
    f = np.fft.fft2(gray.astype(np.float32))
    fshift = np.fft.fftshift(f)
    filtered = fshift * mask
    f_ishift = np.fft.ifftshift(filtered)
    img_back = np.fft.ifft2(f_ishift)
    return np.clip(np.abs(img_back), 0, 255).astype(np.uint8)


def _process_image(image, mask_fn, cutoff):
    if image.ndim == 3:
        channels = [_apply_fft_filter(image[:, :, c], mask_fn(image[:, :, c].shape, cutoff)) for c in range(image.shape[2])]
        return cv2.merge(channels)
    return _apply_fft_filter(image, mask_fn(image.shape, cutoff))


class FrequencyService:

    @staticmethod
    def apply_filters(image, cutoff_low=30, cutoff_high=30):
        """Returns (low_pass_result, high_pass_result, hybrid_result)"""
        if not validate_image(image):
            return None, None, None

        low = _process_image(image, _make_low_pass_mask, cutoff_low)
        high = _process_image(image, _make_high_pass_mask, cutoff_high)

        # Hybrid: sum low and high, normalized
        hybrid = np.clip(low.astype(np.float32) + high.astype(np.float32), 0, 255).astype(np.uint8)

        return low, high, hybrid
    
    @staticmethod
    def apply_low_pass(image, cutoff=30):
        if not validate_image(image):
            return None
        return _process_image(image, _make_low_pass_mask, cutoff)

    @staticmethod
    def apply_high_pass(image, cutoff=30):
        if not validate_image(image):
            return None
        return _process_image(image, _make_high_pass_mask, cutoff)