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
3. Make sure your **ESPHome device is added** to Home Assistant (Settings →
   Devices & Services → ESPHome). Its buttons/selects must exist, e.g.
   `button.robiroboter_smart_cleaning`.
4. **Settings → Devices & Services → Add Integration → Tesvor X500**.
5. Enter:
   - **Name** — display name
   - **MQTT topic prefix** — default `tesvor/x500`
   - **ESPHome entity prefix** — the device-name slug used in the ESPHome
     entity IDs. For a device named *RobiRoboter* this is `robiroboter`.

## How control works (no firmware change)

The integration forwards each control to the firmware's existing ESPHome
entities:

| Integration action        | ESPHome entity called                          |
|---------------------------|------------------------------------------------|
| `vacuum.start`            | `button.<prefix>_smart_cleaning`               |
| `vacuum.stop` / `pause`   | `button.<prefix>_stop`                          |
| `vacuum.return_to_base`   | `button.<prefix>_go_charge`                     |
| `vacuum.clean_spot`       | `button.<prefix>_spot_cleaning`                 |
| Spot / Edge / Zigzag / Mop buttons | matching `button.<prefix>_*`           |
| Mop Intensity / Suction selects | `select.<prefix>_wischintensitat` / `_saugstarke_test_experimentell` |
| Map Reset button          | clears the integration's stored path (local)   |

If your ESPHome entity IDs differ, re-add the integration with the correct
**ESPHome entity prefix**.

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
├── const.py             # topics, ESPHome entity suffixes
├── coordinator.py       # MQTT subscribe + ESPHome service calls
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
