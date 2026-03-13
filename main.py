"""
Main GUI application for face recognition.
Built with PySide6 (Qt for Python).
"""
import sys
import cv2
import numpy as np
from pathlib import Path

# TODO: Import Qt widgets - fill in the missing widget names
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QScrollArea, QFileDialog,
    QStatusBar, QToolBar, QMessageBox, QInputDialog, QFrame
)

# TODO: Import Qt core classes
from PySide6.QtCore import Qt, QTimer, Signal, QSize

# TODO: Import Qt GUI classes
from PySide6.QtGui import QImage, QPixmap, QAction

# TODO: Import our custom modules
from face_detector import _______
from face_database import _______
from camera_handler import _______


class FaceItemWidget(QFrame):
    """Widget representing a single saved face in the list."""

    # TODO: Define a signal that emits two strings (old_name, new_name)
    rename_requested = _______(str, str)

    def __init__(self, name: str, display_name: str, face_path: str):
        super().__init__()

        # TODO: Store parameters as instance variables
        self._______ = name
        self._______ = display_name
        self._______ = face_path

        # Create horizontal layout
        layout = _______()
        layout.setContentsMargins(5, 5, 5, 5)

    # TODO: Create thumbnail label with fixed size 64x64
    self.thumbnail = _______()
    self.thumbnail.setFixedSize(_______, _______)
    self.thumbnail.setScaledContents(True)
    self.load_thumbnail()
    layout.addWidget(self.thumbnail)

    # TODO: Create name label with display_name
    self.name_label = _______(display_name)
    self.name_label.setStyleSheet("font-size: 12pt;")
    layout.addWidget(self.name_label, 1)  # Stretch factor

    # TODO: Create rename button with emoji pencil "✏️"
    rename_btn = _______("✏️")
    rename_btn.setFixedSize(30, 30)
    rename_btn.clicked.connect(self.on_rename_clicked)
    layout.addWidget(rename_btn)

    self.setLayout(layout)
    self.setFrameStyle(QFrame.Box)
    self.setLineWidth(1)

    def load_thumbnail(self):
        """Load and display face thumbnail."""
        # TODO: Check if face_path exists using Path().exists()
        if _______(self.face_path)._______():
            # TODO: Load image using cv2.imread()
            image = cv2._______(self.face_path)

            if image is not None:
                # TODO: Resize to 64x64 using cv2.resize()
                image = cv2._______(image, (64, 64))

                # TODO: Convert BGR to RGB for Qt
                rgb_image = cv2._______(image, cv2.COLOR_________)

                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w

                # TODO: Create QImage from numpy array data
                qt_image = _______(rgb_image.data, w, h, bytes_per_line,
                                   QImage.Format_RGB888)

                # TODO: Set pixmap on thumbnail label
                self.thumbnail.setPixmap(_______.fromImage(qt_image))

    def on_rename_clicked(self):
        """Handle rename button click."""
        # TODO: Show input dialog using QInputDialog.getText()
        # Parameters: parent, title, label, text=default_value
        new_name, ok = _______._______(
            self,
            "Rename Face",
            "Enter new name:",
            text=self._______
        )

        # TODO: Check if user clicked OK and name is different
        if ok and new_name and new_name != self._______:
            # TODO: Emit the rename_requested signal
            self._______.emit(self.name, new_name)

            # Update label
            self.name_label.setText(new_name)
            self.display_name = new_name


class FaceRecognitionApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # TODO: Initialize core components
        self.detector = _______()
        self.database = _______("data")
        self.camera = _______()

        # TODO: Initialize state variables
        self.current_mode = None  # 'live', 'image', or None
        self.current_image = None
        self.current_face_locations = []
        self.current_face_landmarks = None

        # TODO: Create QTimer for live feed updates
        self.timer = _______()
        self.timer.timeout.connect(self.update_live_feed)

        # Setup UI and load faces
        self.setup_ui()
        self.load_saved_faces()

    def setup_ui(self):
        """Initialize the user interface."""

        # TODO: Set window title
        self.setWindowTitle("_______")

        # TODO: Set window geometry (x, y, width, height)
        self.setGeometry(100, 100, 1200, 800)

        # TODO: Create and set central widget
        central_widget = _______()
        self.setCentralWidget(central_widget)

        # TODO: Create main horizontal layout
        main_layout = _______()
        central_widget.setLayout(main_layout)

        # TODO: Create left vertical layout for display area
        left_layout = _______()

    # Create toolbar
    toolbar = QToolBar()

    # TODO: Create Live Feed button with emoji "📹"
    self.live_btn = _______("📹 Live Feed")
    self.live_btn.clicked.connect(self.start_live_feed)
    toolbar.addWidget(self.live_btn)

    # TODO: Create Upload button with emoji "📁"
    self.upload_btn = _______("📁 Upload Image")
    self.upload_btn.clicked.connect(self.upload_image)
    toolbar.addWidget(self.upload_btn)

    # TODO: Create Save Face button with emoji "💾"
    self.save_face_btn = _______("💾 Save Face")
    self.save_face_btn.clicked.connect(self.save_current_face)
    self.save_face_btn.setEnabled(False)  # Disabled initially
    toolbar.addWidget(self.save_face_btn)

    left_layout.addWidget(toolbar)

    # TODO: Create display label for video/image
    self.display_label = _______()
    self.display_label.setMinimumSize(800, 600)
    self.display_label.setAlignment(Qt._______)
    self.display_label.setStyleSheet("background-color: #2b2b2b; color: white;")
    self.display_label.setText("Click 'Live Feed' or 'Upload Image' to start")
    left_layout.addWidget(self.display_label)

    # TODO: Add left_layout to main_layout with stretch factor 3
    main_layout.addLayout(left_layout, _______)

    # TODO: Create right vertical layout
    right_layout = _______()

    # Search label
    search_label = QLabel("Search Faces:")
    right_layout.addWidget(search_label)

    # TODO: Create search input field
    self.search_input = _______()
    self.search_input.setPlaceholderText("Type to search...")
    self.search_input.textChanged.connect(self.on_search_changed)
    right_layout.addWidget(self.search_input)

    # TODO: Create scroll area for faces list
    self.scroll_area = _______()
    self.scroll_area.setWidgetResizable(True)
    self.scroll_area.setMinimumWidth(300)

    # TODO: Create container widget for faces
    self.faces_container = _______()
    self.faces_layout = _______()
    self.faces_layout.setAlignment(Qt.AlignTop)
    self.faces_container.setLayout(self.faces_layout)

    self.scroll_area.setWidget(self.faces_container)
    right_layout.addWidget(self.scroll_area)

    # TODO: Add right_layout to main_layout with stretch factor 1
    main_layout.addLayout(right_layout, _______)

    # TODO: Create status bar
    self.status_bar = _______()
    self.setStatusBar(self.status_bar)
    self.status_bar.showMessage("Ready")

    def start_live_feed(self):
        """Start or stop live camera feed."""

        # TODO: Check if currently in live mode
        if self.current_mode == '_______':
            # Stop camera
            self.timer.stop()
            self.camera.stop()
            self.current_mode = None
            self.live_btn.setText("📹 Live Feed")
            self.display_label.setText("Live feed stopped")
            self.save_face_btn.setEnabled(False)
            self.status_bar.showMessage("Live feed stopped")
            return

        # TODO: Try to start camera
        if self.camera._______():
            self.current_mode = '_______'

            # TODO: Start timer with 30ms interval (~30 FPS)
            self.timer.start(_______)

            self.live_btn.setText("⏹️ Stop Feed")
            self.status_bar.showMessage("Live feed started")
        else:
            # TODO: Show warning message box
            _______.warning(self, "Camera Error", "Failed to start camera")

    def update_live_feed(self):
            """Update live feed frame (called by timer)."""

            # TODO: Read frame from camera
            frame = self.camera._______()
            if frame is None:
                return

            # TODO: Store copy as current_image
            self.current_image = frame._______()

            # TODO: Detect faces and landmarks
            self.current_face_locations, self.current_face_landmarks = \
                self.detector._______(frame)

            # TODO: Draw face boxes if faces detected
            if self.current_face_locations:
                frame = self.detector._______(frame, self.current_face_locations)
                self.save_face_btn.setEnabled(_______)
            else:
                self.save_face_btn.setEnabled(_______)

            # TODO: Draw landmarks if detected
            if self.current_face_landmarks:
                frame = self.detector._______(frame, self.current_face_landmarks)

            # TODO: Try to match first face
            if self.current_face_locations:
                first_face = self.current_face_locations[0]

                # TODO: Get face encoding
                encoding = self.detector._______(self.current_image, first_face)

                if encoding is not None:
                    # TODO: Find closest match in database
                    match = self.database._______(encoding)

                    if match:
                        name, distance = match
                        self.status_bar.showMessage(f"Match: {name} (distance: {distance:.3f})")
                    else:
                        self.status_bar.showMessage("No match found")

            # TODO: Display frame
            self._______(frame)

    def upload_image(self):
            """Upload and process a static image."""

            # TODO: Open file dialog using QFileDialog.getOpenFileName()
            file_path, _ = _______._______(
                self,
                "Select Image",
                "",
                "Images (*.png *.jpg *.jpeg *.bmp)"
            )

            if not file_path:
                return  # User cancelled

            # Stop live feed if running
            if self.current_mode == 'live':
                self.timer.stop()
                self.camera.stop()
                self.live_btn.setText("📹 Live Feed")

            self.current_mode = '_______'

            # TODO: Load image using cv2.imread()
            image = cv2._______(file_path)
            if image is None:
                QMessageBox.warning(self, "Error", "Failed to load image")
                return

            # TODO: Store copy and detect faces
            self.current_image = image._______()
            self.current_face_locations, self.current_face_landmarks = \
                self.detector._______(image)

            # TODO: Draw boxes if faces found
            if self.current_face_locations:
                image = self.detector._______(image, self.current_face_locations)
                self.save_face_btn.setEnabled(True)
            else:
                self.save_face_btn.setEnabled(False)
                _______.information(self, "No Faces", "No faces detected in image")

            # TODO: Draw landmarks
            if self.current_face_landmarks:
                image = self.detector._______(image, self.current_face_landmarks)

            # TODO: Try to match first face
            if self.current_face_locations:
                first_face = self.current_face_locations[0]
                encoding = self.detector._______(self.current_image, first_face)

                if encoding is not None:
                    match = self.database._______(encoding)
                    if match:
                        name, distance = match
                        self.status_bar.showMessage(f"Match: {name} (distance: {distance:.3f})")
                    else:
                        self.status_bar.showMessage("No match found")

            # Display image
            self.display_frame(image)

    def save_current_face(self):
        """Save the first detected face to the database."""

        # TODO: Validate we have a face
        if not self.current_face_locations or self.current_image is None:
            QMessageBox.warning(self, "No Face", "No face detected to save")
            return

        # TODO: Prompt user for name using QInputDialog.getText()
        name, ok = _______._______(self, "Save Face", "Enter person's name:")
        if not ok or not name:
            return

        # Get first face
        first_face = self.current_face_locations[0]

        # TODO: Crop face using detector
        face_image = self.detector._______(self.current_image, first_face)

        # TODO: Generate encoding
        encoding = self.detector._______(self.current_image, first_face)
        if encoding is None:
            QMessageBox.warning(self, "Error", "Failed to generate face encoding")
            return

        # TODO: Save to database
        if self.database._______(name, face_image, encoding):
            QMessageBox.information(self, "Success", f"Face saved as '{name}'")
            self.load_saved_faces()  # Refresh list
        else:
            QMessageBox.warning(self, "Error", "Failed to save face")

    def load_saved_faces(self, search_query: str = ""):
        """Load and display saved faces in the sidebar."""

        # TODO: Clear existing widgets (iterate in reverse)
        for i in reversed(range(self.faces_layout.count())):
            widget = self.faces_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # TODO: Get faces from database (filtered or all)
        if search_query:
            faces = self.database._______(search_query)
        else:
            faces = self.database._______()

        # TODO: Create widget for each face
        for face in faces:
            widget = FaceItemWidget(
                face['_______'],
                face['_______'],
                face['_______']
            )
            # TODO: Connect rename signal
            widget.rename_requested.connect(self.on_face_renamed)
            self.faces_layout.addWidget(widget)

    def on_search_changed(self, text: str):
        """Handle search input changes."""
        # TODO: Reload faces with filter
        self._______(text)

    def on_face_renamed(self, old_name: str, new_name: str):
        """Handle face rename request."""
        # TODO: Rename in database
        if self.database._______(old_name, new_name):
            self.status_bar.showMessage(f"Renamed to '{new_name}'")

    def display_frame(self, frame: np.ndarray):
        """Display a frame in the GUI."""

        # TODO: Convert BGR to RGB
        rgb_frame = cv2._______(frame, cv2.COLOR_________)

        # Calculate resize to fit display
        h, w, ch = rgb_frame.shape
        display_width = self.display_label.width()
        display_height = self.display_label.height()

        # Calculate aspect ratio
        aspect = w / h
        if display_width / display_height > aspect:
            new_height = display_height
            new_width = int(new_height * aspect)
        else:
            new_width = display_width
            new_height = int(new_width / aspect)

        # TODO: Resize frame using cv2.resize()
        resized = cv2._______(rgb_frame, (new_width, new_height))
        h, w, ch = resized.shape

        # TODO: Convert to Qt image
        bytes_per_line = ch * w
        qt_image = _______(resized.data, w, h, bytes_per_line,
                           QImage.Format_RGB888)

        # TODO: Set pixmap on display label
        self.display_label.setPixmap(_______.fromImage(qt_image))

    def closeEvent(self, event):
        """Handle window close event - cleanup resources."""
        # TODO: Stop timer
        self.timer._______()

        # TODO: Stop camera
        self.camera._______()

        # TODO: Cleanup detector
        self.detector._______()

        # TODO: Accept event to allow close
        event._______()

    def main():
        """Main entry point for the application."""

        # TODO: Create Qt application
        app = _______(sys.argv)

        # TODO: Create main window
        window = _______()

        # TODO: Show window
        window._______()

        # TODO: Start event loop and exit with return code
        sys.exit(app._______())

    if __name__ == "__main__":
        main()

