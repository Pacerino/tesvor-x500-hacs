"""Constants for the Tesvor X500 integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "tesvor_x500"

PLATFORMS = [
    Platform.VACUUM,
    Platform.CAMERA,
    Platform.BUTTON,
    Platform.SELECT,
    Platform.SENSOR,
]

# Config entry keys
CONF_NAME = "name"
CONF_TOPIC_PREFIX = "topic_prefix"
CONF_ESPHOME_PREFIX = "esphome_prefix"

DEFAULT_NAME = "Tesvor X500"
DEFAULT_TOPIC_PREFIX = "tesvor/x500"
# Slug of the ESPHome device friendly name. The firmware device is
# "RobiRoboter", so its entity IDs are e.g. button.robiroboter_smart_cleaning.
DEFAULT_ESPHOME_PREFIX = "robiroboter"

# MQTT subtopics (appended to the configured prefix). The firmware hard-
# publishes the robot state to "<prefix>/state" and map point batches to
# "<prefix>/map/points" as {"p": [[seq, x, y, kind], ...]} (real sequence
# numbers, not limited to a 16-point window).
TOPIC_STATE = "state"
TOPIC_MAP_POINTS = "map/points"

# Raw robot states published on <prefix>/state by the firmware.
STATE_CLEANING = "cleaning"
STATE_SPOT_CLEANING = "spot_cleaning"
STATE_EDGE_CLEANING = "edge_cleaning"
STATE_ZMODE_CLEANING = "zmode_cleaning"
STATE_RETURNING = "returning"
STATE_DOCKED = "docked"
STATE_CHARGING = "charging"
STATE_IDLE = "idle"
STATE_HIBERNATED = "hibernated"
STATE_SETTING = "setting"
STATE_ERROR = "error"

CLEANING_STATES = {
    STATE_CLEANING,
    STATE_SPOT_CLEANING,
    STATE_EDGE_CLEANING,
    STATE_ZMODE_CLEANING,
}

# Entity-ID suffixes of the ESPHome-native button/select entities exposed by
# the firmware. Full target entity_id is built as:
#   button.<esphome_prefix>_<suffix>   /   select.<esphome_prefix>_<suffix>
# These slugs come from the friendly names in x500.yaml.
BTN_SMART = "smart_cleaning"
BTN_SPOT = "spot_cleaning"
BTN_EDGE = "edge_cleaning"
BTN_STOP = "stop"
BTN_GO_CHARGE = "go_charge"
BTN_ZIGZAG = "zickzack_wischen"
BTN_MOP = "mop_cleaning_test_experimentell"
BTN_MAP_RESET = "map_reset"

SEL_MOP = "wischintensitat"
SEL_FAN = "saugstarke_test_experimentell"

# Options offered by the ESPHome select entities. Selecting an option on our
# proxy select forwards the same option to the ESPHome select.
MOP_OPTIONS = ["Low", "Default", "High", "Off"]
FAN_OPTIONS = ["Normal", "Strong", "Pause", "Quiet"]

# Map rendering
MAP_IMAGE_SIZE = 1000  # output PNG is square, size x size px
MAP_PADDING = 40  # px border around the path bounds
MAX_POINTS = 4000  # cap stored path points to bound memory
