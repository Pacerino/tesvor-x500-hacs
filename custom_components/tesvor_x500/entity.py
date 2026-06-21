"""Base entity for the Tesvor X500 integration."""

from __future__ import annotations

from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN
from .coordinator import TesvorCoordinator, signal_update


class TesvorEntity(Entity):
    """Base entity wired to the coordinator dispatcher."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, coordinator: TesvorCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name="Tesvor X500",
            manufacturer="Tesvor",
            model="X500 / X500 Pro",
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_update(self.coordinator.entry_id),
                self._handle_update,
            )
        )

    def _handle_update(self) -> None:
        self.async_write_ha_state()
