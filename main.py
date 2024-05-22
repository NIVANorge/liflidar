import logging

from liflidar import Instrument, run_gui


def main():
    logging.root.level = logging.DEBUG
    for name, logger in logging.root.manager.loggerDict.items():
        if 'asyncqt' in name:
            logger.level = logging.INFO

    instrument = Instrument
    run_gui(instrument)


if __name__ == "__main__":
    main()
