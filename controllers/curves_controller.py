"""
Histogram controller for managing histogram equalization and distribution
"""
import cv2
from PyQt5.QtWidgets import QMessageBox
from services.curves_service import (
    histogram_equalization,
    get_distribution_as_image,
    to_grayscale
)
from utils.image_utils import qpixmap_to_cv, cv_to_qpixmap


class HistogramController:
    """
    Controller for managing histogram operations and displaying distributions
    """
    
    def __init__(self, main_controller):
        """
        Initialize histogram controller
        
        Args:
            main_controller: Reference to the main controller
        """
        self.main_controller = main_controller
        self.equalized_image = None
        self.grayscale_image = None
        self._connect_signals()
        self._initialize_controls()
    
    def _initialize_controls(self):
        """Initialize all controls to default state"""
        if hasattr(self.main_controller, 'comboHistChannel'):
            self.main_controller.comboHistChannel.setCurrentIndex(0)
    
    def _connect_signals(self):
        """Connect histogram-related signals to slots"""
        mc = self.main_controller
        if hasattr(mc, 'btnShowHist'):
            mc.btnShowHist.clicked.connect(self._show_histogram)
        if hasattr(mc, 'btnShowDistribution'):
            mc.btnShowDistribution.clicked.connect(self._show_distribution_curve)
        if hasattr(mc, 'btnEqualize'):
            mc.btnEqualize.clicked.connect(self._apply_histogram_equalization)
        if hasattr(mc, 'btnNormalize'):
            mc.btnNormalize.clicked.connect(self._apply_normalize)
        if hasattr(mc, 'btnGrayscale'):
            mc.btnGrayscale.clicked.connect(self._apply_grayscale)
    
    def reset_histogram_controls(self):
        """Reset all histogram controls to initial state"""
        self.equalized_image = None
        self.grayscale_image = None
        # Reset to default values (reuse initialization)
        self._initialize_controls()
    
    def _get_selected_image(self, combo_attr='comboHistChannel', default_title="Image"):
        """
        Get the selected image based on combo box selection
        
        Returns:
            tuple: (cv_image, title) or (None, None) if error
        """
        combo = getattr(self.main_controller, combo_attr, None)
        if not combo:
            return None, None
        
        selected = combo.currentText()
        
        if selected == "Equalized Image":
            if self.equalized_image is None:
                self.main_controller.show_error("Please apply equalization first")
                return None, None
            return self.equalized_image.copy(), f"{default_title} (Equalized)"
        
        elif selected == "Grayscale Image":
            if self.grayscale_image is None:
                self.main_controller.show_error("Please apply grayscale first")
                return None, None
            return self.grayscale_image.copy(), f"{default_title} (Grayscale)"
        
        else:  # Original image
            cv_image = qpixmap_to_cv(self.main_controller.original_pixmap)
            return cv_image, f"{default_title} (Original)"
    
    def _display_result(self, cv_image):
        """Display result image in output"""
        self.main_controller.output_pixmap = cv_to_qpixmap(cv_image)
        self.main_controller._display_output_image(cv_image)

    def _show_histogram(self):
        """Show histogram distribution"""
        if not self.main_controller.validate_image_loaded():
            return
        
        try:
            cv_image, title = self._get_selected_image('comboHistChannel', 'Histogram')
            if cv_image is None:
                return
            
            hist_image = get_distribution_as_image(cv_image, mode="hist", title=title)
            self._display_result(hist_image)
            
        except Exception as e:
            self.main_controller.show_error(f"Failed to show histogram: {str(e)}")
    
    def _show_distribution_curve(self):
        """Show distribution curve (PDF or CDF)"""
        if not self.main_controller.validate_image_loaded():
            return
        
        try:
            combo_attr = 'comboCurveChannel' if hasattr(self.main_controller, 'comboCurveChannel') else 'comboHistChannel'
            cv_image, title = self._get_selected_image(combo_attr, 'Distribution Curve')
            if cv_image is None:
                return
            
            # Get curve type (PDF or CDF)
            curve_combo = getattr(self.main_controller, 'comboCurveType', None)
            if curve_combo:
                mode = "pdf" if curve_combo.currentText().upper() == "PDF" else "cdf"
            else:
                mode = "cdf"
            
            title = f"{title} ({mode.upper()})"
            dist_image = get_distribution_as_image(cv_image, mode=mode, title=title)
            self._display_result(dist_image)
            
        except Exception as e:
            self.main_controller.show_error(f"Failed to show distribution curve: {str(e)}")

    def _apply_histogram_equalization(self):
        """Apply histogram equalization to the current image"""
        if not self.main_controller.validate_image_loaded():
            return

        try:
            cv_image = qpixmap_to_cv(self.main_controller.original_pixmap)
            equalized = histogram_equalization(cv_image)
            
            self.equalized_image = equalized.copy()
            self.main_controller.image_loader.update_current_image(equalized)
            self._display_result(equalized)
            self.main_controller._update_undo_button_state()

        except Exception as e:
            self.main_controller.show_error(f"Failed to apply equalization: {str(e)}")

    def _apply_normalize(self):
        """Apply normalization to the current image"""
        if not self.main_controller.validate_image_loaded():
            return

        try:
            cv_image = qpixmap_to_cv(self.main_controller.original_pixmap)
            normalized = cv2.normalize(cv_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            
            self.main_controller.image_loader.update_current_image(normalized)
            self._display_result(normalized)
            self.main_controller._update_undo_button_state()

        except Exception as e:
            self.main_controller.show_error(f"Failed to apply normalization: {str(e)}")

    def _apply_grayscale(self):
        """Convert current image to grayscale"""
        if not self.main_controller.validate_image_loaded():
            return

        try:
            cv_image = qpixmap_to_cv(self.main_controller.original_pixmap)
            gray_image = to_grayscale(cv_image)
            
            self.grayscale_image = gray_image.copy()
            self.main_controller.image_loader.update_current_image(gray_image)
            self._display_result(gray_image)
            self.main_controller._update_undo_button_state()

        except Exception as e:
            self.main_controller.show_error(f"Failed to convert to grayscale: {str(e)}")

    