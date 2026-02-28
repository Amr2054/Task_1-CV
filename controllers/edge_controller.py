from services.edge_service import EdgeService

class EdgeController:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.edge_service = EdgeService()
        self._connect_signals()
        # تحديث العرض بناءً على نوع الحواف الحالي
        self._on_edge_type_changed()

    def _connect_signals(self):
        # ربط كل radio buttons الخاصة بأنواع الحواف بالوظيفة _on_edge_type_changed
        for rb in ['radioCanny', 'radioSobel', 'radioPrewitt', 'radioRoberts']:
            getattr(self.main_controller, rb).toggled.connect(self._on_edge_type_changed)
        # ربط زرار Apply لتطبيق الكشف عن الحواف
        self.main_controller.btnApplyEdgeDetection.clicked.connect(self._apply_edge_detection)
        
        # ربط السلايدرز لتحديث قيمها في الـ labels
        self.main_controller.sliderEdgeKernelSize.valueChanged.connect(self._update_edge_kernel_label)
        self.main_controller.sliderEdgeThreshold.valueChanged.connect(self._update_threshold_label)
        self.main_controller.sliderWeight.valueChanged.connect(self._update_weight_label)
        self.main_controller.sliderKx.valueChanged.connect(self._update_kx_label)
        self.main_controller.sliderKy.valueChanged.connect(self._update_ky_label)

    def _update_edge_kernel_label(self, value):
        """تحديث label الخاص بـ Edge Kernel Size"""
        # التأكد من أن القيمة فردية (odd)
        if value % 2 == 0:
            value += 1
            self.main_controller.sliderEdgeKernelSize.setValue(value)
        self.main_controller.labelEdgeKernel.setText(f"Edge Kernel Size: {value}")
    
    def _update_threshold_label(self, value):
        """تحديث label الخاص بـ Threshold"""
        self.main_controller.labelEdgeThreshold.setText(f"Threshold: {value}")
    
    def _update_weight_label(self, value):
        """تحديث label الخاص بـ Weight"""
        self.main_controller.labelWeight.setText(f"Weight: {value/10:.1f}")
    
    def _update_kx_label(self, value):
        """تحديث label الخاص بـ Kx Scale"""
        self.main_controller.labelKx.setText(f"Kx Scale: {value/10:.1f}")
    
    def _update_ky_label(self, value):
        """تحديث label الخاص بـ Ky Scale"""
        self.main_controller.labelKy.setText(f"Ky Scale: {value/10:.1f}")

    def _on_edge_type_changed(self):
        """
        تحديث ظهور السلايدرز بناءً على نوع الحواف المختار.
        - Threshold يظهر فقط لو اخترنا Canny
        - Edge Kernel Size يظهر فقط لو اخترنا Sobel أو Prewitt
        - Weight, Kx, Ky يظلوا ظاهرين دائمًا لأي نوع edge
        """
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
        if not self.main_controller.image_loader.has_image():
            self.main_controller.show_message(self.main_controller, 'warning', "No Image", "Upload image first")
            return

        img = self.main_controller.image_loader.get_original_image()
        blur_sigma = 1.0
        # قراءة قيم Weight و Kx و Ky
        weight = self.main_controller.sliderWeight.value() / 10
        kx = self.main_controller.sliderKx.value() / 10
        ky = self.main_controller.sliderKy.value() / 10

        # قراءة Kernel Size الخاص بالـ edge operator (Sobel / Prewitt)
        edge_kernel_size = self.main_controller.sliderEdgeKernelSize.value()
        if edge_kernel_size % 2 == 0:
            edge_kernel_size += 1  # تأكد إنه عدد فردي

        # تحديد نوع الحواف المطبق
        if self.main_controller.radioCanny.isChecked():
            threshold = self.main_controller.sliderEdgeThreshold.value()
            result = self.edge_service.apply_canny(img, threshold, blur_size=5, blur_sigma=blur_sigma,
                                                   weight=weight, kx=kx, ky=ky)
        elif self.main_controller.radioSobel.isChecked():
            result = self.edge_service.apply_sobel(img, kernel_size=edge_kernel_size, blur_sigma=blur_sigma,
                                                   weight=weight, kx=kx, ky=ky)
        elif self.main_controller.radioPrewitt.isChecked():
            result = self.edge_service.apply_prewitt(img, kernel_size=edge_kernel_size, blur_sigma=blur_sigma,
                                                     weight=weight, kx=kx, ky=ky)
        else:
            result = self.edge_service.apply_roberts(img, blur_sigma=blur_sigma, weight=weight, kx=kx, ky=ky)

        if result is None:
            self.main_controller.show_message(self.main_controller, 'error', "Error", "Edge failed")
            return

        self.main_controller.image_loader.update_current_image(result)
        self.main_controller._display_output_image(result)
        self.main_controller._update_undo_button_state()