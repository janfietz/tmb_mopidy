"""
mopidy json rpc api
"""
import requests
import json

import logging

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
        
        response = requests.post(self._url, json=payload).json()

        if 'error' in response:
            logging.error(response['error'])
            raise TypeError

        if response["jsonrpc"] == "2.0" and response["id"] == request_id and 'result' in response:
            return response["result"]
        
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
            self.__post("core.playback.pause", [])
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