class CameraVision:
    """
    Handles:
    - Connecting to camera
    - Capturing image
    - Processing maze image
    - Converting maze into a grid
    """

    def __init__(self, camera_id=0, debug_folder="debug"):
        self.camera_id = camera_id
        self.debug_folder = debug_folder
        self.camera = None

    def connect(self):
        """Connect to the camera."""
         import cv2
        self.camera = cv2.VideoCapture(self.camera_id)
        if not self.camera.isopened():
            raise RuntimeError(f"Could not open camera with ID {self.camera_id}")
        pass

    def capture_frame(self):
        """Capture a single image frame from the camera."""
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from camera")
        return frame

    def preprocess(self, frame):
        """Clean/normalize the image before parsing."""
        pass

    def segment_maze(self, frame):
        """
        Convert image into a simplified representation:
        - walls vs path
        - binary mask
        """
        pass

    def extract_grid(self, segmented_frame, grid_width, grid_height):
        """
        Convert segmented maze into a grid.

        Returns:
            grid: 2D array-like structure
                  0 = open path
                  1 = wall
        """
        pass

    def release(self):
        """Disconnect camera safely."""
        if self.camera is not None:
            self.camera.release()
