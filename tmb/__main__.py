#!/usr/bin/env python
import asyncio
import signal
import sys

import argparse
import logging
import logging.handlers

from tmb.mopidy_api import MopidyAPI

def end_read(signal,frame):
    global run
    print("\nCtrl+C captured, ending read.")
    run = False
    sys.exit()

signal.signal(signal.SIGINT, end_read)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prog', choices=['buttons', 'nfc'], help="Programm to start")
    parser.add_argument('--syslog', action='store_true', help="Log to system log")
    parser.add_argument('--loglevel', choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'), default='WARNING', help="Log level")

    api = MopidyAPI("http://localhost:6680/mopidy/rpc")

    args = parser.parse_args()

    log_handlers = []
    if args.syslog:
        log_handlers.append(logging.handlers.SysLogHandler(address='/dev/log'))

    logging.basicConfig(level=args.loglevel,
                        format='tmb[%(process)d]: %(name)s %(message)s',
                        handlers=log_handlers)

    if args.prog == "buttons":
        from tmb.button_input import ButtonInput 
        button_input = ButtonInput(api)
        button_input.run()

    if args.prog == "nfc":
        from tmb.nfc_reader import NFCReader
        nfc = NFCReader(api)
        nfc.run()

if __name__ == "__main__":
    main()