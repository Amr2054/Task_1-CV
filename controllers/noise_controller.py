"""
Noise controller for managing noise-related UI interactions
"""
from services.noise_service import NoiseService


class NoiseController:
    """
    Controller for managing noise controls and applying noise to images
    """
    
    # Default slider values
    DEFAULT_VALUES = {
        'uniform': 30,
        'salt_pepper': 5,
        'gaussian_mean': 0,
        'gaussian_sigma': 10
    }
    
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.noise_service = NoiseService()
        self._connect_signals()
        self._initialize_controls()
    
    def _initialize_controls(self):
        """Initialize all controls to default state"""
        mc = self.main_controller
        # Set default values
        mc.sliderUniform.setValue(self.DEFAULT_VALUES['uniform'])
        mc.sliderSaltPepper.setValue(self.DEFAULT_VALUES['salt_pepper'])
        mc.sliderGaussianMean.setValue(self.DEFAULT_VALUES['gaussian_mean'])
        mc.sliderGaussianSigma.setValue(self.DEFAULT_VALUES['gaussian_sigma'])
        # Hide all sliders initially
        self._on_noise_type_changed()
    
    def _connect_signals(self):
        """Connect noise-related signals to slots"""
        mc = self.main_controller
        # Radio buttons
        mc.radioUniform.toggled.connect(self._on_noise_type_changed)
        mc.radioSaltPepper.toggled.connect(self._on_noise_type_changed)
        mc.radioGaussian.toggled.connect(self._on_noise_type_changed)
        
        # Sliders
        mc.sliderUniform.valueChanged.connect(lambda v: mc.labelUniformValue.setText(f"Range: ±{v}"))
        mc.sliderSaltPepper.valueChanged.connect(lambda v: mc.labelSaltPepperValue.setText(f"Amount: {v}%"))
        mc.sliderGaussianMean.valueChanged.connect(lambda v: mc.labelGaussianMeanValue.setText(f"Mean: {v}"))
        mc.sliderGaussianSigma.valueChanged.connect(lambda v: mc.labelGaussianSigmaValue.setText(f"Sigma: {v}"))
        
        # Apply button
        mc.btnApplyNoise.clicked.connect(self._apply_noise)
    
    def _on_noise_type_changed(self):
        """Handle noise type radio button changes to show/hide appropriate sliders"""
        mc = self.main_controller
        is_uniform = mc.radioUniform.isChecked()
        is_salt_pepper = mc.radioSaltPepper.isChecked()
        is_gaussian = mc.radioGaussian.isChecked()
        
        # Show/hide slider containers
        mc.uniformSliderContainer.setVisible(is_uniform)
        mc.sliderUniform.setVisible(is_uniform)
        mc.labelUniformValue.setVisible(is_uniform)
        
        mc.saltPepperSliderContainer.setVisible(is_salt_pepper)
        mc.sliderSaltPepper.setVisible(is_salt_pepper)
        mc.labelSaltPepperValue.setVisible(is_salt_pepper)
        
        mc.gaussianSliderContainer.setVisible(is_gaussian)
        mc.sliderGaussianMean.setVisible(is_gaussian)
        mc.labelGaussianMeanValue.setVisible(is_gaussian)
        mc.sliderGaussianSigma.setVisible(is_gaussian)
        mc.labelGaussianSigmaValue.setVisible(is_gaussian)
    
    def reset_noise_controls(self):
        """Reset all noise controls to initial state"""
        mc = self.main_controller
        
        # Uncheck all radio buttons
        mc.uncheck_radio_buttons(mc.radioUniform, mc.radioSaltPepper, mc.radioGaussian)
        
        # Reset to default values (reuse initialization)
        self._initialize_controls()
    
    def _apply_noise(self):
        """Apply the selected noise type to the original image"""
        mc = self.main_controller
        
        if not mc.validate_image_loaded():
            return
        
        image = mc.image_loader.get_original_image()
        
        # Apply selected noise type
        if mc.radioUniform.isChecked():
            result = self.noise_service.apply_uniform_noise(image, mc.sliderUniform.value())
        elif mc.radioSaltPepper.isChecked():
            result = self.noise_service.apply_salt_pepper_noise(image, mc.sliderSaltPepper.value())
        elif mc.radioGaussian.isChecked():
            result = self.noise_service.apply_gaussian_noise(image, mc.sliderGaussianMean.value(), mc.sliderGaussianSigma.value())
        else:
            mc.show_warning("Please select a noise type.", "No Selection")
            return
        
        if result is None:
            mc.show_error("Failed to apply noise.")
            return
        
        # Update and display
        mc.image_loader.update_current_image(result)
        mc._display_output_image(result)
        mc._update_undo_button_state()
