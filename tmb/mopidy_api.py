"""
mopidy json rpc api
"""
import requests
import json

import logging

logger = logging.getLogger('mopidy_api')

class MopidyAPI:
    """
    Api class
    """

    def __init__(self, url):
        self._url = url
    
    def __post(self, method, params):
        request_id = 1
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": request_id,
        }
        logger.info("post: %s:%s", method, str(params))

        try:
            response = requests.post(self._url, json=payload).json()

            if 'error' in response:
                logger.error(response['error'])
                raise TypeError

            if response["jsonrpc"] == "2.0" and response["id"] == request_id and 'result' in response:
                logger.debug("result: %s", response["result"])
                return response["result"]
        except:
            raise TypeError

        raise TypeError

    def play(self):
        try:
            self.__post("core.playback.play", [])
        except TypeError:
            pass

    def pause(self):
        try:
            self.__post("core.playback.pause", [])
        except TypeError:
            pass
    
    def resume(self):
        try:
            self.__post("core.playback.resume", [])
        except TypeError:
            pass
    
    def next(self):
        try:
            self.__post("core.playback.next", [])
        except TypeError:
            pass
    
    def previous(self):
        try:
            self.__post("core.playback.previous", [])
        except TypeError:
            pass
    
    def get_volume(self):
        try:
            result = self.__post("core.playback.get_volume", [])
            return result
        except TypeError:
            pass
    
    def set_volume(self, volume):
        try:
            self.__post("core.playback.set_volume", [volume])
        except TypeError:
            pass

    def get_state(self):
        try:
            return self.__post("core.playback.get_state", [])
        except TypeError:
            pass
        return None

    def playlists_as_list(self):
        try:
            return self.__post("core.playlists.as_list", [])
        except TypeError:
            pass
        return None
    
    def playlists_get_items(self, uri):
        try:
            return self.__post("core.playlists.get_items", {'uri': uri})
        except TypeError:
            pass
        return None
    
    def playlists_create(self, name, uri_scheme=None):
        try:
            return self.__post("core.playlists.create", {'name': name, 'uri_scheme': uri_scheme})
        except TypeError:
            pass
        return None
    
    def tracklist_clear(self):
        try:
            return self.__post("core.tracklist.clear", [])
        except TypeError:
            pass
        return None

    def tracklist_add(self, uri):
        try:
            return self.__post("core.tracklist.add", {'uris': uri})
        except TypeError:
            pass
        return None

    def library_lookup(self, uris):
        try:
            return self.__post("core.library.lookup", {'uris': uris})
        except TypeError:
            pass
        return None