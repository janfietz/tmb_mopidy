"""
"""
import time
import logging
import json
import re


from pirc522 import RFID

logger = logging.getLogger('nfc_reader')


def read_playlist_object(data):
    if data[0] != 0x01: # nfc well known format
        return None
    size = data[1]
    data_type = data[2]
    if data_type != 0x55: # waiting for type U
        return None
    _skip = data[3]
    #read data
    str_data = "".join([chr(item) for item in data[4:size+3]])
    return str_data

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
    Mifare_Ultralight_Auth = [0x49, 0x45, 0x4D, 0x4B, 0x41, 0x45, 0x52, 0x42, 0x21, 0x4E, 0x41, 0x43, 0x55, 0x4F, 0x59, 0x46]
    Default_Auth = [0xff, 0xff, 0xff, 0xff]
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

    def _load_m3u_playlist(self, uri):
        playlists = self._api.playlists_as_list()
        found = False
        for playlist in playlists:
            if re.search(uri, playlist['uri'], re.IGNORECASE):
                logger.info("Playlist : {} is available.".format(playlist['name']))
                self._status['playlist'] = playlist                
                items = self._api.playlists_get_items(playlist['uri'])
                uris = []
                for item in items:
                    uris.append(item['uri'])
                    logger.debug("Queue : add item {0} {1}".format(item['uri'], item['name']))
                self._api.tracklist_add(uris)
                
                found = True
        return False

    def _load_to_playlist(self, uri):
        uris = []
        result = self._api.library_lookup([uri])
        if result:
            logger.info("Uri : {} is available.".format(uri))
            self._status['playlist'] = uri
            
            for track_item in result:
                if "__model__" in track_item and track_item["__model__"] == "Track":
                    uris.append(track_item['uri'])
                    logger.debug("Queue : add item {0} {1}".format(track_item['uri'], track_item['name']))
        
        if len(uris) > 0:
            self._api.tracklist_add(uris)
            return True
        return False

    def __on_detected(self, uid, playlist_uri):
        hex_uid = ''.join('{:02x}'.format(x) for x in uid)
        logger.info("Detected : " + hex_uid)
        self._status['nfc_uuid'] = hex_uid

        found = False
        if playlist_uri.startwith('m3u'):
            found = self._load_m3u_playlist(playlist_uri)
        else:
            found = self._load_to_playlist(playlist_uri)

        if found:
            self._api.play()
        
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

        logger.info("Search for MFRC522 device")
        version = 0
        while version == 0:
            time.sleep(1)
            version = self._rdr.dev_read(0x37)
            self._rdr = RFID(pin_irq=None, antenna_gain=0x07, pin_rst=11)
            self._util = self._rdr.util()
        logger.info("MFRC522 device found. Start searching for tags.")

        while True:
            (error, data) = self._rdr.request()
            if not error:
                (error, uid) = self._rdr.anticoll()
                if not error:                    
                    if uid is not None:
                        last_not_detected = None
                        logger.debug("Request success")
                        if last_uid != uid:
                            card_data = []
                            read_error = False
                            for i in range(9):
                                (error, data) = self._rdr.read(6 + i*4)
                                if not error:
                                    card_data += data
                                else:
                                    read_error = True
                            if not read_error:
                                logger.debug("Card read UID: " + str(uid))
                                playlist = read_playlist_object(card_data)
                                if playlist is not None:
                                    logger.debug("Card read playlist: {0} ".format(playlist))
                                else:
                                    str_data = "".join(["{0:02x}({1})\n".format(item, chr(item)) for item in card_data])
                                    logger.warning("Card read data: {0} ".format(str_data))
                                last_uid = uid
                                self.__on_detected(last_uid, playlist)

            elif last_uid is not None:
                now = time.monotonic()
                if last_not_detected is not None:
                    if now - last_not_detected > 2: # 2s
                        self.__on_lost(last_uid)
                        last_uid = None
                else:
                    last_not_detected = now

            time.sleep(0.01)
