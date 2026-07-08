import cv2
import threading
import time
from traffic_cam.logging_config import get_logger

logger = get_logger("camera")


class ThreadedCamera:
    def __init__(self, src=0, target_width=0, target_height=0):
        if isinstance(src, str) and src.isdigit():
            src = int(src)

        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        orig_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.width = target_width if target_width > 0 else orig_w
        self.height = target_height if target_height > 0 else orig_h

        self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        is_stream = str(src).startswith('rtsp') or str(src).startswith('http') or isinstance(src, int)
        self.frame_delay = (1.0 / self.video_fps) if (self.video_fps > 0 and not is_stream) else 0

        logger.info(f"Камера инициализирована. Разрешение: {self.width}x{self.height}. FPS: {self.video_fps}")

        ret, self.frame = self.cap.read()
        if ret and (self.width != orig_w or self.height != orig_h):
            self.frame = cv2.resize(self.frame, (self.width, self.height))

        self.started = False
        self.read_lock = threading.Lock()

    def start(self):
        if self.started:
            return self
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        logger.info("Фоновый поток чтения камеры запущен.")
        return self

    def update(self):
        while self.started:
            t0 = time.perf_counter()
            ret, frame = self.cap.read()

            if ret:
                if frame.shape[1] != self.width or frame.shape[0] != self.height:
                    frame = cv2.resize(frame, (self.width, self.height))

                with self.read_lock:
                    self.frame = frame

                if self.frame_delay > 0:
                    elapsed = time.perf_counter() - t0
                    if self.frame_delay > elapsed:
                        time.sleep(self.frame_delay - elapsed)
            else:
                self.started = False

    def read(self):
        with self.read_lock:
            if self.frame is None:
                return False, None
            frame = self.frame.copy()
        return True, frame

    def stop(self):
        self.started = False
        if self.thread.is_alive():
            self.thread.join()
        self.cap.release()
        logger.info("Поток камеры остановлен.")