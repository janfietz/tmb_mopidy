#!/usr/bin/env python
import signal
import sys

import argparse
import logging
import logging.handlers

from tmb.mopidy_api import MopidyAPI
import json

def end_read(signal,frame):
    global run
    print("\nCtrl+C captured, ending read.")
    run = False
    sys.exit()

signal.signal(signal.SIGINT, end_read)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prog', default='api', choices=['buttons', 'nfc', 'api'], help="Programm to start")
    parser.add_argument('--syslog', action='store_true', help="Log to system log")
    parser.add_argument('--loglevel', choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'), default='WARNING', help="Log level")
    parser.add_argument('--remote', default='localhost:6680', help="Mopidy host and port")
    parser.add_argument('--uri', help="Load uri to queue")
    args = parser.parse_args()

    api = MopidyAPI("http://{0}/mopidy/rpc".format(args.remote))


    log_handlers = []
    if args.syslog:
        log_handlers.append(logging.handlers.SysLogHandler(address='/dev/log'))
    else:
        log_handlers.append(logging.StreamHandler())

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

    if args.prog == "api":
        result = api.library_lookup([args.uri])
        print(json.dumps(result))


if __name__ == "__main__":
    main()