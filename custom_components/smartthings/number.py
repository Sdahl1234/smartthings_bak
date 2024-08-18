"""Support for numbers through the SmartThings cloud API."""
from __future__ import annotations

import logging

from collections import namedtuple
from collections.abc import Sequence

import asyncio

from typing import Literal

from . import Attribute, Capability
from pysmartthings.device import DeviceEntity

from homeassistant.components.number import NumberEntity, NumberMode

from homeassistant.components.sensor import SensorDeviceClass


from . import SmartThingsEntity
from .const import DATA_BROKERS, DOMAIN

from homeassistant.const import (
    AREA_SQUARE_METERS,
    CONCENTRATION_PARTS_PER_MILLION,
    LIGHT_LUX,
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfMass,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolume,
)

UNITS = {
    "C": UnitOfTemperature.CELSIUS,
    "F": UnitOfTemperature.FAHRENHEIT,
}

Map = namedtuple(
    "map",
    "attribute command name unit_of_measurement icon min_value max_value step mode",
)

_LOGGER = logging.getLogger(__name__)

CAPABILITY_TO_NUMBER = {
    Capability.thermostat_cooling_setpoint: [
        Map(
            Attribute.cooling_setpoint,
            "set_cooling_setpoint",
            "Cooling Setpoint",
            UnitOfTemperature.FAHRENHEIT,
            "mdi:thermometer",
            -8,
            500,
            1,
            NumberMode.AUTO,
        )
    ],
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add numbers for a config entries."""
    broker = hass.data[DOMAIN][DATA_BROKERS][config_entry.entry_id]
    numbers = []
    for device in broker.devices.values():
        for capability in broker.get_assigned(device.device_id, "number"):
        
            _LOGGER.debug(
                  "NB first number capability loop: %s: capability: %s ",
                   device.device_id,
                   capability,
            )                
                       
            maps = CAPABILITY_TO_NUMBER[capability]
            numbers.extend(
                [
                    SmartThingsNumber(
                        device,
                        "main",
                        m.attribute,
                        m.command,
                        m.name,
                        m.unit_of_measurement,
                        m.icon,
                        m.min_value,
                        m.max_value,
                        m.step,
                        m.mode,
                    )
                    for m in maps
                ]
            )
            

        device_capabilities_for_number = broker.get_assigned(device.device_id, "number")

        for component in device.components:
            _LOGGER.debug(
                  "NB component loop: %s: %s ",
                   device.device_id,
                   component,
            )                        
            for capability in device.components[component]:
                _LOGGER.debug(
                  "NB second number capability loop: %s: %s : %s ",
                   device.device_id,
                   component,
                   capability,
                )                
                if capability not in device_capabilities_for_number:
                    _LOGGER.debug(
                        "NB capability not found: %s: %s : %s ",
                        device.device_id,
                        component,
                        capability,
                    )                
                    continue

                
                maps = CAPABILITY_TO_NUMBER[capability]
                
                if component == "cooler":
                    numbers.extend(
                        [
	                    SmartThingsNumber(
	                        device,
	                        component,
	                        m.attribute,
	                        m.command,
	                        m.name,
	                        m.unit_of_measurement,
	                        m.icon,
	                        34,
	                        44,
	                        m.step,
	                        m.mode,
	                    )
                            for m in maps
                        ]
                    )    
                elif component == "freezer":
                    numbers.extend(
                        [
	                    SmartThingsNumber(
	                        device,
	                        component,
	                        m.attribute,
	                        m.command,
	                        m.name,
	                        m.unit_of_measurement,
	                        m.icon,
	                        -8,
	                        5,
	                        m.step,
	                        m.mode,
	                    )
                            for m in maps
                        ]
                    )    
                else:                                            
                    numbers.extend(
                        [
	                     SmartThingsNumber(
	                        device,
	                        component,
	                        m.attribute,
	                        m.command,
	                        m.name,
	                        m.unit_of_measurement,
	                        m.icon,
	                        m.min_value,
	                        m.max_value,
	                        m.step,
	                        m.mode,
	                    )
                            for m in maps
                        ]
                    )    
                            

    async_add_entities(numbers)


def get_capabilities(capabilities: Sequence[str]) -> Sequence[str] | None:
    """Return all capabilities supported if minimum required are present."""
    # Must have a numeric value that is selectable.
    
    _LOGGER.debug(
                  "NB number get_capabilities: %s ",
                   capabilities,
    )                    
    
    return [
        capability for capability in CAPABILITY_TO_NUMBER if capability in capabilities
    ]


class SmartThingsNumber(SmartThingsEntity, NumberEntity):
    """Define a SmartThings Number."""

    def __init__(
        self,
        device: DeviceEntity,
        component: str,
        attribute: str,
        command: str,
        name: str,
        unit_of_measurement: str | None,
        icon: str | None,
        min_value: str | None,
        max_value: str | None,
        step: str | None,
        mode: str | None,
    ) -> None:
        """Init the class."""
        super().__init__(device)
        self._component = component        
        self._attribute = attribute
        self._command = command
        self._name = name
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._icon = icon
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_mode = mode

    async def async_set_native_value(self, value: float) -> None:
        """Set the number value."""
        _LOGGER.debug(
                  "NB number set_native_value device: %s command: %s value: %s ",
                  self._device.device_id,
                  self._command,
                  value,
        )                  
        await getattr(self._device, self._command)(int(value), set_status=True)
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Return the name of the number."""
        if self._component == "main":
            return f"{self._device.label} {self._name}"        
        return f"{self._device.label} {self._component} {self._name}"       

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        if self._component == "main":
            return f"{self._device.device_id}.{self._attribute}"
        return f"{self._device.device_id}.{self._component}.{self._attribute}"
        

    @property
    def native_value(self) -> float:
        """Return  Value."""
#        return self._device.status.attributes[self._attribute].value

        """Return the state of the sensor."""
        _LOGGER.debug(
                  "NB Return the state component: %s ",
                   self._component,
        )                        
        if self._component == "main":
            value = self._device.status.attributes[self._attribute].value
        else:
            value = (
                self._device.status.components[self._component]
                .attributes[self._attribute]
                .value
            )
            
        _LOGGER.debug(
                  "NB Number Return the value for component: %s attribute: %s value: %s ",
                   self._component,
                   self._attribute,
                   value,
        )                                    

        return value

    @property
    def icon(self) -> str:
        """Return Icon."""
        return self._icon

    @property
    def native_min_value(self) -> float:
        """Define mimimum level."""
        return self._attr_native_min_value

    @property
    def native_max_value(self) -> float:
        """Define maximum level."""
        return self._attr_native_max_value

    @property
    def native_step(self) -> float:
        """Define stepping size"""
        return self._attr_native_step

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement"""
        unit = self._device.status.attributes[self._attribute].unit
        return UNITS.get(unit, unit) if unit else self._attr_native_unit_of_measurement

    @property
    def mode(self) -> Literal["auto", "slider", "box"]:
        """Return representation mode"""
        return self._attr_mode


