from services.edge_service import EdgeService

class EdgeController:

    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.edge_service = EdgeService()

        self._connect_signals()
        self._on_edge_type_changed()

    def _connect_signals(self):

        self.main_controller.radioCanny.toggled.connect(self._on_edge_type_changed)
        self.main_controller.radioSobel.toggled.connect(self._on_edge_type_changed)
        self.main_controller.radioPrewitt.toggled.connect(self._on_edge_type_changed)
        self.main_controller.radioRoberts.toggled.connect(self._on_edge_type_changed)

        self.main_controller.btnApplyEdgeDetection.clicked.connect(self._apply_edge_detection)


    def _on_edge_type_changed(self):

        is_canny = self.main_controller.radioCanny.isChecked()
        is_kernel = not is_canny

        self.main_controller.sliderEdgeThreshold.setVisible(is_canny)
        self.main_controller.labelEdgeThreshold.setVisible(is_canny)

        self.main_controller.sliderWeight.setVisible(is_kernel)
        self.main_controller.sliderKx.setVisible(is_kernel)
        self.main_controller.sliderKy.setVisible(is_kernel)


    def _apply_edge_detection(self):

        if not self.main_controller.image_loader.has_image():
            self.main_controller.show_message(self.main_controller,'warning',"No Image","Upload image first")
            return

        image = self.main_controller.image_loader.get_original_image()

        blur_size = 5
        blur_sigma = 1.0

        weight = self.main_controller.sliderWeight.value()/10
        kx = self.main_controller.sliderKx.value()/10
        ky = self.main_controller.sliderKy.value()/10

        if self.main_controller.radioCanny.isChecked():

            threshold = self.main_controller.sliderEdgeThreshold.value()

            result = self.edge_service.apply_canny(image,threshold,blur_size,blur_sigma)

        elif self.main_controller.radioSobel.isChecked():

            result = self.edge_service.apply_sobel(image,blur_size,blur_sigma,weight,kx,ky)

        elif self.main_controller.radioPrewitt.isChecked():

            result = self.edge_service.apply_prewitt(image,blur_size,blur_sigma,weight,kx,ky)

        else:

            result = self.edge_service.apply_roberts(image,blur_size,blur_sigma,weight,kx,ky)


        if result is None:
            self.main_controller.show_message(self.main_controller,'error',"Error","Edge failed")
            return

        self.main_controller.image_loader.update_current_image(result)
        self.main_controller._display_output_image(result)
        self.main_controller._update_undo_button_state()