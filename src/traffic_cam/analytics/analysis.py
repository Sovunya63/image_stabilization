import pandas as pd
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from pathlib import Path


def run_analysis(csv_path, main_logger):
    main_logger.info(f"Загрузка данных из {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        main_logger.error(f"Не удалось прочитать CSV: {e}")
        return

    avg_metrics = df.groupby('Mode')[['Fetch_ms', 'Analysis_ms', 'Compensate_ms', 'Render_ms']].mean()

    avg_metrics.plot(kind='bar', figsize=(10, 6), title='Средние временные затраты по этапам (мс)')
    plt.ylabel('Время (мс)')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    csv_file = Path(csv_path)
    output_path = csv_file.parent / f"{csv_file.stem}_plot.png"

    plt.savefig(output_path)
    main_logger.info(f"График успешно сохранен в {output_path}")
    plt.show()