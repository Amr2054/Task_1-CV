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
    
    def _connect_main_signals(self):
        """Connect main window signals to slots"""
        # Top bar buttons
        self.btnUploadOriginal.clicked.connect(self._upload_original_image)
        self.btnUndo.clicked.connect(self._undo_last_operation)
        self.btnUndoAll.clicked.connect(self._undo_all_operations)
        self.btnReset.clicked.connect(self._reset_view)
        
        # Mode selector
        self.modeCombo.currentIndexChanged.connect(self._on_mode_changed)
        
        # Update undo button state initially
        self._update_undo_button_state()
    
    def _upload_original_image(self):
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
        Undo the last operation (noise or filter)
        """
        if not self.image_loader.can_undo():
            self.show_message(self, 'info', "No History", "There are no operations to undo.")
            return
        
        # Undo and get previous image
        previous_image = self.image_loader.undo()
        
        if previous_image is not None:
            # Display the previous state
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
        """
        if not self.image_loader.has_image():
            self.show_message(self, 'info', "No Image", "No image loaded.")
            return
        
        # Clear output image
        self.imgOutput.clear()
        self.imgOutput.setText("Processed image will appear here")
        self.output_pixmap = None
        
        # Clear frequency mode images (except original)
        self.imgFreqHybrid.clear()
        self.imgFreqHybrid.setText("Hybrid image will appear here")
        
        # Reset to original image
        self.image_loader.reset_to_original()
        
        # Reset histogram controller cached image
        if hasattr(self, 'histogram_controller'):
            self.histogram_controller.equalized_image = None
        
        # Update undo button state
        self._update_undo_button_state()
    
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

        # مسح الـ history عند تغيير الـ mode
        self.image_loader.history = []
        self._update_undo_button_state()
    
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
        
        # Reset histogram controller cached image
        if hasattr(self, 'histogram_controller'):
            self.histogram_controller.equalized_image = None
        
        # Reset frequency controller images
        if hasattr(self, 'frequency_controller'):
            self.frequency_controller._img1 = None
            self.frequency_controller._img2 = None
        
        # Reset image loader
        self.image_loader = ImageLoader()
    
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
