# Tesvor X500 — Home Assistant Integration

A HACS custom integration for the **Tesvor X500 / X500 Pro** robot vacuum,
built on top of the [tesvor-x500-pro-esphome-vacuum](https://github.com/hannes813/tesvor-x500-pro-esphome-vacuum)
firmware. It connects over **MQTT** and provides:

- A native **`vacuum`** entity (start / stop / return-to-dock / spot, state, battery)
- A **`camera`** entity rendering the live **path map** as a PNG (Dreame-style live map)
- **Buttons** for spot / edge / zigzag / mop / map reset
- **Selects** for mop intensity and suction power
- **Sensors** for raw state and map point count

> **Hardware note:** the X500 uses gyro/bump navigation (no LIDAR). The firmware
> only reports a *trail of path points*, so the map is a **coverage path**, not a
> room-segmented map with no-go zones like a LIDAR Dreame. That is a hardware
> limit, not a software one.

## Requirements

- The ESPHome firmware from the upstream project flashed and **added to Home
  Assistant** (it already exposes button/select entities via the ESPHome API)
- The MQTT integration configured in Home Assistant
- The firmware publishes (already does, no change needed):
  - `<prefix>/state` — raw state string
  - `<prefix>/map/points` — `{"p": [[seq, x, y, type], ...]}`

**No firmware modification is required.** Map and state come from MQTT; all
controls are forwarded to the firmware's existing ESPHome button/select
entities via the `button.press` / `select.select_option` services.

## Installation (HACS)

1. HACS → ⋮ → **Custom repositories** → add this repo as type **Integration**.
2. Install **Tesvor X500 Vacuum**, restart Home Assistant.
3. **Settings → Devices & Services → Add Integration → Tesvor X500**.
4. Enter a name and the MQTT **topic prefix** (default `tesvor/x500`).

## Firmware command channel

The upstream firmware exposes each command as a separate ESPHome button. This
integration instead publishes raw UART hex frames to `<prefix>/command`. Add a
small MQTT subscriber to your `x500.yaml` so the ESP writes them to UART:

```yaml
mqtt:
  # ...existing config...
  on_message:
    - topic: tesvor/x500/command
      then:
        - lambda: |-
            // payload like "AA 03 02 22 02 26"
            std::vector<uint8_t> frame;
            std::string s = x;
            size_t pos = 0;
            while (pos < s.size()) {
              if (s[pos] == ' ') { pos++; continue; }
              frame.push_back((uint8_t) strtol(s.substr(pos, 2).c_str(), nullptr, 16));
              pos += 2;
            }
            id(uart_bus).write_array(frame);
```

(If you prefer not to modify the firmware, change the vacuum/button/select
entities to publish to the per-command topics your firmware already exposes.)

## Lovelace map card

Works with the [Xiaomi Vacuum Map Card](https://github.com/PiotrMachowski/lovelace-xiaomi-vacuum-map-card)
or a simple picture card:

```yaml
type: picture-entity
entity: vacuum.tesvor_x500
camera_image: camera.tesvor_x500_map
camera_view: live
show_state: true
```

## Layout

```
custom_components/tesvor_x500/
├── __init__.py          # setup / coordinator wiring
├── manifest.json
├── const.py             # topics, UART command frames
├── coordinator.py       # MQTT subscribe, state + path points
├── config_flow.py
├── entity.py            # shared base entity
├── vacuum.py
├── camera.py            # serves the rendered map
├── map_renderer.py      # draws path points -> PNG (Pillow)
├── button.py
├── select.py
├── sensor.py
├── strings.json
└── translations/en.json
```
