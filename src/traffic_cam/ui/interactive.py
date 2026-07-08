
import cv2
from traffic_cam.logging_config import get_logger

logger = get_logger("ui")

class UIHandler:
    def __init__(self, window_name, target_points=4):
        self.window_name = window_name
        self.target_points = target_points
        self.points = []
        self.frame_copy = None
        self.setup_done = False

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and not self.setup_done and self.frame_copy is not None:
            self.points.append((x, y))
            cv2.circle(self.frame_copy, (x, y), 5, (0, 0, 255), -1)

            if len(self.points) > 1:
                cv2.line(self.frame_copy, self.points[-2], self.points[-1], (0, 0, 255), 2)

            if len(self.points) == self.target_points:
                cv2.line(self.frame_copy, self.points[-1], self.points[0], (0, 0, 255), 2)
                self.setup_done = True
                logger.info(f"Зона из {self.target_points} точек успешно задана.")