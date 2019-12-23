"""
"""
import signal
import time
import sys
import datetime

from pirc522 import RFID

class NFCReader:
    """
    NFCReader class
    """
    def __init__(self, api):
        self._rdr = RFID(pin_irq=None, antenna_gain=0x07)
        self._util = self._rdr.util()
        self._util.debug = True
        self._api = api
    
    def __del__(self): 
        self._rdr.cleanup()

    def run(self):
        last_uid = None
        last_not_detected = None
        while True:
            uid = self._rdr.read_id()
            if uid is not None:
                last_not_detected = None
                if last_uid != uid:
                    last_uid = uid
                    hex_uid = ':'.join('{:02x}'.format(x) for x in last_uid)
                    print('Detected UID: ' + hex_uid)
            else:
                if last_uid is not None:
                    now = datetime.datetime.now()
                    if last_not_detected is None:
                        last_not_detected = now
                    elif (now - last_not_detected).total_seconds() > 3.0:
                        hex_uid = ':'.join('{:02x}'.format(x) for x in last_uid)
                        print('Lost UID: ' + hex_uid)
                        last_uid = None
                        last_not_detected = None
                    
                    #if last_not_detected is not None:
                    #    print('Not detected: ' + str(now - last_not_detected) )

            time.sleep(0.01)