"""
Main controller for managing the application window and UI state
"""
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5 import uic
from pathlib import Path
from services.image_loader import ImageLoader
from utils.image_utils import cv_to_qpixmap, scale_pixmap
from controllers.curves_controller import HistogramController


class MainController(QMainWindow):
    """
    Main window controller that manages the application state and UI
    """
    
    def __init__(self):
        super().__init__()
        
        # Load UI file
        ui_path = Path(__file__).parent.parent / "ui" / "main_window.ui"
        uic.loadUi(ui_path, self)
        
        # Set minimum size for group boxes to maintain equal size but allow expansion
        self.noiseGroup.setMinimumSize(630, 230)
        self.filterGroup.setMinimumSize(630, 230)
        
        # Initialize image loader service
        self.image_loader = ImageLoader()
        
        # Store current pixmaps for resizing
        self.original_pixmap = None
        self.output_pixmap = None
        
        # Separate history for each mode (0: Noise, 1: Filter, 2: Edge, 3: Frequency, 4: Histogram)
        self.mode_history = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.current_mode = 0  # Track current mode
        
        # Initialize controllers
        self.histogram_controller = HistogramController(self)
        
        # Connect basic signals
        self._connect_main_signals()
    
    @staticmethod
    def show_message(parent, msg_type, title, text, informative_text=""):
        """
        Show a styled message box with consistent formatting
        
        Args:
            parent: Parent widget
            msg_type: Type of message ('warning', 'error', 'info', 'success')
            title: Dialog title
            text: Main message text
            informative_text: Optional additional information
        """
        msg_box = QMessageBox(parent)
        
        # Set icon based on type
        if msg_type == 'warning':
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == 'error':
            msg_box.setIcon(QMessageBox.Critical)
        elif msg_type in ['info', 'success']:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.setWindowTitle(title)
        msg_box.setText(f"<b style='color: black; font-size: 11pt;'>{text}</b>")
        
        if informative_text:
            msg_box.setInformativeText(f"<p style='color: black; font-size: 10pt;'>{informative_text}</p>")
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: black;
                min-width: 350px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 6px 20px;
                font-size: 10pt;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        msg_box.exec_()
    
    # ============== Shared Helper Methods ==============
    
    def validate_image_loaded(self, show_error=True):

        has_image = self.image_loader.has_image()
        if not has_image and show_error:
            self.show_warning("Please upload an image first.", "No Image")
        return has_image
    
    def uncheck_radio_buttons(self, *radio_buttons):
        """
        Helper to safely uncheck radio buttons without triggering signals
        
        Args:
            *radio_buttons: Variable number of QRadioButton objects to uncheck
        """
        for rb in radio_buttons:
            rb.blockSignals(True)
            rb.setAutoExclusive(False)
            rb.setChecked(False)
            rb.setAutoExclusive(True)
            rb.blockSignals(False)
    
    def show_error(self, message, title="Error"):
        """Show error message dialog"""
        self.show_message(self, 'error', title, message)
    
    def show_warning(self, message, title="Warning"):
        """Show warning message dialog"""
        self.show_message(self, 'warning', title, message)
    
    # ============== Signal Connections ==========================
    
    def _connect_main_signals(self):
        """Connect main window signals to slots"""
        # Top bar buttons
        self.btnUploadOriginal.clicked.connect(self._upload_original_image)
        self.btnUndo.clicked.connect(self._undo_last_operation)
        self.btnUndoAll.clicked.connect(self._undo_all_operations)
        self.btnReset.clicked.connect(self._reset_view)
        self.btnSave.clicked.connect(self._save_output_image)
        
        # Mode selector
        self.modeCombo.currentIndexChanged.connect(self._on_mode_changed)
        
        # Update undo button state initially
        self._update_undo_button_state()
    
    def _upload_original_image(self):    #1)upload original image
        """
        Open file dialog to select and load an image
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        # Load image using service
        success, image, error_msg = self.image_loader.load_image(file_path)
        
        if not success:
            self.show_message(self, 'error', "Error", error_msg)
            return
        
        # Clear history for current mode when loading new image
        self.mode_history[self.current_mode] = []
        
        # Display the loaded image
        self._display_original_image(image)
        
        # Clear output image
        self.imgOutput.clear()
        self.imgOutput.setText("Processed image will appear here")
        self.output_pixmap = None
        
        # Update undo button state
        self._update_undo_button_state()
    
    def _display_original_image(self, image):
        """
        Display the original image in the UI
        
        Args:
            image: OpenCV image (numpy array)
        """
        if image is None:
            return
        
        # Convert to pixmap
        pixmap = cv_to_qpixmap(image)
        
        # Store for resizing
        self.original_pixmap = pixmap
        
        # Scale and display
        self._set_scaled_pixmap(self.imgOriginal, pixmap)
    
    def _display_output_image(self, image):
        """
        Display the processed output image in the UI
        
        Args:
            image: OpenCV image (numpy array)
        """
        if image is None:
            return
        
        # Convert to pixmap
        pixmap = cv_to_qpixmap(image)
        
        # Store for resizing
        self.output_pixmap = pixmap
        
        # Scale and display
        self._set_scaled_pixmap(self.imgOutput, pixmap)
    
    def _undo_last_operation(self):
        """
        Undo the last operation (noise, filter, edge, or frequency)
        """
        if not self.image_loader.can_undo():
            self.show_message(self, 'info', "No History", "There are no operations to undo.")
            return
        
        # Undo and get previous image
        previous_image = self.image_loader.undo()
        
        if previous_image is not None:
            # Check if we're in frequency mode
            if self.current_mode == 3:  # Frequency mode
                # Display in frequency hybrid label
                from utils.image_utils import cv_to_qpixmap, scale_pixmap
                pixmap = cv_to_qpixmap(previous_image)
                scaled = scale_pixmap(pixmap, self.imgFreqHybrid.width() - 10, self.imgFreqHybrid.height() - 10)
                self.imgFreqHybrid.setPixmap(scaled)
            else:
                # Display in output image for other modes
                self._display_output_image(previous_image)
            
            self._update_undo_button_state()
        else:
            self.show_message(self, 'warning', "Undo Failed", "Failed to undo the last operation.")
    
    def _update_undo_button_state(self):
        """
        Update the enabled state of the undo button based on history
        """
        has_history = self.image_loader.can_undo()
        self.btnUndo.setEnabled(has_history)
        self.btnUndoAll.setEnabled(has_history)
    
    def _reset_all_controls(self):
        """
        Reset all UI controls in all modes to their initial state
        This is a centralized function to avoid code duplication
        """
        # Reset Noise controls
        if hasattr(self, 'noise_controller'):
            self.noise_controller.reset_noise_controls()
        
        # Reset Filter controls
        if hasattr(self, 'filter_controller'):
            self.filter_controller.reset_filter_controls()
        
        # Reset Edge Detection controls
        if hasattr(self, 'edge_controller'):
            self.edge_controller.reset_edge_controls()
        
        # Reset Frequency Domain controls
        if hasattr(self, 'frequency_controller'):
            self.frequency_controller.reset_frequency_controls()
        
        # Reset Histogram/Curves controls
        if hasattr(self, 'histogram_controller'):
            self.histogram_controller.reset_histogram_controls()
    
    def _set_scaled_pixmap(self, label, pixmap):
        """
        Scale and set pixmap to label
        
        Args:
            label: QLabel widget to display the image
            pixmap: QPixmap to display
        """
        if pixmap.isNull():
            return
        
        scaled = scale_pixmap(pixmap, label.width() - 20, label.height() - 20)
        label.setPixmap(scaled)
    
    def _undo_all_operations(self):
        """
        مسح كل الـ operations والرجوع للصورة الأصلية (مع إبقاء الـ original موجودة)
        Only reverts the image without changing any UI controls
        """
        # Check if in frequency mode (mode 3)
        if self.current_mode == 3:
            # In frequency mode, just clear the hybrid image
            self.imgFreqHybrid.clear()
            self.imgFreqHybrid.setText("Hybrid image will appear here")
            # Clear history for frequency mode
            self.mode_history[self.current_mode] = []
            self.image_loader.history = []
            self._update_undo_button_state()
            return
        
        if not self.image_loader.has_image():
            self.show_message(self, 'info', "No Image", "No image loaded.")
            return
        
        # Clear output image
        self.imgOutput.clear()
        self.imgOutput.setText("Processed image will appear here")
        self.output_pixmap = None
        
        # Reset to original image
        self.image_loader.reset_to_original()
        
        # Clear history for current mode
        self.mode_history[self.current_mode] = []
        
        # Update undo button state
        self._update_undo_button_state()
    
    def _save_output_image(self):
        """Save the output image to a file"""
        # Check if in frequency mode
        if self.current_mode == 3:
            # Check if hybrid image exists
            if not hasattr(self.imgFreqHybrid, 'pixmap') or self.imgFreqHybrid.pixmap() is None or self.imgFreqHybrid.pixmap().isNull():
                self.show_warning("No output image to save. Please generate a hybrid image first.", "No Output")
                return
        else:
            # Check if output image exists
            if self.output_pixmap is None or self.output_pixmap.isNull():
                self.show_warning("No output image to save. Please process an image first.", "No Output")
                return
        
        # Open save file dialog
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Output Image",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;BMP Image (*.bmp);;TIFF Image (*.tiff);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # Get the image to save
            if self.current_mode == 3:  # Frequency mode
                # Get current image from image_loader (last hybrid generated)
                if self.image_loader.can_undo() or self.image_loader.current_image is not None:
                    import cv2
                    cv2.imwrite(file_path, self.image_loader.current_image)
                else:
                    self.show_warning("No hybrid image to save.", "No Output")
                    return
            else:
                # Get current image from image_loader
                if self.image_loader.current_image is not None:
                    import cv2
                    cv2.imwrite(file_path, self.image_loader.current_image)
                else:
                    self.show_warning("No processed image to save.", "No Output")
                    return
            
            # Success message - show filename only
            from pathlib import Path
            filename = Path(file_path).name
            self.show_message(self, 'info', "Success", f"Image saved successfully as {filename}")
            
        except Exception as e:
            self.show_error(f"Failed to save image: {str(e)}")
    
    # def _on_mode_changed(self, index):
    #     self.settingsStack.setCurrentIndex(index)

    #     is_frequency = (index == 3)
    #     self.scrollArea.setVisible(not is_frequency)
        
    #     # إخفاء زر Upload Original في frequency mode
    #     self.btnUploadOriginal.setVisible(not is_frequency)

    #     # Make settings container expand to fill space when in frequency mode
    #     if is_frequency:
    #         self.settingsContainer.setMaximumHeight(16777215)  # unlimited
    #     else:
    #         self.settingsContainer.setMaximumHeight(310)  # original constraint

    #     # Clear output image when switching modes
    #     self.imgOutput.clear()
    #     self.imgOutput.setText("Processed image will appear here")
    #     self.output_pixmap = None
        
    #     # مسح الـ history عند تغيير الـ mode لجعل كل mode له history خاص به
    #     self.image_loader.history = []
    #     self._update_undo_button_state()
    
    def _on_mode_changed(self, index):
        # Save current mode's history before switching
        if hasattr(self, 'current_mode'):
            self.mode_history[self.current_mode] = self.image_loader.history.copy()
        
        # Update current mode
        self.current_mode = index
        
        # Restore the new mode's history
        self.image_loader.history = self.mode_history[index].copy()
        
        is_frequency = (index == 3)

        # Update heights BEFORE changing visibility to avoid layout glitch
        if is_frequency:
            self.settingsContainer.setMaximumHeight(16777215)  # unlimited
            self.scrollArea.setVisible(False)
        else:
            self.settingsContainer.setMaximumHeight(310)  # original constraint
            self.scrollArea.setVisible(True)

        self.settingsStack.setCurrentIndex(index)

        # إخفاء زر Upload Original في frequency mode
        self.btnUploadOriginal.setVisible(not is_frequency)

        # Force layout recalculation to prevent misplaced widgets
        self.centralWidget().updateGeometry()
        self.centralWidget().layout().activate()

        # Clear output image when switching modes
        self.imgOutput.clear()
        self.imgOutput.setText("Processed image will appear here")
        self.output_pixmap = None
        
        # Update undo button state based on new mode's history
        self._update_undo_button_state()
        
        # Reset all UI controls when switching modes
        self._reset_all_controls()
    
    def _reset_view(self):
        """
        Reset all images and UI controls to initial state
        """
        # Reset images
        self.imgOriginal.clear()
        self.imgOriginal.setText("Upload an image to get started")
        self.imgOutput.clear()
        self.imgOutput.setText("Processed image will appear here")
        
        # Reset frequency mode images
        self.imgFreqLowPass.clear()
        self.imgFreqLowPass.setText("Upload image to apply Low Pass")
        self.imgFreqHighPass.clear()
        self.imgFreqHighPass.setText("Upload image to apply High Pass")
        self.imgFreqHybrid.clear()
        self.imgFreqHybrid.setText("Hybrid image will appear here")
        
        # Clear stored pixmaps
        self.original_pixmap = None
        self.output_pixmap = None
        
        # Reset all UI controls
        self._reset_all_controls()
        
        # Reset image loader
        self.image_loader = ImageLoader()
        
        # Clear all mode history
        self.mode_history = {0: [], 1: [], 2: [], 3: [], 4: []}
        
        # Update undo button state
        self._update_undo_button_state()
    
    def resizeEvent(self, event):
        """
        Handle window resize to rescale images proportionally
        
        Args:
            event: QResizeEvent
        """
        super().resizeEvent(event)
        
        # Rescale images if they exist
        if self.original_pixmap and not self.original_pixmap.isNull():
            self._set_scaled_pixmap(self.imgOriginal, self.original_pixmap)
        
        if self.output_pixmap and not self.output_pixmap.isNull():
            self._set_scaled_pixmap(self.imgOutput, self.output_pixmap)
    
    def get_image_loader(self):
        """Get the image loader service"""
        return self.image_loader
