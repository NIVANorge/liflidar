# Copyright 2024 The Liflidar Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging

from liflidar import Instrument, run_gui


def main():
    parser = argparse.ArgumentParser(description='Liflidar.')
    parser.add_argument('--debug', action='store_true', help='Enable logging to debug level.')

    args = parser.parse_args()

    if args.debug:
        logging.root.level = logging.DEBUG
    for name, logger in logging.root.manager.loggerDict.items():
        if 'asyncqt' in name:
            logger.level = logging.INFO

    instrument = Instrument
    run_gui(instrument)


if __name__ == "__main__":
    main()
