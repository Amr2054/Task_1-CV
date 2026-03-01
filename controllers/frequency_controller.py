"""
Frequency domain filter controller
"""
import cv2
from PyQt5.QtWidgets import QFileDialog
from services.frequency_service import FrequencyService
from utils.image_utils import cv_to_qpixmap, scale_pixmap


class FrequencyController:
    
    # Default cutoff values
    DEFAULT_CUTOFF = 30

    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.freq_service = FrequencyService()
        self._img1 = None  # image for low pass
        self._img2 = None  # image for high pass
        self._connect_signals()
        self._initialize_controls()
    
    def _initialize_controls(self):
        """Initialize all controls to default state"""
        mc = self.main_controller
        if hasattr(mc, 'sliderLowPassCutoff'):
            mc.sliderLowPassCutoff.setValue(self.DEFAULT_CUTOFF)
            mc.labelLowCutoffVal.setText(str(self.DEFAULT_CUTOFF))
        if hasattr(mc, 'sliderHighPassCutoff'):
            mc.sliderHighPassCutoff.setValue(self.DEFAULT_CUTOFF)
            mc.labelHighCutoffVal.setText(str(self.DEFAULT_CUTOFF))

    def _connect_signals(self):
        mc = self.main_controller
        mc.sliderLowPassCutoff.valueChanged.connect(self._on_low_cutoff_changed)
        mc.sliderHighPassCutoff.valueChanged.connect(self._on_high_cutoff_changed)
        mc.btnUploadLowPass.clicked.connect(self._upload_low_pass_image)
        mc.btnUploadHighPass.clicked.connect(self._upload_high_pass_image)
        mc.btnGenerateHybrid.clicked.connect(self._generate_hybrid)
    
    def reset_frequency_controls(self):
        """Reset all frequency domain controls to initial state"""
        mc = self.main_controller
        
        # Clear images
        self._img1 = None
        self._img2 = None
        
        # Reset to default values (reuse initialization)
        self._initialize_controls()
        
        # Clear image displays
        if hasattr(mc, 'imgFreqLowPass'):
            mc.imgFreqLowPass.clear()
            mc.imgFreqLowPass.setText("Upload image to apply Low Pass")
        if hasattr(mc, 'imgFreqHighPass'):
            mc.imgFreqHighPass.clear()
            mc.imgFreqHighPass.setText("Upload image to apply High Pass")
        if hasattr(mc, 'imgFreqHybrid'):
            mc.imgFreqHybrid.clear()
            mc.imgFreqHybrid.setText("Hybrid image will appear here")

    def _on_low_cutoff_changed(self):
        mc = self.main_controller
        mc.labelLowCutoffVal.setText(f"{mc.sliderLowPassCutoff.value()}")
        if self._img1 is not None:
            self._apply_low_pass()

    def _on_high_cutoff_changed(self):
        mc = self.main_controller
        mc.labelHighCutoffVal.setText(f"{mc.sliderHighPassCutoff.value()}")
        if self._img2 is not None:
            self._apply_high_pass()

    def _upload_low_pass_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self.main_controller, "Select Image for Low Pass", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            return
        self._img1 = img
        self._apply_low_pass()

    def _upload_high_pass_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self.main_controller, "Select Image for High Pass", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            return
        self._img2 = img
        self._apply_high_pass()

    def _apply_low_pass(self):
        cutoff = self.main_controller.sliderLowPassCutoff.value()
        low = self.freq_service.apply_low_pass(self._img1, cutoff)
        if low is not None:
            self._show_in_label(low, self.main_controller.imgFreqLowPass)

    def _apply_high_pass(self):
        cutoff = self.main_controller.sliderHighPassCutoff.value()
        high = self.freq_service.apply_high_pass(self._img2, cutoff)
        if high is not None:
            self._show_in_label(high, self.main_controller.imgFreqHighPass)

    def _generate_hybrid(self):
        mc = self.main_controller
        if self._img1 is None or self._img2 is None:
            mc.show_warning("Please upload both images first.", "Missing Images")
            return

        cutoff_low = mc.sliderLowPassCutoff.value()
        cutoff_high = mc.sliderHighPassCutoff.value()

        low = self.freq_service.apply_low_pass(self._img1, cutoff_low)
        high = self.freq_service.apply_high_pass(self._img2, cutoff_high)

        if low is None or high is None:
            return

        # Resize high to match low if needed
        import numpy as np
        if low.shape != high.shape:
            high = cv2.resize(high, (low.shape[1], low.shape[0]))

        hybrid = np.clip(low.astype(np.float32) + high.astype(np.float32), 0, 255).astype(np.uint8)
        self._show_in_label(hybrid, mc.imgFreqHybrid)
        
        # Update image loader for undo support
        mc.image_loader.update_current_image(hybrid)
        mc._update_undo_button_state()

    def _show_in_label(self, img, label):
        pixmap = cv_to_qpixmap(img)
        scaled = scale_pixmap(pixmap, label.width() - 10, label.height() - 10)
        label.setPixmap(scaled)