import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="traffic_cam",
        description="Инструмент для компенсации смещения камеры и трекинга зон",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    track = subparsers.add_parser(
        "track",
        help="запуск процесса стабилизации и отслеживания"
    )
    track.add_argument("--source", type=str, default="0", help="путь к видео или RTSP (по умолчанию: 0)")
    track.add_argument("--no-hud", action="store_true", help="скрыть метрики производительности на экране")
    track.add_argument("--mask", type=str, default=None, help="путь к PNG маске")
    track.add_argument("--features", type=int, default=500, help="количество точек ORB (по умолчанию: 500)")
    track.add_argument("--width", type=int, default=0, help="ширина кадра (0 = исходная)")
    track.add_argument("--height", type=int, default=0, help="высота кадра (0 = исходная)")
    track.add_argument("--points", type=int, default=4, help="количество точек зоны (минимум 3)")

    analyze = subparsers.add_parser(
        "analyze",
        help="анализ файла метрик/лога и построение графиков"
    )
    analyze.add_argument("--file", required=True, help="путь к файлу")
    analyze.add_argument("--tail", type=int, default=100, help="количество последних записей для анализа")
    return parser


def check_args(args, logger):
    if args.command == "track":
        if args.points < 3:
            logger.error("Для создания замкнутой зоны нужно минимум 3 точки.")
            return False

        if args.mask:
            if not Path(args.mask).exists():
                logger.error(f"Файл маски не найден: {args.mask}")
                return False

        if not args.source.isdigit() and not args.source.startswith(('rtsp', 'http')):
            if not Path(args.source).exists():
                logger.error(f"Видеофайл не найден: {args.source}")
                return False

    return True