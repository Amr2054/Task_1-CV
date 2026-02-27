"""
Noise controller for managing noise-related UI interactions
"""
from PyQt5.QtWidgets import QMessageBox
from services.noise_service import NoiseService


class NoiseController:
    """
    Controller for managing noise controls and applying noise to images
    """
    
    def __init__(self, main_controller):
        """
        Initialize noise controller
        
        Args:
            main_controller: Reference to the main controller
        """
        self.main_controller = main_controller
        self.noise_service = NoiseService()
        
        # Connect signals
        self._connect_signals()
        
        # Initialize: Hide all sliders at start
        self._on_noise_type_changed()
    
    def _connect_signals(self):
        """Connect noise-related signals to slots"""
        # Radio button changes
        self.main_controller.radioUniform.toggled.connect(self._on_noise_type_changed)
        self.main_controller.radioSaltPepper.toggled.connect(self._on_noise_type_changed)
        self.main_controller.radioGaussian.toggled.connect(self._on_noise_type_changed)
        
        # Slider value changes - update labels
        self.main_controller.sliderUniform.valueChanged.connect(self._update_uniform_label)
        self.main_controller.sliderSaltPepper.valueChanged.connect(self._update_salt_pepper_label)
        self.main_controller.sliderGaussianMean.valueChanged.connect(self._update_gaussian_mean_label)
        self.main_controller.sliderGaussianSigma.valueChanged.connect(self._update_gaussian_sigma_label)
        
        # Apply button
        self.main_controller.btnApplyNoise.clicked.connect(self._apply_noise)
    
    def _on_noise_type_changed(self):
        """
        Handle noise type radio button changes to show/hide appropriate sliders
        """
        # Get which radio button is checked
        is_uniform = self.main_controller.radioUniform.isChecked()
        is_salt_pepper = self.main_controller.radioSaltPepper.isChecked()
        is_gaussian = self.main_controller.radioGaussian.isChecked()
        
        # Show/hide slider containers and their widgets
        self.main_controller.uniformSliderContainer.setVisible(is_uniform)
        self.main_controller.sliderUniform.setVisible(is_uniform)
        self.main_controller.labelUniformValue.setVisible(is_uniform)
        
        self.main_controller.saltPepperSliderContainer.setVisible(is_salt_pepper)
        self.main_controller.sliderSaltPepper.setVisible(is_salt_pepper)
        self.main_controller.labelSaltPepperValue.setVisible(is_salt_pepper)
        
        self.main_controller.gaussianSliderContainer.setVisible(is_gaussian)
        self.main_controller.sliderGaussianMean.setVisible(is_gaussian)
        self.main_controller.labelGaussianMeanValue.setVisible(is_gaussian)
        self.main_controller.sliderGaussianSigma.setVisible(is_gaussian)
        self.main_controller.labelGaussianSigmaValue.setVisible(is_gaussian)
    
    def _update_uniform_label(self, value):
        """Update the uniform noise slider label"""
        self.main_controller.labelUniformValue.setText(f"Range: ±{value}")
    
    def _update_salt_pepper_label(self, value):
        """Update the salt & pepper noise slider label"""
        self.main_controller.labelSaltPepperValue.setText(f"Amount: {value}%")
    
    def _update_gaussian_mean_label(self, value):
        """Update the gaussian noise mean slider label"""
        self.main_controller.labelGaussianMeanValue.setText(f"Mean: {value}")
    
    def _update_gaussian_sigma_label(self, value):
        """Update the gaussian noise sigma slider label"""
        self.main_controller.labelGaussianSigmaValue.setText(f"Sigma: {value}")
    
    def _apply_noise(self):
        """
        Apply the selected noise type to the original image
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
        
        # Get original image
        image = self.main_controller.image_loader.get_original_image()
        
        # Determine which noise type is selected and apply
        if self.main_controller.radioUniform.isChecked():
            # Uniform noise: slider controls the range (-value to +value)
            intensity = self.main_controller.sliderUniform.value()
            result = self.noise_service.apply_uniform_noise(image, intensity)
        
        elif self.main_controller.radioSaltPepper.isChecked():
            # Salt & Pepper: slider controls percentage of affected pixels
            amount = self.main_controller.sliderSaltPepper.value()
            result = self.noise_service.apply_salt_pepper_noise(image, amount)
        
        elif self.main_controller.radioGaussian.isChecked():
            # Gaussian noise: sliders control mean and sigma
            mean = self.main_controller.sliderGaussianMean.value()
            sigma = self.main_controller.sliderGaussianSigma.value()
            result = self.noise_service.apply_gaussian_noise(image, mean=mean, sigma=sigma)
        
        else:
            self.main_controller.show_message(
                self.main_controller,
                'warning',
                "No Selection",
                "Please select a noise type."
            )
            return
        
        # Check if processing was successful
        if result is None:
            self.main_controller.show_message(
                self.main_controller,
                'error',
                "Error",
                "Failed to apply noise."
            )
            return
        
        # Update current image and display
        self.main_controller.image_loader.update_current_image(result)
        self.main_controller._display_output_image(result)
        
        # Update undo button state
        self.main_controller._update_undo_button_state()
