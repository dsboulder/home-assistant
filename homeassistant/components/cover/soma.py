# The domain of your component. Equal to the filename of your component.

import logging
import voluptuous as vol

from homeassistant.components.cover import CoverDevice, PLATFORM_SCHEMA, SUPPORT_OPEN, SUPPORT_CLOSE, SUPPORT_SET_POSITION, ATTR_POSITION

import homeassistant.helpers.config_validation as cv

import datetime

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ["soma3"]
REQUIREMENTS = ["bluepy==1.2.0"]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("mac"): cv.string,
    vol.Required("name"): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    dev = SomaBlind(config)
    add_devices([dev], True)


class SomaBlind(CoverDevice):
    def __init__(self, config):
        self._mac = config.get("mac")
        self._name = config.get("name")
        self._available = False
        self._position = None 
        self._opening = False
        self._closing = False
        self._last_updated = None

    @property
    def name(self):
        return self._name

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return 'window' 

    @property
    def available(self):
        return self._available

    @property
    def is_opening(self):
        return self._opening

    @property
    def is_closing(self):
        return self._closing

    @property
    def is_open(self):
        """Return if the cover is open."""
        if self._position is not None:
            return self._position == 100

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        if self._position is not None:
            return self._position == 0

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_OPEN | SUPPORT_CLOSE 

    def update(self):
        try:
            if self._needs_update():
               c = self._get_conn()
               self._position = 100 - c.get_position()
               c.disconnect()
               self._available = True
               self._last_updated = datetime.datetime.now()
               _LOGGER.error("Position set to "+str(self._position))
               if self.is_closed:
                    self._closing = False
               if self.is_open:
                     self._opening = False
            else:
                _LOGGER.error("Skipping SOMA Update this time: "+self._name)


        except EOFError as err:
            _LOGGER.error("Error updating SOMA: %s", err)
            self._available = False

    def _get_conn(self):
        return soma3.SomaBlind(self._mac)

    def _needs_update(self):
        if self.is_opening or self.is_closing or self._last_updated == None:
            return True

        delta = datetime.datetime.now() - self._last_updated 
        if delta.total_seconds() > 300:
            return True
        else:
            return False


    def open_cover(self, **kwargs):
        c = self._get_conn()
        c.open()
        c.disconnect()
        self._opening = True

    def close_cover(self, **kwargs):
        c = self._get_conn()
        c.close()
        c.disconnect()
        self._closing = True

    def set_cover_position(self, **kwargs):
        """Set the cover to a specific position."""
        c = self._get_conn()
        c.set_position(100 - kwargs[ATTR_POSITION])
        c.disconnect()

