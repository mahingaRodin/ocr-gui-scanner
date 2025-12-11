# PyTesseract OCR Scanner

A GUI-based printed text scanner built with PyQt5 and PyTesseract for optical character recognition.

## Features

- **Image Loading**: Load images from disk (PNG, JPG, JPEG, BMP)
- **Live Camera Input**: Capture images directly from your webcam
- **ROI Selection**: Draw regions of interest for targeted OCR
- **Preprocessing Options**:
  - Grayscale conversion
  - Binary thresholding
  - Gaussian blur + thresholding
- **OCR Extraction**: Extract text using PyTesseract
- **Text Overlay**: Visualize detected text boundaries on the image

## Installation

### 1. Install Tesseract OCR

**Windows:**
- Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`
- Or update the path in `main.py` line 18

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 2. Install Python Dependencies

```bash
pip install PyQt5 pytesseract opencv-python pillow numpy
```

## Running the Application

```bash
python main.py
```

## Usage Guide

### Loading Images
1. Click **"Load Image"** button
2. Select an image file from your computer

### Using Camera
1. Click **"Start Camera"** to activate webcam
2. Click **"Stop Camera"** to deactivate

### ROI Selection
1. Click and drag on the image to select a region
2. The red dashed rectangle shows your selection
3. Click **"Clear ROI"** to remove selection
4. OCR will process only the selected region

### Preprocessing
1. Select preprocessing method from dropdown:
   - **None**: No preprocessing
   - **Grayscale**: Convert to grayscale
   - **Threshold**: Binary threshold (adjustable)
   - **Blur + Threshold**: Gaussian blur before threshold
2. Adjust threshold slider when using threshold methods

### Running OCR
1. Click **"Run OCR"** button
2. Extracted text appears in the right panel

### Text Overlay
1. Click **"Show Text Overlay"** to visualize detected text
2. Green boxes show word boundaries
3. Blue text labels show detected words

## File Structure

```
ocr-scanner/
│
├── main.py                 # Main application code
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## Requirements

- Python 3.7+
- PyQt5
- pytesseract
- opencv-python
- Pillow
- numpy
- Tesseract OCR (system installation)

## Troubleshooting

**"Tesseract not found" error:**
- Ensure Tesseract is installed
- Update the path in `main.py` line 18 to match your installation

**Camera not working:**
- Check camera permissions
- Ensure no other application is using the camera
- Try changing camera index from 0 to 1 in `cv2.VideoCapture(0)`

**Poor OCR results:**
- Try different preprocessing options
- Ensure text is clearly visible and well-lit
- Use ROI to focus on specific text regions
- Adjust threshold slider for better contrast

## Technical Details

This project demonstrates classical OCR using:
- **PyTesseract**: Open-source OCR engine
- **OpenCV**: Image preprocessing and manipulation
- **PyQt5**: GUI framework for user interface

The preprocessing pipeline improves OCR accuracy through:
- Noise reduction (Gaussian blur)
- Contrast enhancement (thresholding)
- Grayscale conversion

## License

MIT License - Free for educational and commercial use

## Author

Created for AI Without ML - Classical OCR Systems Assignment