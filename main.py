from liflidar import Instrument
from liflidar import run_gui


def main():
    instrument = Instrument()
    run_gui(instrument)


if __name__ == "__main__":
    main()
