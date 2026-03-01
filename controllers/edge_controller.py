from services.edge_service import EdgeService


class EdgeController:
    
    # Default slider values
    DEFAULT_VALUES = {
        'kernel_size': 3,
        'threshold': 100,
        'weight': 10,  # 1.0 actual
        'kx': 10,      # 1.0 actual
        'ky': 10       # 1.0 actual
    }
    
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.edge_service = EdgeService()
        self._connect_signals()
        self._initialize_controls()
    
    def _initialize_controls(self):
        """Initialize all controls to default state"""
        mc = self.main_controller
        if hasattr(mc, 'sliderEdgeKernelSize'):
            mc.sliderEdgeKernelSize.setValue(self.DEFAULT_VALUES['kernel_size'])
        if hasattr(mc, 'sliderEdgeThreshold'):
            mc.sliderEdgeThreshold.setValue(self.DEFAULT_VALUES['threshold'])
        if hasattr(mc, 'sliderWeight'):
            mc.sliderWeight.setValue(self.DEFAULT_VALUES['weight'])
        if hasattr(mc, 'sliderKx'):
            mc.sliderKx.setValue(self.DEFAULT_VALUES['kx'])
        if hasattr(mc, 'sliderKy'):
            mc.sliderKy.setValue(self.DEFAULT_VALUES['ky'])
        self._on_edge_type_changed()

    def _connect_signals(self):
        mc = self.main_controller
        # Radio buttons
        for rb_name in ['radioCanny', 'radioSobel', 'radioPrewitt', 'radioRoberts']:
            getattr(mc, rb_name).toggled.connect(self._on_edge_type_changed)
        
        # Apply button
        mc.btnApplyEdgeDetection.clicked.connect(self._apply_edge_detection)
        
        # Sliders - using lambda for cleaner code
        mc.sliderEdgeKernelSize.valueChanged.connect(lambda v: self._update_kernel_label(v))
        mc.sliderEdgeThreshold.valueChanged.connect(lambda v: mc.labelEdgeThreshold.setText(f"Threshold: {v}"))
        mc.sliderWeight.valueChanged.connect(lambda v: mc.labelWeight.setText(f"Weight: {v/10:.1f}"))
        mc.sliderKx.valueChanged.connect(lambda v: mc.labelKx.setText(f"Kx Scale: {v/10:.1f}"))
        mc.sliderKy.valueChanged.connect(lambda v: mc.labelKy.setText(f"Ky Scale: {v/10:.1f}"))
    
    def _update_kernel_label(self, value):
        """Update label for Edge Kernel Size ensuring odd value"""
        if value % 2 == 0:
            value += 1
            self.main_controller.sliderEdgeKernelSize.setValue(value)
        self.main_controller.labelEdgeKernel.setText(f"Edge Kernel Size: {value}")
    
    def reset_edge_controls(self):
        """Reset all edge detection controls to initial state"""
        mc = self.main_controller
        
        # Uncheck all radio buttons
        mc.uncheck_radio_buttons(mc.radioCanny, mc.radioSobel, mc.radioPrewitt, mc.radioRoberts)
        
        # Reset to default values (reuse initialization)
        self._initialize_controls()
    
    def _on_edge_type_changed(self):
        """Update slider visibility based on selected edge type"""
        is_canny = self.main_controller.radioCanny.isChecked()
        is_roberts = self.main_controller.radioRoberts.isChecked()
        is_sobel = self.main_controller.radioSobel.isChecked()
        is_prewitt = self.main_controller.radioPrewitt.isChecked()

        # Threshold يظهر فقط لو Canny
        self.main_controller.sliderEdgeThreshold.setVisible(is_canny)
        self.main_controller.labelEdgeThreshold.setVisible(is_canny)

        # Edge Kernel Size يظهر فقط لو Sobel أو Prewitt
        show_kernel = is_sobel or is_prewitt
        self.main_controller.sliderEdgeKernelSize.setVisible(show_kernel)
        self.main_controller.labelEdgeKernel.setVisible(show_kernel)

        # Weight و Kx و Ky يظلوا ظاهرين دائمًا
        self.main_controller.sliderWeight.setVisible(True)
        self.main_controller.sliderKx.setVisible(True)
        self.main_controller.sliderKy.setVisible(True)

    def _apply_edge_detection(self):
        """
        تطبيق الكشف عن الحواف على الصورة الحالية بناءً على الاختيارات في الـ UI
        """
        mc = self.main_controller
        
        if not mc.validate_image_loaded():
            return

        # Check if an edge detection type is selected
        if not (mc.radioCanny.isChecked() or 
                mc.radioSobel.isChecked() or 
                mc.radioPrewitt.isChecked() or 
                mc.radioRoberts.isChecked()):
            mc.show_warning("Please select an edge detection type first", "No Selection")
            return

        img = mc.image_loader.get_original_image()
        blur_sigma = 1.0
        # قراءة قيم Weight و Kx و Ky
        weight = mc.sliderWeight.value() / 10
        kx = mc.sliderKx.value() / 10
        ky = mc.sliderKy.value() / 10

        # قراءة Kernel Size الخاص بالـ edge operator (Sobel / Prewitt)
        edge_kernel_size = mc.sliderEdgeKernelSize.value()
        if edge_kernel_size % 2 == 0:
            edge_kernel_size += 1  # تأكد إنه عدد فردي

        # تحديد نوع الحواف المطبق
        if mc.radioCanny.isChecked():
            threshold = mc.sliderEdgeThreshold.value()
            result = self.edge_service.apply_canny(img, threshold, blur_size=5, blur_sigma=blur_sigma,
                                                   weight=weight, kx=kx, ky=ky)
        elif mc.radioSobel.isChecked():
            result = self.edge_service.apply_sobel(img, kernel_size=edge_kernel_size, blur_sigma=blur_sigma,
                                                   weight=weight, kx=kx, ky=ky)
        elif mc.radioPrewitt.isChecked():
            result = self.edge_service.apply_prewitt(img, kernel_size=edge_kernel_size, blur_sigma=blur_sigma,
                                                     weight=weight, kx=kx, ky=ky)
        elif mc.radioRoberts.isChecked():
            result = self.edge_service.apply_roberts(img, blur_sigma=blur_sigma, weight=weight, kx=kx, ky=ky)
        else:
            return

        if result is None:
            mc.show_error("Edge detection failed")
            return

        mc.image_loader.update_current_image(result)
        mc._display_output_image(result)
        mc._update_undo_button_state()