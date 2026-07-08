import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def run_analysis(input_path, main_logger):
    path = Path(input_path)

    if path.suffix == '.csv':
        df = pd.read_csv(input_path)
        avg = df.groupby('Mode')[['Fetch_ms', 'Analysis_ms', 'Compensate_ms', 'Render_ms']].mean()
        avg.plot(kind='bar', figsize=(10, 6), title='Средние временные затраты')
        plt.ylabel('Время (мс)')
        plt.tight_layout()
        plt.savefig(path.parent / "performance_plot.png")
        plt.show()

    elif path.suffix == '.log':
        data = []
        with open(input_path, 'r') as f:
            for line in f:
                if "X=" in line:
                    parts = line.split('|')[-1].split(',')
                    x = float(parts[0].replace('X=', '').replace('px', ''))
                    y = float(parts[1].replace('Y=', '').replace('px', ''))
                    data.append((x, y))

        df = pd.DataFrame(data, columns=['X', 'Y'])

        plt.figure(figsize=(8, 8))
        plt.plot(df['X'], df['Y'], alpha=0.5, label='Траектория смещения')
        plt.scatter(df['X'].iloc[0], df['Y'].iloc[0], color='green', label='Старт')
        plt.scatter(df['X'].iloc[-1], df['Y'].iloc[-1], color='red', label='Финиш')
        plt.title('Траектория "гуляния" камеры (смещение зоны)')
        plt.xlabel('Смещение X (пиксели)')
        plt.ylabel('Смещение Y (пиксели)')
        plt.legend()
        plt.grid(True)
        plt.savefig("stats/trajectory_plot.png")
        plt.show()