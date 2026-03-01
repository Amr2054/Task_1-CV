"""
Filter controller for managing filter-related UI interactions
"""
from services.filter_service import FilterService


class FilterController:
    """
    Controller for managing filter controls and applying filters to images
    """
    
    # Default values
    DEFAULT_SIGMA = 10  # Slider value (1.0 actual)
    
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.filter_service = FilterService()
        self._connect_signals()
        self._initialize_controls()
    
    def _initialize_controls(self):
        """Initialize all controls to default state"""
        mc = self.main_controller
        mc.sliderSigma.setValue(self.DEFAULT_SIGMA)
        mc.sigmaContainer.setVisible(False)
        mc.comboKernelSize.setCurrentIndex(0)
        mc.comboFilterApplyOn.setCurrentIndex(0)
    
    def _connect_signals(self):
        """Connect filter-related signals to slots"""
        mc = self.main_controller
        mc.btnApplyFilter.clicked.connect(self._apply_filter)
        mc.sliderSigma.valueChanged.connect(lambda v: mc.labelSigmaValue.setText(f"{v/10:.1f}"))
        mc.radioGaussianFilter.toggled.connect(lambda checked: mc.sigmaContainer.setVisible(checked))
        mc.sliderSigma.valueChanged.emit(mc.sliderSigma.value())  # Initialize label
    
    def reset_filter_controls(self):
        """Reset all filter controls to initial state"""
        mc = self.main_controller
        
        # Uncheck all radio buttons
        mc.uncheck_radio_buttons(mc.radioAverage, mc.radioGaussianFilter, mc.radioMedian)
        
        # Reset to default values (reuse initialization)
        self._initialize_controls()
    
    def _apply_filter(self):
        """Apply the selected filter type to either original or current image"""
        mc = self.main_controller
        
        if not mc.validate_image_loaded():
            return
        
        # Get image based on selection
        apply_on_index = mc.comboFilterApplyOn.currentIndex()
        if apply_on_index == 0:
            if not mc.image_loader.is_image_modified():
                mc.show_warning("There is no current image with noise applied yet.", "No Current Image")
                return
            image = mc.image_loader.get_current_image()
        else:
            image = mc.image_loader.get_original_image()
        
        # Get kernel size
        kernel_sizes = [3, 5, 7, 9, 11, 13, 15]
        kernel_size = kernel_sizes[mc.comboKernelSize.currentIndex()]
        
        # Apply selected filter
        if mc.radioAverage.isChecked():
            result = self.filter_service.apply_average_filter(image, kernel_size)
        elif mc.radioGaussianFilter.isChecked():
            sigma = mc.sliderSigma.value() / 10.0
            result = self.filter_service.apply_gaussian_filter(image, kernel_size, sigma=sigma)
        elif mc.radioMedian.isChecked():
            result = self.filter_service.apply_median_filter(image, kernel_size)
        else:
            mc.show_warning("Please select a filter type.", "No Selection")
            return
        
        if result is None:
            mc.show_error("Failed to apply filter.")
            return
        
        # Update and display
        mc.image_loader.update_current_image(result)
        mc._display_output_image(result)
        mc._update_undo_button_state()
