"""Support for Balboa Spa binary sensors."""
import logging

from .const import DOMAIN as BALBOA_DOMAIN
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOVING,
    BinarySensorDevice
)
from homeassistant.const import CONF_NAME
from . import BalboaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up of the spa is done through async_setup_entry."""
    pass


async def async_setup_entry(hass, entry, async_add_entities):
    spa = hass.data[BALBOA_DOMAIN][entry.entry_id]
    name = entry.data[CONF_NAME]
    devs = []

    devs.append(BalboaSpaBinarySensor(hass, spa, f'{name}-filter1', 'filter1'))
    devs.append(BalboaSpaBinarySensor(hass, spa, f'{name}-filter2', 'filter2'))

    if spa.have_circ_pump():
        devs.append(
            BalboaSpaBinarySensor(hass, spa, f'{name}-circ_pump', 'circ_pump')
        )
    async_add_entities(devs, True)


class BalboaSpaBinarySensor(BalboaEntity, BinarySensorDevice):
    """Representation of a Balboa Spa binary sensor device."""

    def __init__(self, hass, client, name, bsensor_key):
        """Initialize the binary sensor."""
        super().__init__(hass, client, name)
        self.bsensor_key = bsensor_key

    @property
    def is_on(self) -> bool:
        if 'filter' in self.bsensor_key:
            fmode = self._client.get_filtermode()
            if fmode == self._client.FILTER_OFF:
                return False
            if ('filter1' in self.bsensor_key
                and (fmode == self._client.FILTER_1 or
                     fmode == self._client.FILTER_1_2)):
                return True
            elif ('filter2' in self.bsensor_key and
                  fmode >= self._client.FILTER2):
                return True
            return False
        elif 'circ_pump' in self.bsensor_key:
            return self._client.get_circ_pump()
        return False

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_MOVING

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if 'circ_pump' in self.bsensor_key:
            return 'mdi:water-pump'
        return 'mdi:autorenew'
