"""
Filter controller for managing filter-related UI interactions
"""
from PyQt5.QtWidgets import QMessageBox
from services.filter_service import FilterService


class FilterController:
    """
    Controller for managing filter controls and applying filters to images
    """
    
    def __init__(self, main_controller):
        """
        Initialize filter controller
        
        Args:
            main_controller: Reference to the main controller
        """
        self.main_controller = main_controller
        self.filter_service = FilterService()
        
        # Connect signals
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect filter-related signals to slots"""
        # Apply button
        self.main_controller.btnApplyFilter.clicked.connect(self._apply_filter)
    
    def _apply_filter(self):
        """
        Apply the selected filter type to either original or current image based on combo box selection
        """
        # Check if image is loaded
        if not self.main_controller.image_loader.has_image():
            self.main_controller.show_message(
                self.main_controller,
                'warning',
                "No Image",
                "Please upload an image first."
            )
            return
        
        # Get image based on combo box selection
        # Index 0 = Current Image (with Noise), Index 1 = Original Image
        apply_on_index = self.main_controller.comboFilterApplyOn.currentIndex()
        
        if apply_on_index == 0:
            # Check if current image has been modified (noise applied)
            if not self.main_controller.image_loader.is_image_modified():
                self.main_controller.show_message(
                    self.main_controller,
                    'warning',
                    "No Current Image",
                    "There is no current image with noise applied yet.",
                    # "Please choose one of the following options:<br><br>"
                    # "<b>1.</b> Apply noise first to create a current image<br>"
                    # "<b>2.</b> Select 'Original Image' from the dropdown and apply the filter"
                )
                return
            else:
                # Apply on current image (which has noise)
                image = self.main_controller.image_loader.get_current_image()
        else:
            # Apply on original image
            image = self.main_controller.image_loader.get_original_image()
        
        # Get kernel size from combo box
        # Index 0 = 3×3, Index 1 = 5×5, Index 2 = 7×7, Index 3 = 9×9, Index 4 = 11×11, Index 5 = 13×13, Index 6 = 15×15
        kernel_index = self.main_controller.comboKernelSize.currentIndex()
        kernel_sizes = [3, 5, 7, 9, 11, 13, 15]
        kernel_size = kernel_sizes[kernel_index] if kernel_index < len(kernel_sizes) else 3
        
        # Determine which filter type is selected and apply
        if self.main_controller.radioAverage.isChecked():
            result = self.filter_service.apply_average_filter(image, kernel_size)
        
        elif self.main_controller.radioGaussianFilter.isChecked():
            # Use sigma=1 as default for manual implementation
            result = self.filter_service.apply_gaussian_filter(image, kernel_size, sigma=1)
        
        elif self.main_controller.radioMedian.isChecked():
            result = self.filter_service.apply_median_filter(image, kernel_size)
        
        else:
            self.main_controller.show_message(
                self.main_controller,
                'warning',
                "No Selection",
                "Please select a filter type."
            )
            return
        
        # Check if processing was successful
        if result is None:
            self.main_controller.show_message(
                self.main_controller,
                'error',
                "Error",
                "Failed to apply filter."
            )
            return
        
        # Update current image and display
        self.main_controller.image_loader.update_current_image(result)
        self.main_controller._display_output_image(result)
        
        # Update undo button state
        self.main_controller._update_undo_button_state()
