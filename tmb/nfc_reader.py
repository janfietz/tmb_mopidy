"""
"""
import signal
import time
import sys
import datetime
import logging
import json
import re

from pirc522 import RFID

logger = logging.getLogger('nfc_reader')

def write_status(status):
    """
    Write status to run dir
    """
    try:
        with open('/run/tmb_nfc_reader', 'w') as f:
            f.write(json.dumps(status, indent=2))
    except PermissionError:
        logger.warning("No permission to write run status.")

class NFCReader:
    """
    NFCReader class
    """
    def __init__(self, api):
        self._rdr = RFID(pin_irq=None, antenna_gain=0x07, pin_rst=11)
        self._util = self._rdr.util()
        self._util.debug = True
        self._api = api
        self._status = {}
    
    def __del__(self): 
        self._rdr.cleanup()

    def __on_detected(self, uid):
        hex_uid = ''.join('{:02x}'.format(x) for x in uid)
        logger.info("Detected : " + hex_uid)
        self._status['nfc_uuid'] = hex_uid
        playlists = self._api.playlists_as_list()
        found = False
        for playlist in playlists:
            if re.search(hex_uid, playlist['name'], re.IGNORECASE):
                logger.info("Playlist : {} is available.".format(hex_uid))
                self._status['playlist'] = playlist
                items = self._api.playlists_get_items(playlist['uri'])
                for item in items:
                    self._api.tracklist_add(item['uri'])
                self._api.play()
                found = True
        if not found:
            logger.info("Playlist : {} is not available.".format(hex_uid))
            self._status['playlist'] = None
        
        write_status(self._status)
    
    def __on_lost(self, uid):
        hex_uid = ':'.join('{:02x}'.format(x) for x in uid)
        logger.info("Lost : " + hex_uid)
        self._status['nfc_uuid'] = ""
        self._status['playlist'] = None
        self._api.tracklist_clear()
        write_status(self._status)

    def run(self):
        last_uid = None
        last_not_detected = None
        while True:
            uid = self._rdr.read_id()
            if uid is not None:
                last_not_detected = None
                if last_uid != uid:
                    last_uid = uid
                    self.__on_detected(last_uid)
                    
            else:
                if last_uid is not None:
                    now = datetime.datetime.now()
                    if last_not_detected is None:
                        last_not_detected = now
                    elif (now - last_not_detected).total_seconds() > 3.0:
                        self.__on_lost(last_uid)
                        last_uid = None
                        last_not_detected = None

            time.sleep(0.01)