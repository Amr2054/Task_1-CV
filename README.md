# Image Studio - Project Structure

## Overview
Professional image processing application with a clean, modular architecture.

## Directory Structure

```
image_studio/
│
├── main.py                 # Application entry point
│
├── ui/                     # User interface files
│   └── main_window.ui      # Qt Designer UI file
│
├── controllers/            # UI Controllers (MVC pattern)
│   ├── __init__.py
│   ├── main_controller.py      # Main window and navigation
│   ├── noise_controller.py     # Noise operations UI logic
│   ├── filter_controller.py    # Filter operations UI logic
│   └── edge_controller.py      # Edge detection UI logic
│
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── image_loader.py         # Image loading and management
│   ├── noise_service.py        # Noise generation algorithms
│   ├── filter_service.py       # Image filtering algorithms
│   └── edge_service.py         # Edge detection algorithms
│
└── utils/                  # Utility functions
    ├── __init__.py
    └── image_utils.py          # Image conversion and helpers
```

## Architecture

### MVC Pattern
- **Model**: Services layer (`services/`)
- **View**: Qt Designer UI file (`ui/main_window.ui`)
- **Controller**: Controllers layer (`controllers/`)

### Layered Architecture
1. **Presentation Layer** (Controllers)
   - Handles UI events
   - Manages user interactions
   - Coordinates between services and UI

2. **Business Logic Layer** (Services)
   - Contains image processing algorithms
   - Independent of UI
   - Reusable across different interfaces

3. **Utility Layer** (Utils)
   - Common helper functions
   - Image format conversions
   - Validation functions

## Running the Application

```bash
cd image_studio
python main.py
```

## Features

### Noise Generation
- Uniform Noise
- Salt & Pepper Noise
- Gaussian Noise

### Image Filtering
- Average Filter
- Gaussian Filter
- Median Filter

### Edge Detection
- Canny Edge Detector
- Sobel Operator
- Prewitt Operator
- Roberts Operator

## Dependencies

- PyQt5 >= 5.15
- OpenCV (cv2) >= 4.5
- NumPy >= 1.20

## Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Controllers receive dependencies via constructor
3. **Loose Coupling**: Services are independent and reusable
4. **Testability**: Each layer can be tested independently

## Future Enhancements

- Histogram operations (equalization, normalization)
- Thresholding (local/global)
- Image enhancement operations
- Batch processing
- Export/save functionality
