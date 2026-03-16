import sys
import cv2
import numpy as np
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QScrollArea, QFileDialog,
    QStatusBar, QToolBar, QMessageBox, QInputDialog, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QImage, QPixmap, QAction

from face_detector import FaceDetector
from face_database import FaceDatabase
from camera_handler import CameraHandler

class FaceItemWidget(QFrame):
    rename_requested = Signal(str, str)
    
    def __init__(self, name: str, display_name: str, face_path: str):
        super().__init__()
        self.name = name
        self.display_name = display_name
        self.face_path = face_path
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(64, 64)
        self.thumbnail.setScaledContents(True)
        self.load_thumbnail()
        layout.addWidget(self.thumbnail)
        
        self.name_label = QLabel(display_name)
        self.name_label.setStyleSheet("font-size: 12pt;")
        layout.addWidget(self.name_label, 1)
        
        rename_btn = QPushButton("✏️")
        rename_btn.setFixedSize(30, 30)
        rename_btn.clicked.connect(self.on_rename_clicked)
        layout.addWidget(rename_btn)
        
        self.setLayout(layout)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)

    def load_thumbnail(self):
        if Path(self.face_path).exists():
            image = cv2.imread(self.face_path)
            if image is not None:
                image = cv2.resize(image, (64, 64))
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.thumbnail.setPixmap(QPixmap.fromImage(qt_image))

    def on_rename_clicked(self):
        new_name, ok = QInputDialog.getText(self, "Rename Face", "Enter new name:", text=self.display_name)
        if ok and new_name and new_name != self.display_name:
            self.rename_requested.emit(self.name, new_name)
            self.name_label.setText(new_name)
            self.display_name = new_name

class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detector = FaceDetector()
        self.database = FaceDatabase("data")
        self.camera = CameraHandler()
        
        self.current_mode = None
        self.current_image = None
        self.current_face_locations = []
        self.current_face_landmarks = None
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_feed)
        
        self.setup_ui()
        self.load_saved_faces()

    def setup_ui(self):
        self.setWindowTitle("Real-Time Face Recognition")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        left_layout = QVBoxLayout()
        toolbar = QToolBar()
        
        self.live_btn = QPushButton("📹 Live Feed")
        self.live_btn.clicked.connect(self.start_live_feed)
        toolbar.addWidget(self.live_btn)
        
        self.upload_btn = QPushButton("📁 Upload Image")
        self.upload_btn.clicked.connect(self.upload_image)
        toolbar.addWidget(self.upload_btn)
        
        self.save_face_btn = QPushButton("💾 Save Face")
        self.save_face_btn.clicked.connect(self.save_current_face)
        self.save_face_btn.setEnabled(False)
        toolbar.addWidget(self.save_face_btn)
        
        left_layout.addWidget(toolbar)
        
        self.display_label = QLabel("Click 'Live Feed' or 'Upload Image' to start")
        self.display_label.setMinimumSize(800, 600)
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setStyleSheet("background-color: #2b2b2b; color: white;")
        left_layout.addWidget(self.display_label)
        
        main_layout.addLayout(left_layout, 3)
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Search Faces:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self.on_search_changed)
        right_layout.addWidget(self.search_input)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumWidth(300)
        
        self.faces_container = QWidget()
        self.faces_layout = QVBoxLayout(self.faces_container)
        self.faces_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.faces_container)
        right_layout.addWidget(self.scroll_area)
        
        main_layout.addLayout(right_layout, 1)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def start_live_feed(self):
        if self.current_mode == 'live':
            self.timer.stop()
            self.camera.stop()
            self.current_mode = None
            self.live_btn.setText("📹 Live Feed")
            self.display_label.setText("Live feed stopped")
            self.save_face_btn.setEnabled(False)
            return
        
        if self.camera.start():
            self.current_mode = 'live'
            self.timer.start(30)
            self.live_btn.setText("⏹️ Stop Feed")
            self.status_bar.showMessage("Live feed started")
        else:
            QMessageBox.warning(self, "Camera Error", "Failed to start camera")

    def update_live_feed(self):
        frame = self.camera.read_frame()
        if frame is None: return
        
        self.current_image = frame.copy()
        self.current_face_locations, self.current_face_landmarks = self.detector.detect_faces(frame)
        
        if self.current_face_locations:
            frame = self.detector.draw_face_boxes(frame, self.current_face_locations)
            self.save_face_btn.setEnabled(True)
            
            # Recognition logic
            encoding = self.detector.get_face_encoding(self.current_image, self.current_face_locations[0])
            if encoding is not None:
                match = self.database.find_closest_match(encoding)
                if match:
                    name, dist = match
                    self.status_bar.showMessage(f"Match: {name} ({dist:.3f})")
                else:
                    self.status_bar.showMessage("No match found")
        else:
            self.save_face_btn.setEnabled(False)

        if self.current_face_landmarks:
            frame = self.detector.draw_face_landmarks(frame, self.current_face_landmarks)
        
        self.display_frame(frame)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not file_path: return
        
        if self.current_mode == 'live': self.start_live_feed()
        
        self.current_mode = 'image'
        image = cv2.imread(file_path)
        if image is None: return
        
        self.current_image = image.copy()
        self.current_face_locations, self.current_face_landmarks = self.detector.detect_faces(image)
        
        if self.current_face_locations:
            image = self.detector.draw_face_boxes(image, self.current_face_locations)
            self.save_face_btn.setEnabled(True)
        
        if self.current_face_landmarks:
            image = self.detector.draw_face_landmarks(image, self.current_face_landmarks)
            
        self.display_frame(image)

    def save_current_face(self):
        if not self.current_face_locations or self.current_image is None: return
        name, ok = QInputDialog.getText(self, "Save Face", "Enter person's name:")
        if ok and name:
            face_img = self.detector.crop_face(self.current_image, self.current_face_locations[0])
            encoding = self.detector.get_face_encoding(self.current_image, self.current_face_locations[0])
            if encoding is not None and self.database.save_face(name, face_img, encoding):
                QMessageBox.information(self, "Success", f"Saved {name}")
                self.load_saved_faces()

    def load_saved_faces(self, search_query: str = ""):
        for i in reversed(range(self.faces_layout.count())):
            self.faces_layout.itemAt(i).widget().deleteLater()
        
        faces = self.database.search_faces(search_query) if search_query else self.database.get_all_faces()
        for face in faces:
            widget = FaceItemWidget(face['name'], face['display_name'], face['face_path'])
            widget.rename_requested.connect(self.on_face_renamed)
            self.faces_layout.addWidget(widget)

    def on_search_changed(self, text):
        self.load_saved_faces(text)

    def on_face_renamed(self, old, new):
        self.database.rename_face(old, new)

    def display_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        # Simple scaling to fit label
        label_w, label_h = self.display_label.width(), self.display_label.height()
        resized = cv2.resize(rgb_frame, (label_w, label_h), interpolation=cv2.INTER_AREA)
        qt_img = QImage(resized.data, label_w, label_h, ch * label_w, QImage.Format_RGB888)
        self.display_label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, event):
        self.timer.stop()
        self.camera.stop()
        self.detector.cleanup()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()