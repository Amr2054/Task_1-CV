"""
Frequency domain filter controller
"""
import cv2
from PyQt5.QtWidgets import QFileDialog
from services.frequency_service import FrequencyService
from utils.image_utils import cv_to_qpixmap, scale_pixmap


class FrequencyController:

    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.freq_service = FrequencyService()
        self._img1 = None  # image for low pass
        self._img2 = None  # image for high pass
        self._connect_signals()

    def _connect_signals(self):
        mc = self.main_controller
        mc.sliderLowPassCutoff.valueChanged.connect(self._on_low_cutoff_changed)
        mc.sliderHighPassCutoff.valueChanged.connect(self._on_high_cutoff_changed)
        mc.btnUploadLowPass.clicked.connect(self._upload_low_pass_image)
        mc.btnUploadHighPass.clicked.connect(self._upload_high_pass_image)
        mc.btnGenerateHybrid.clicked.connect(self._generate_hybrid)

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
            mc.show_message(mc, 'warning', "Missing Images",
                            "Please upload both images first.")
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

    def _show_in_label(self, img, label):
        pixmap = cv_to_qpixmap(img)
        scaled = scale_pixmap(pixmap, label.width() - 10, label.height() - 10)
        label.setPixmap(scaled)