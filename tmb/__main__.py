#!/usr/bin/env python

import signal
import sys

import argparse

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

    api = MopidyAPI("http://localhost:6680/mopidy/rpc")

    args = parser.parse_args()
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