"""Button entities for the Tesvor X500."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    BTN_EDGE,
    BTN_MOP,
    BTN_SPOT,
    BTN_ZIGZAG,
    DOMAIN,
)
from .coordinator import TesvorCoordinator
from .entity import TesvorEntity


@dataclass(frozen=True, kw_only=True)
class TesvorButton:
    key: str
    name: str
    icon: str
    suffix: str | None = None  # ESPHome button suffix to forward to
    handler: str | None = None  # coordinator method name for local actions


BUTTONS: tuple[TesvorButton, ...] = (
    TesvorButton(key="spot", name="Spot Cleaning", icon="mdi:target", suffix=BTN_SPOT),
    TesvorButton(key="edge", name="Edge Cleaning", icon="mdi:border-all", suffix=BTN_EDGE),
    TesvorButton(key="zigzag", name="Zigzag / Mop", icon="mdi:sine-wave", suffix=BTN_ZIGZAG),
    TesvorButton(key="mop", name="Mop Cleaning", icon="mdi:water", suffix=BTN_MOP),
    TesvorButton(key="map_reset", name="Map Reset", icon="mdi:map-marker-off", handler="reset_map"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TesvorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TesvorButtonEntity(coordinator, desc) for desc in BUTTONS)


class TesvorButtonEntity(TesvorEntity, ButtonEntity):
    def __init__(
        self, coordinator: TesvorCoordinator, desc: TesvorButton
    ) -> None:
        super().__init__(coordinator)
        self._desc = desc
        self._attr_name = desc.name
        self._attr_icon = desc.icon
        self._attr_unique_id = f"{coordinator.entry_id}_btn_{desc.key}"

    async def async_press(self) -> None:
        if self._desc.handler:
            getattr(self.coordinator, self._desc.handler)()
        elif self._desc.suffix:
            await self.coordinator.async_press_button(self._desc.suffix)
