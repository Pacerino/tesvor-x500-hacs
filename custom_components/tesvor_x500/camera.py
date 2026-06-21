"""Camera entity that renders the Tesvor X500 path map as a PNG."""

from __future__ import annotations

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TesvorCoordinator
from .entity import TesvorEntity
from .map_renderer import render_png


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TesvorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TesvorMapCamera(coordinator)])


class TesvorMapCamera(TesvorEntity, Camera):
    """Serves the live path map as a camera image."""

    _attr_name = "Map"
    _attr_icon = "mdi:map"

    def __init__(self, coordinator: TesvorCoordinator) -> None:
        TesvorEntity.__init__(self, coordinator)
        Camera.__init__(self)
        self._attr_unique_id = f"{coordinator.entry_id}_map"
        self._cached: bytes | None = None
        self._cached_count = -1

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        points = self.coordinator.points
        # Re-render only when the path changed.
        if self._cached is None or len(points) != self._cached_count:
            self._cached = await self.hass.async_add_executor_job(
                render_png, points
            )
            self._cached_count = len(points)
        return self._cached

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "point_count": len(self.coordinator.points),
            "robot_state": self.coordinator.state,
        }

    def _handle_update(self) -> None:
        # Invalidate cache so the next image request re-renders.
        self._cached_count = -1
        super()._handle_update()
