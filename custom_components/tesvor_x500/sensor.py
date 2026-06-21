"""Sensor entities for the Tesvor X500."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TesvorCoordinator
from .entity import TesvorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TesvorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            TesvorStateSensor(coordinator),
            TesvorPointsSensor(coordinator),
        ]
    )


class TesvorStateSensor(TesvorEntity, SensorEntity):
    _attr_name = "Raw State"
    _attr_icon = "mdi:robot-vacuum"

    def __init__(self, coordinator: TesvorCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_raw_state"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.state


class TesvorPointsSensor(TesvorEntity, SensorEntity):
    _attr_name = "Map Points"
    _attr_icon = "mdi:map-marker-path"
    _attr_native_unit_of_measurement = "points"

    def __init__(self, coordinator: TesvorCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_map_points"

    @property
    def native_value(self) -> int:
        return len(self.coordinator.points)
