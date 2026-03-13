"""
Camera handler for live video capture.
"""
import cv2
import numpy as np
from typing import Optional


class CameraHandler:
    """Manages webcam video capture."""

    def __init__(self, camera_index: int = 0):
        # TODO: Store the camera_index parameter as an instance variable
        self._______ = _______

        # TODO: Initialize capture to None (will be set when camera starts)
        self._______ = None

        # TODO: Initialize running state flag to False
        self._______ = False

    def start(self) -> bool:
        """
        Start the camera capture.

        Returns:
            bool: True if camera started successfully, False if failed
        """
        # If camera is already running, return success
        if self._______ is not None:
            return True

        # TODO: Initialize OpenCV VideoCapture with the camera_index
        self.capture = cv2.___________(self._________)

        # TODO: Check if camera opened successfully using .isOpened() method
        if not self._______._________():
            # Failed - cleanup and return False
            self.capture = None
            return False

        # TODO: Set the is_running flag to True
        self._________ = True
        return True

    def stop(self):
        """
        Stop the camera capture and release resources.
        """
        # TODO: Set is_running flag to False
        self._________ = _______

        # Release camera resources if active
        if self._______ is not None:
            # TODO: Call the release() method to free the camera
            self._______._________()
            self.capture = None

    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read a single frame from the camera.

        Returns:
            np.ndarray: BGR image (H x W x 3), or None if failed
        """
        # Check if camera is initialized and running
        if self._______ is None or not self._________:
            return None

        # TODO: Read frame using capture.read() method
        # This returns (success_flag, frame_array)
        ret, frame = self._______._______()

        # Return frame if successful, otherwise None
        if ret:
            return frame
        return None

    def get_frame_size(self) -> tuple:
        """
        Get current frame dimensions.

        Returns:
            tuple: (width, height) in pixels
        """
        # Return default if not initialized
        if self._______ is None:
            return (640, 480)

        # TODO: Query camera properties using cv2.CAP_PROP_FRAME_WIDTH
        width = int(self._______.get(cv2._______))

        # TODO: Query camera properties using cv2.CAP_PROP_FRAME_HEIGHT
        height = int(self._______.get(cv2._______))

        return (width, height)

    