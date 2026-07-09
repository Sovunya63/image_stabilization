import sys
from .cli import build_parser, check_args
from .logging_config import get_logger


def main(argv=None):
    logger = get_logger()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        logger.info(f"Запуск команды: {args.command}")

        if not check_args(args, logger):
            return 1

        if args.command == "track":
            logger.info("Инициализация алгоритмов трекинга...")

            from .core.tracker import run_tracking_pipeline
            run_tracking_pipeline(args, logger)

        elif args.command == "analyze":
            logger.info("Запуск анализа метрик...")

            from .analytics.analysis import run_analysis
            run_analysis(args.file, logger, last_n=args.tail)

        logger.info("Завершено успешно.")
        return 0

    except KeyboardInterrupt:
        logger.info("Работа прервана пользователем.")
        return 0
    except Exception as e:
        logger.exception("Произошла критическая ошибка во время выполнения:")
        return 1


if __name__ == "__main__":
    sys.exit(main())