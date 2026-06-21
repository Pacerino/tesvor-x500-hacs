"""MQTT data coordinator for the Tesvor X500 integration."""

from __future__ import annotations

import json
import logging

from homeassistant.components import mqtt
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    CLEANING_STATES,
    DOMAIN,
    MAX_POINTS,
    TOPIC_MAP_POINTS,
    TOPIC_STATE,
)

_LOGGER = logging.getLogger(__name__)


def signal_update(entry_id: str) -> str:
    """Dispatcher signal fired when coordinator data changes."""
    return f"{DOMAIN}_{entry_id}_update"


class TesvorCoordinator:
    """Holds the latest robot state and accumulated map path points.

    Subscribes to the firmware MQTT topics:
      <prefix>/state         -> raw state string
      <prefix>/map/points    -> {"p": [[seq, x, y, type], ...]}
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        topic_prefix: str,
        esphome_prefix: str,
    ) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.topic_prefix = topic_prefix.rstrip("/")
        # Slug prefix of the ESPHome device, e.g. "robiroboter".
        self.esphome_prefix = esphome_prefix.strip().strip(".")

        self.state: str | None = None
        self.battery: int | None = None
        # points_by_seq maps sequence number -> (x, y, type)
        self._points_by_seq: dict[int, tuple[int, int, int]] = {}

        self._unsubs: list = []

    @property
    def state_topic(self) -> str:
        return f"{self.topic_prefix}/{TOPIC_STATE}"

    @property
    def points_topic(self) -> str:
        return f"{self.topic_prefix}/{TOPIC_MAP_POINTS}"

    def button_entity(self, suffix: str) -> str:
        """Full entity_id of an ESPHome button."""
        return f"button.{self.esphome_prefix}_{suffix}"

    def select_entity(self, suffix: str) -> str:
        """Full entity_id of an ESPHome select."""
        return f"select.{self.esphome_prefix}_{suffix}"

    @property
    def is_cleaning(self) -> bool:
        return self.state in CLEANING_STATES

    @property
    def points(self) -> list[tuple[int, int, int]]:
        """Ordered list of (x, y, type) points by sequence."""
        return [self._points_by_seq[k] for k in sorted(self._points_by_seq)]

    async def async_setup(self) -> None:
        """Subscribe to MQTT topics."""
        self._unsubs.append(
            await mqtt.async_subscribe(
                self.hass, self.state_topic, self._handle_state, qos=0
            )
        )
        self._unsubs.append(
            await mqtt.async_subscribe(
                self.hass, self.points_topic, self._handle_points, qos=0
            )
        )
        _LOGGER.debug(
            "Subscribed to %s and %s", self.state_topic, self.points_topic
        )

    async def async_unload(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()

    async def async_press_button(self, suffix: str) -> None:
        """Press an ESPHome-native button entity exposed by the firmware."""
        entity_id = self.button_entity(suffix)
        _LOGGER.debug("Pressing ESPHome button %s", entity_id)
        await self.hass.services.async_call(
            "button",
            "press",
            {ATTR_ENTITY_ID: entity_id},
            blocking=False,
        )

    async def async_select_option(self, suffix: str, option: str) -> None:
        """Set an option on an ESPHome-native select entity."""
        entity_id = self.select_entity(suffix)
        _LOGGER.debug("Setting ESPHome select %s -> %s", entity_id, option)
        await self.hass.services.async_call(
            "select",
            "select_option",
            {ATTR_ENTITY_ID: entity_id, "option": option},
            blocking=False,
        )

    def reset_map(self) -> None:
        self._points_by_seq.clear()
        self._notify()

    @callback
    def _handle_state(self, msg) -> None:
        new_state = msg.payload.strip()
        if not new_state:
            return
        # Starting a fresh clean from a docked/idle state clears the old path.
        if new_state in CLEANING_STATES and not self.is_cleaning:
            self._points_by_seq.clear()
        self.state = new_state
        self._notify()

    @callback
    def _handle_points(self, msg) -> None:
        try:
            data = json.loads(msg.payload)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid map points payload: %s", msg.payload)
            return

        added = 0
        for p in data.get("p", []):
            if not isinstance(p, list) or len(p) != 4:
                continue
            try:
                seq, x, y, kind = int(p[0]), int(p[1]), int(p[2]), int(p[3])
            except (ValueError, TypeError):
                continue
            if seq not in self._points_by_seq:
                self._points_by_seq[seq] = (x, y, kind)
                added += 1

        # Bound memory: drop oldest sequences if we exceed the cap.
        if len(self._points_by_seq) > MAX_POINTS:
            for old in sorted(self._points_by_seq)[: len(self._points_by_seq) - MAX_POINTS]:
                del self._points_by_seq[old]

        if added:
            self._notify()

    @callback
    def _notify(self) -> None:
        async_dispatcher_send(self.hass, signal_update(self.entry_id))
