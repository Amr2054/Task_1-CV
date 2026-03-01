"""
Histogram controller for managing histogram equalization and distribution
"""
from PyQt5.QtWidgets import QMessageBox
from services.curves_service import (
    compute_histogram_stats, 
    draw_distribution, 
    histogram_equalization,
    get_distribution_as_image,
    to_grayscale
)


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
        self.equalized_image = None  # Cache for equalized image
        
        # Connect signals
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect histogram-related signals to slots"""
        # Show Histogram button
        if hasattr(self.main_controller, 'btnShowHist'):
            self.main_controller.btnShowHist.clicked.connect(self._show_histogram)
        
        # Show Distribution Curve button
        if hasattr(self.main_controller, 'btnShowDistribution'):
            self.main_controller.btnShowDistribution.clicked.connect(self._show_distribution_curve)
        
        # Equalize button
        if hasattr(self.main_controller, 'btnEqualize'):
            self.main_controller.btnEqualize.clicked.connect(self._apply_histogram_equalization)
        
        # Normalize button
        if hasattr(self.main_controller, 'btnNormalize'):
            self.main_controller.btnNormalize.clicked.connect(self._apply_normalize)

        # Grayscale button
        if hasattr(self.main_controller, 'btnGrayscale'):
            self.main_controller.btnGrayscale.clicked.connect(self._apply_grayscale)

    def _show_histogram(self):
        """Show histogram distribution"""
        if self.main_controller.original_pixmap is None:
            self.main_controller.show_message(self.main_controller, 'warning', "Error", "Please load an image first")
            return
        
        try:
            from utils.image_utils import qpixmap_to_cv, cv_to_qpixmap
            
            # Get selected image type from combo box
            combo = self.main_controller.comboHistChannel if hasattr(self.main_controller, 'comboHistChannel') else None
            if combo is None:
                self.main_controller.show_message(self.main_controller, 'warning', "Error", "Histogram selector not found")
                return
                
            selected_type = combo.currentText()
            
            if selected_type == "Equalized Image":
                # Use equalized image if available
                if self.equalized_image is None:
                    self.main_controller.show_message(self.main_controller, 'warning', "Error",
                                                      "Please apply equalization first")
                    return
                cv_image = self.equalized_image.copy()
                title = "Histogram (Equalized)"
            elif selected_type == "Grayscale Image":
                # Use grayscale image if available
                if getattr(self, 'grayscale_image', None) is None:
                    self.main_controller.show_message(self.main_controller, 'warning', "Error",
                                                      "Please apply grayscale first")
                    return
                cv_image = self.grayscale_image.copy()
                title = "Histogram (Grayscale)"
            else:
                # Use original image
                cv_image = qpixmap_to_cv(self.main_controller.original_pixmap)
                title = "Image Histogram (Original)"

            # Get histogram as image
            hist_image = get_distribution_as_image(cv_image, mode="hist", title=title)
            
            # Display in output
            self.main_controller.output_pixmap = cv_to_qpixmap(hist_image)
            self.main_controller._display_output_image(hist_image)
            
        except Exception as e:
            self.main_controller.show_message(self.main_controller, 'error', "Error", f"Failed to show histogram: {str(e)}")
    
    def _show_distribution_curve(self):
        """Show distribution curve (PDF or CDF)"""
        if self.main_controller.original_pixmap is None:
            self.main_controller.show_message(self.main_controller, 'warning', "Error", "Please load an image first")
            return
        
        try:
            from utils.image_utils import qpixmap_to_cv, cv_to_qpixmap
            
            # Get selected image type from combo box (use comboCurveChannel for distribution curve)
            combo = self.main_controller.comboCurveChannel if hasattr(self.main_controller, 'comboCurveChannel') else self.main_controller.comboHistChannel
            selected_type = combo.currentText()
            
            if selected_type == "Equalized Image":
                # Use equalized image if available
                if self.equalized_image is None:
                    self.main_controller.show_message(self.main_controller, 'warning', "Error",
                                                      "Please apply equalization first")
                    return
                cv_image = self.equalized_image.copy()
                title = "Distribution Curve (Equalized)"
            elif selected_type == "Grayscale Image":
                # Use grayscale image if available
                if getattr(self, 'grayscale_image', None) is None:
                    self.main_controller.show_message(self.main_controller, 'warning', "Error",
                                                      "Please apply grayscale first")
                    return
                cv_image = self.grayscale_image.copy()
                title = "Distribution Curve (Grayscale)"
            else:
                # Use original image
                cv_image = qpixmap_to_cv(self.main_controller.original_pixmap)
                title = "Distribution Curve (Original)"

            # Get selected curve type (PDF or CDF) from combo box
            curve_type_combo = self.main_controller.comboCurveType if hasattr(self.main_controller, 'comboCurveType') else None
            if curve_type_combo is None:
                mode = "cdf"  # Default to CDF if combo box not found
            else:
                selected_curve_type = curve_type_combo.currentText().upper()
                mode = "pdf" if selected_curve_type == "PDF" else "cdf"

            # Add mode info to title
            title = f"{title} ({mode.upper()})"

            # Get distribution curve as image
            dist_image = get_distribution_as_image(cv_image, mode=mode, title=title)

            # Display in output
            self.main_controller.output_pixmap = cv_to_qpixmap(dist_image)
            self.main_controller._display_output_image(dist_image)

        except Exception as e:
            self.main_controller.show_message(self.main_controller, 'error', "Error", f"Failed to show distribution curve: {str(e)}")

    def _apply_histogram_equalization(self):
        """Apply histogram equalization to the current image"""
        if self.main_controller.original_pixmap is None:
            self.main_controller.show_message(self.main_controller, 'warning', "Error", "Please load an image first")
            return

        try:
            from utils.image_utils import qpixmap_to_cv, cv_to_qpixmap

            # Convert QPixmap to OpenCV format
            cv_image = qpixmap_to_cv(self.main_controller.original_pixmap)

            # Apply histogram equalization
            equalized = histogram_equalization(cv_image)

            # Cache the equalized image
            self.equalized_image = equalized.copy()

            # Update current image for undo support
            self.main_controller.image_loader.update_current_image(equalized)

            # Update the display
            self.main_controller.output_pixmap = cv_to_qpixmap(equalized)
            self.main_controller._display_output_image(equalized)

            # Update undo button state
            self.main_controller._update_undo_button_state()

            self.main_controller.show_message(self.main_controller, 'success', "Success", "Histogram equalization applied")

        except Exception as e:
            self.main_controller.show_message(self.main_controller, 'error', "Error", f"Failed to apply equalization: {str(e)}")

    def _apply_normalize(self):
        """Apply normalization to the current image"""
        if self.main_controller.original_pixmap is None:
            self.main_controller.show_message(self.main_controller, 'warning', "Error", "Please load an image first")
            return

        try:
            import cv2
            from utils.image_utils import qpixmap_to_cv, cv_to_qpixmap

            # Convert QPixmap to OpenCV format
            cv_image = qpixmap_to_cv(self.main_controller.original_pixmap)

            # Normalize image (0-255 range)
            normalized = cv2.normalize(cv_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            # Update current image for undo support
            self.main_controller.image_loader.update_current_image(normalized)

            # Update the display
            self.main_controller.output_pixmap = cv_to_qpixmap(normalized)
            self.main_controller._display_output_image(normalized)

            # Update undo button state
            self.main_controller._update_undo_button_state()

            self.main_controller.show_message(self.main_controller, 'success', "Success", "Normalization applied")

        except Exception as e:
            self.main_controller.show_message(self.main_controller, 'error', "Error", f"Failed to apply normalization: {str(e)}")

    def _apply_grayscale(self):
        """Convert current image to grayscale"""
        if self.main_controller.original_pixmap is None:
            self.main_controller.show_message(self.main_controller, 'warning', "Error", "Please load an image first")
            return

        try:
            from utils.image_utils import qpixmap_to_cv, cv_to_qpixmap

            # Convert QPixmap to OpenCV format
            cv_image = qpixmap_to_cv(self.main_controller.original_pixmap)

            # Apply grayscale conversion
            gray_image = to_grayscale(cv_image)

            # Cache the grayscale image
            self.grayscale_image = gray_image.copy()

            # Update current image for undo support
            self.main_controller.image_loader.update_current_image(gray_image)

            # Update the display
            self.main_controller.output_pixmap = cv_to_qpixmap(gray_image)
            self.main_controller._display_output_image(gray_image)

            # Update undo button state
            self.main_controller._update_undo_button_state()

            self.main_controller.show_message(self.main_controller, 'success', "Success", "Converted to grayscale")

        except Exception as e:
            self.main_controller.show_message(self.main_controller, 'error', "Error", f"Failed to convert to grayscale: {str(e)}")

    def compute_stats(self, img):
        """
        Compute histogram statistics for an image

        Args:
            img: Input image (grayscale or RGB)

        Returns:
            hist, pdf, cdf: Histogram statistics
        """
        return compute_histogram_stats(img)

    def equalize_image(self, img):
        """
        Apply histogram equalization to an image

        Args:
            img: Input image (grayscale or RGB)

        Returns:
            Equalized image
        """
        return histogram_equalization(img)

    def show_distribution(self, img, mode="hist", title="Distribution"):
        """
        Display histogram distribution
        
        Args:
            img: Input image
            mode: 'hist', 'pdf', or 'cdf'
            title: Title for the plot
        """
        draw_distribution(img, mode=mode, title=title)
