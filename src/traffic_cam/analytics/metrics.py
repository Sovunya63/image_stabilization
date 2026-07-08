import cv2
import numpy as np
import time
import csv
from pathlib import Path
from traffic_cam.logging_config import get_logger

logger = get_logger("metrics")


class MetricsTracker:
    def __init__(self, csv_filename="stats/perf_metrics.csv"):
        self.smoothed_metrics = {}
        self.csv_filename = csv_filename
        self.prev_frame_time = time.perf_counter()

        Path(self.csv_filename).parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.csv_filename, mode='w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.file)
        self.csv_writer.writerow(['Mode', 'Fetch_ms', 'Analysis_ms', 'Compensate_ms', 'Render_ms', 'FPS'])

    def start_loop(self):
        pass
    def update_and_draw(self, frame, current_metrics, mode):
        now = time.perf_counter()
        fps = 1.0 / (now - self.prev_frame_time + 1e-6)
        self.prev_frame_time = now

        current_metrics['FPS'] = fps

        for k, v in current_metrics.items():
            self.smoothed_metrics[k] = self.smoothed_metrics.get(k, v) * 0.9 + v * 0.1

        self.csv_writer.writerow([
            mode,
            f"{current_metrics.get('Fetch', 0):.2f}",
            f"{current_metrics.get('Analysis', 0):.2f}",
            f"{current_metrics.get('Compensate', 0):.2f}",
            f"{current_metrics.get('Render', 0):.2f}",
            f"{fps:.2f}"
        ])

        self._draw_hud(frame, self.smoothed_metrics)

    def _draw_hud(self, frame: np.ndarray, metrics: dict) -> None:
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (280, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        cv2.putText(frame, "METRICS (ms)", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        y = 65
        for key, val in metrics.items():
            color = (0, 255, 0) if key == 'FPS' and val >= 25 else (255, 255, 255)
            text = f"{key}: {val:.1f}" if key == 'FPS' else f"{key}: {val:.1f} ms"
            cv2.putText(frame, text, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y += 22

    def close(self):
        self.file.close()