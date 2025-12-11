import sys
import cv2
import numpy as np
import pytesseract
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QComboBox, QSlider, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ImageLabel(QLabel):
    roi_selected = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignCenter)
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.roi_rect = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.drawing = True
            
    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.end_point = event.pos()
            if self.start_point and self.end_point:
                x1, y1 = self.start_point.x(), self.start_point.y()
                x2, y2 = self.end_point.x(), self.end_point.y()
                self.roi_rect = QRect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                self.roi_selected.emit(self.roi_rect)
            self.update()
            
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.drawing and self.start_point and self.end_point:
            painter = QPainter(self)
            pen = QPen(Qt.red, 2, Qt.DashLine)
            painter.setPen(pen)
            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = self.end_point.x(), self.end_point.y()
            painter.drawRect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            
    def clear_roi(self):
        self.roi_rect = None
        self.start_point = None
        self.end_point = None
        self.update()

class OCRScanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image = None
        self.original_image = None
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.roi_rect = None
        self.detected_text_overlay = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('PyTesseract OCR Scanner')
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        left_panel = QVBoxLayout()
        
        self.image_label = ImageLabel()
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet("border: 2px solid black; background-color: #f0f0f0;")
        self.image_label.roi_selected.connect(self.on_roi_selected)
        left_panel.addWidget(self.image_label)
        
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton('Load Image')
        self.load_btn.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_btn)
        
        self.camera_btn = QPushButton('Start Camera')
        self.camera_btn.clicked.connect(self.toggle_camera)
        button_layout.addWidget(self.camera_btn)
        
        self.clear_roi_btn = QPushButton('Clear ROI')
        self.clear_roi_btn.clicked.connect(self.clear_roi)
        button_layout.addWidget(self.clear_roi_btn)
        
        left_panel.addLayout(button_layout)
        
        preprocess_layout = QHBoxLayout()
        preprocess_layout.addWidget(QLabel('Preprocessing:'))
        self.preprocess_combo = QComboBox()
        self.preprocess_combo.addItems(['None', 'Grayscale', 'Threshold', 'Blur + Threshold'])
        preprocess_layout.addWidget(self.preprocess_combo)
        
        preprocess_layout.addWidget(QLabel('Threshold:'))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(255)
        self.threshold_slider.setValue(127)
        self.threshold_slider.setEnabled(False)
        self.preprocess_combo.currentTextChanged.connect(self.on_preprocess_change)
        preprocess_layout.addWidget(self.threshold_slider)
        
        left_panel.addLayout(preprocess_layout)
        
        main_layout.addLayout(left_panel, 2)
        
        right_panel = QVBoxLayout()
        
        right_panel.addWidget(QLabel('Extracted Text:'))
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setMinimumWidth(400)
        right_panel.addWidget(self.text_display)
        
        self.ocr_btn = QPushButton('Run OCR')
        self.ocr_btn.clicked.connect(self.run_ocr)
        self.ocr_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;")
        right_panel.addWidget(self.ocr_btn)
        
        self.overlay_btn = QPushButton('Show Text Overlay')
        self.overlay_btn.clicked.connect(self.show_text_overlay)
        right_panel.addWidget(self.overlay_btn)
        
        main_layout.addLayout(right_panel, 1)
        
    def on_preprocess_change(self, text):
        self.threshold_slider.setEnabled(text in ['Threshold', 'Blur + Threshold'])
        
    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.jpeg *.bmp)')
        if filename:
            self.original_image = cv2.imread(filename)
            self.image = self.original_image.copy()
            self.display_image(self.image)
            self.image_label.clear_roi()
            
    def toggle_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                QMessageBox.warning(self, 'Error', 'Could not open camera')
                self.camera = None
                return
            self.timer.start(30)
            self.camera_btn.setText('Stop Camera')
        else:
            self.timer.stop()
            self.camera.release()
            self.camera = None
            self.camera_btn.setText('Start Camera')
            
    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            self.image = frame
            self.original_image = frame.copy()
            self.display_image(frame)
            
    def display_image(self, img):
        if len(img.shape) == 2:
            height, width = img.shape
            bytes_per_line = width
            q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            height, width, channel = img.shape
            bytes_per_line = 3 * width
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            q_img = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        
    def on_roi_selected(self, rect):
        self.roi_rect = rect
        
    def clear_roi(self):
        self.roi_rect = None
        self.image_label.clear_roi()
        
    def preprocess_image(self, img):
        method = self.preprocess_combo.currentText()
        
        if method == 'None':
            return img
        elif method == 'Grayscale':
            if len(img.shape) == 3:
                return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return img
        elif method == 'Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            _, thresh = cv2.threshold(gray, self.threshold_slider.value(), 255, cv2.THRESH_BINARY)
            return thresh
        elif method == 'Blur + Threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, self.threshold_slider.value(), 255, cv2.THRESH_BINARY)
            return thresh
        return img
        
    def run_ocr(self):
        if self.image is None:
            QMessageBox.warning(self, 'Warning', 'Please load an image or start camera first')
            return
            
        try:
            img_to_process = self.original_image.copy()
            
            if self.roi_rect:
                label_size = self.image_label.size()
                pixmap = self.image_label.pixmap()
                if pixmap:
                    scale_x = self.original_image.shape[1] / pixmap.width()
                    scale_y = self.original_image.shape[0] / pixmap.height()
                    
                    x = int(self.roi_rect.x() * scale_x)
                    y = int(self.roi_rect.y() * scale_y)
                    w = int(self.roi_rect.width() * scale_x)
                    h = int(self.roi_rect.height() * scale_y)
                    
                    x = max(0, min(x, self.original_image.shape[1]))
                    y = max(0, min(y, self.original_image.shape[0]))
                    w = min(w, self.original_image.shape[1] - x)
                    h = min(h, self.original_image.shape[0] - y)
                    
                    if w > 0 and h > 0:
                        img_to_process = self.original_image[y:y+h, x:x+w]
            
            processed = self.preprocess_image(img_to_process)
            text = pytesseract.image_to_string(processed)
            
            self.text_display.setText(text)
            
            if not text.strip():
                self.text_display.setText('[No text detected]')
                
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'OCR failed: {str(e)}')
            
    def show_text_overlay(self):
        if self.image is None:
            QMessageBox.warning(self, 'Warning', 'Please load an image first')
            return
            
        try:
            img_to_process = self.original_image.copy()
            
            if self.roi_rect:
                label_size = self.image_label.size()
                pixmap = self.image_label.pixmap()
                if pixmap:
                    scale_x = self.original_image.shape[1] / pixmap.width()
                    scale_y = self.original_image.shape[0] / pixmap.height()
                    
                    x = int(self.roi_rect.x() * scale_x)
                    y = int(self.roi_rect.y() * scale_y)
                    w = int(self.roi_rect.width() * scale_x)
                    h = int(self.roi_rect.height() * scale_y)
                    
                    x = max(0, min(x, self.original_image.shape[1]))
                    y = max(0, min(y, self.original_image.shape[0]))
                    w = min(w, self.original_image.shape[1] - x)
                    h = min(h, self.original_image.shape[0] - y)
                    
                    if w > 0 and h > 0:
                        img_to_process = self.original_image[y:y+h, x:x+w]
                        offset_x, offset_y = x, y
                    else:
                        offset_x, offset_y = 0, 0
                else:
                    offset_x, offset_y = 0, 0
            else:
                offset_x, offset_y = 0, 0
            
            processed = self.preprocess_image(img_to_process)
            
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            
            overlay = self.original_image.copy()
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                if int(data['conf'][i]) > 30:
                    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    x += offset_x
                    y += offset_y
                    cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(overlay, data['text'][i], (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            self.display_image(overlay)
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Overlay failed: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OCRScanner()
    window.show()
    sys.exit(app.exec_())