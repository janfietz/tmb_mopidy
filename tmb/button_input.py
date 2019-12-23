"""
"""

import RPi.GPIO as GPIO
import time
import collections

import logging


class Button:
    """
    Button class
    """
    def __init__(self, pin , action, targetQueue):        
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=self.__handler, bouncetime=30)
        self._action = action
        self._targeQueue = targetQueue

    def __handler(self, channel):
        self._targeQueue.append(dict(type = self._action, args = dict(pressed = GPIO.input(channel) == 1)))

class ButtonInput():
    """
    Button input class
    """

    def __init__(self, api):
        GPIO.setmode(GPIO.BCM)

        self._events = collections.deque()
        self._btn_next = Button(25, "next", self._events)
        self._btn_prev = Button(23, "prev", self._events)
        self._btn_main = Button(24, "main", self._events)
        self._btn_volup = Button(26, "volup", self._events)
        self._btn_voldown = Button(22, "voldown", self._events)
        self._api = api
    
    def __processEvent(self, event):
        try:
            getattr(self, "%s" % event['type'])(**event['args'])
        except AttributeError as e:
            logging.error(e)

    def run(self):
        try:
            while True:
                try:
                    processQueue = True
                    while processQueue:
                        self.__processEvent(self._events.popleft())
                except IndexError:
                    pass

                time.sleep(0.1)
        except KeyboardInterrupt:
            pass


    def next(self, pressed):
        if pressed:
            print("next")
            self._api.next()
    
    def prev(self, pressed):
        if pressed:
            print("prev")
            self._api.previous()

    def main(self, pressed):
        if pressed:
            state = self._api.get_state()
            if state == "stopped":
                self._api.play()
            if state == "playing":
                self._api.pause()
            if state == "paused":
                self._api.resume()
            print("main")            

    def volup(self, pressed):
        if pressed:
            try:
                volume = self._api.get_volume()
                self._api.set_volume(max(0, volume + 5))
            except TypeError:
                pass
            print("volup")

    def voldown(self, pressed):
        if pressed:
            try:
                volume = self._api.get_volume()
                self._api.set_volume(max(0, volume - 10))
            except TypeError:
                pass
            print("voldown")



