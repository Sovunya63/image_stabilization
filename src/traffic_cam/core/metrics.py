import cv2
import numpy as np
import time
import csv
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from traffic_cam.logging_config import get_logger

logger = get_logger("metrics")


class MetricsTracker:
    def __init__(self, csv_filename="logs/performance_metrics.csv"):
        self.smoothed_metrics = {}
        self.csv_filename = csv_filename
        self.t_loop_start = 0

        Path(self.csv_filename).parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.csv_filename, mode='w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.file)
        self.csv_writer.writerow(
            ['Mode', 'Decode_ms', 'Resize_ms', 'Fetch_ms', 'Analysis_ms', 'Compensate_ms', 'Render_ms', 'FPS'])

    def start_loop(self):
        self.t_loop_start = time.perf_counter()

    def update_and_draw(self, frame, current_metrics, mode):
        fps = 1.0 / (time.perf_counter() - self.t_loop_start + 1e-6)
        current_metrics['FPS'] = fps

        for k, v in current_metrics.items():
            self.smoothed_metrics[k] = self.smoothed_metrics.get(k, v) * 0.9 + v * 0.1

        self.csv_writer.writerow([
            mode,
            f"{current_metrics.get('Decode', 0):.2f}",
            f"{current_metrics.get('Resize', 0):.2f}",
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


def run_analysis(csv_path, main_logger):
    main_logger.info(f"Загрузка данных из {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        main_logger.error(f"Не удалось прочитать CSV: {e}")
        return

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 5))
    for mode in df['Mode'].unique():
        subset = df[df['Mode'] == mode]
        plt.plot(subset['FPS'].values, label=f'Режим: {mode}')

    plt.title('Стабильность FPS во времени')
    plt.xlabel('Номер кадра')
    plt.ylabel('FPS')
    plt.legend()

    output_path = "logs/fps_plot.png"
    plt.savefig(output_path)
    main_logger.info(f"График сохранен в {output_path}")
    plt.show()