"""Select entities for the Tesvor X500 (mop intensity, fan)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAN_OPTIONS, MOP_OPTIONS, SEL_FAN, SEL_MOP
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
            TesvorSelect(
                coordinator, "mop", "Mop Intensity", "mdi:water-percent", SEL_MOP, MOP_OPTIONS
            ),
            TesvorSelect(
                coordinator, "fan", "Suction Power", "mdi:fan", SEL_FAN, FAN_OPTIONS
            ),
        ]
    )


class TesvorSelect(TesvorEntity, SelectEntity):
    """Optimistic select that forwards the option to the ESPHome select.

    The firmware does not reliably report these back, so state is optimistic.
    """

    def __init__(
        self,
        coordinator: TesvorCoordinator,
        key: str,
        name: str,
        icon: str,
        suffix: str,
        options: list[str],
    ) -> None:
        super().__init__(coordinator)
        self._suffix = suffix
        self._attr_name = name
        self._attr_icon = icon
        self._attr_options = options
        self._attr_unique_id = f"{coordinator.entry_id}_select_{key}"
        self._attr_current_option = None

    async def async_select_option(self, option: str) -> None:
        if option not in self._attr_options:
            return
        await self.coordinator.async_select_option(self._suffix, option)
        self._attr_current_option = option
        self.async_write_ha_state()
