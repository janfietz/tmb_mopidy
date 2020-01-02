"""
"""

import RPi.GPIO as GPIO
import asyncio

import logging

logger = logging.getLogger('button_input')

def next(api, pressed):
    if pressed:
        logger.debug("Pressed next")
        api.next()
    else:
        logger.debug("Released next")

def prev(api, pressed):
    if pressed:
        logger.debug("Pressed prev")
        api.previous()
    else:
        logger.debug("Released prev")

def main(api, pressed):
    if pressed:
        logger.debug("Pressed main")
        state = api.get_state()
        if state == "stopped":
            api.play()
        if state == "playing":
            api.pause()
        if state == "paused":
            api.resume()
    else:
        logger.debug("Released main")

def volup(api, pressed):
    if pressed:
        logger.debug("Pressed volup")
        try:
            volume = api.get_volume()
            api.set_volume(max(0, volume + 5))
        except TypeError:
            pass
    else:
        logger.debug("Released volup")

def voldown(api, pressed):
    if pressed:
        logger.debug("Pressed voldown")
        try:
            volume = api.get_volume()
            api.set_volume(max(0, volume - 10))
        except TypeError:
            pass
    else:
        logger.debug("Released volup")

class ButtonInput():
    """
    Button input class
    """
    def __init__(self, api):        
        self._api = api        

    def __init_button(self, pin, funct):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        loop = asyncio.get_event_loop()

        def handler(channel):
            loop.call_soon_threadsafe(funct, self._api, GPIO.input(channel) == 1)

        GPIO.add_event_detect(pin, GPIO.BOTH, callback=handler, bouncetime=30)    
            
    def run(self):
        GPIO.setmode(GPIO.BCM)

        self.__init_button(25, next)
        self.__init_button(23, prev)
        self.__init_button(24, main)
        self.__init_button(26, volup)
        self.__init_button(22, voldown)

        asyncio.get_event_loop().run_forever()

        GPIO.cleanup()
    



