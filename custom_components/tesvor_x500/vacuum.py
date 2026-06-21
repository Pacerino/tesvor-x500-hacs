"""Vacuum entity for the Tesvor X500."""

from __future__ import annotations

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    BTN_GO_CHARGE,
    BTN_SMART,
    BTN_SPOT,
    BTN_STOP,
    DOMAIN,
    STATE_CHARGING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_RETURNING,
)
from .coordinator import TesvorCoordinator
from .entity import TesvorEntity

STATE_MAP = {
    STATE_DOCKED: VacuumActivity.DOCKED,
    STATE_CHARGING: VacuumActivity.DOCKED,
    STATE_RETURNING: VacuumActivity.RETURNING,
    STATE_ERROR: VacuumActivity.ERROR,
    "idle": VacuumActivity.IDLE,
    "hibernated": VacuumActivity.IDLE,
    "setting": VacuumActivity.IDLE,
    "cleaning": VacuumActivity.CLEANING,
    "spot_cleaning": VacuumActivity.CLEANING,
    "edge_cleaning": VacuumActivity.CLEANING,
    "zmode_cleaning": VacuumActivity.CLEANING,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TesvorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TesvorVacuum(coordinator)])


class TesvorVacuum(TesvorEntity, StateVacuumEntity):
    """Represents the Tesvor X500 as a Home Assistant vacuum."""

    _attr_name = None  # use device name
    _attr_supported_features = (
        VacuumEntityFeature.START
        | VacuumEntityFeature.STOP
        | VacuumEntityFeature.RETURN_HOME
        | VacuumEntityFeature.STATE
        | VacuumEntityFeature.BATTERY
        | VacuumEntityFeature.CLEAN_SPOT
    )

    def __init__(self, coordinator: TesvorCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_vacuum"

    @property
    def activity(self) -> VacuumActivity | None:
        if self.coordinator.state is None:
            return None
        return STATE_MAP.get(self.coordinator.state, VacuumActivity.IDLE)

    @property
    def battery_level(self) -> int | None:
        return self.coordinator.battery

    async def async_start(self) -> None:
        await self.coordinator.async_press_button(BTN_SMART)

    async def async_stop(self, **kwargs) -> None:
        await self.coordinator.async_press_button(BTN_STOP)

    async def async_pause(self) -> None:
        await self.coordinator.async_press_button(BTN_STOP)

    async def async_return_to_base(self, **kwargs) -> None:
        await self.coordinator.async_press_button(BTN_GO_CHARGE)

    async def async_clean_spot(self, **kwargs) -> None:
        await self.coordinator.async_press_button(BTN_SPOT)
