"""
Image Studio - Professional Image Processing Application
Version: 2.0

Main entry point for the application.
"""
import sys
from pathlib import Path

# Add this directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication
from controllers.main_controller import MainController
from controllers.noise_controller import NoiseController
from controllers.filter_controller import FilterController
from controllers.edge_controller import EdgeController
from controllers.frequency_controller import FrequencyController


def main():
    """
    Main entry point for the Image Studio application
    """
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Image Studio")
    app.setOrganizationName("Image Studio Team")
    
    # Create main window controller
    main_window = MainController()
    
    # Initialize sub-controllers
    noise_controller = NoiseController(main_window)
    filter_controller = FilterController(main_window)
    edge_controller = EdgeController(main_window)
    frequency_controller = FrequencyController(main_window)

    # Show the main window
    main_window.show()
    
    # Start the event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
