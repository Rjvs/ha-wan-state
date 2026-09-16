# WAN Failover Monitor

A Home Assistant custom integration for routers running an active-probe
WAN failover setup (primary connection + cellular backup) that publish
their status over MQTT. Point it at your publisher's topic prefix and it
creates the entities — no YAML, no MQTT discovery payloads to hand-craft.

Push-based (`local_push`): entities update the instant a message arrives
on their topic, nothing is polled.

## Installation

**HACS** (recommended): HACS → Integrations → ⋮ → Custom repositories →
add this repo's URL as an "Integration" → install "WAN Failover Monitor"
→ restart Home Assistant.

**Manual**: copy `custom_components/wan_failover_monitor/` into your HA
config's `custom_components/` directory, then restart.

## Setup

Settings → Devices & Services → Add Integration → "WAN Failover Monitor".
You'll be asked for:

- **Device name** — how the device shows up in HA.
- **MQTT topic prefix** — must match what your publisher script uses
  (see the contract below).
- **Enable cellular status sensors** — turn off if your publisher only
  sends the core failover topics.

Requires HA's own **MQTT** integration already configured against the
broker your publisher sends to.

## The topic contract

A publisher is any script/device that sends MQTT messages matching this
shape. Given a topic prefix (e.g. `router`), retained or not — either
works, but retained means entities show last-known state immediately
after an HA restart, before the next publish:

| Topic | Payload | Creates |
|---|---|---|
| `<prefix>/wan_status` | free-form string, e.g. `primary` / `cellular` | `sensor` — Active WAN |
| `<prefix>/interfaces/nbn` | `ON` or `OFF` | `binary_sensor` — Primary Uplink |
| `<prefix>/interfaces/cellular` | `ON` or `OFF` | `binary_sensor` — Cellular Uplink |
| `<prefix>/next_check` | ISO 8601 timestamp (e.g. `2026-01-01T00:00:15Z`) | `sensor`, `device_class: timestamp` — Next Check |

With cellular status sensors enabled, also:

| Topic | Payload | Creates |
|---|---|---|
| `<prefix>/cellular/network_type` | free-form string, e.g. `LTE` | `sensor` — Cellular Network Type |
| `<prefix>/cellular/signal_dbm` | number (or empty if unknown) | `sensor`, `device_class: signal_strength`, unit dBm — Cellular Signal |
| `<prefix>/cellular/signalbar` | number (or empty) | `sensor` — Cellular Signal Bars |
| `<prefix>/cellular/ppp_status` | free-form string | `sensor` — Cellular PPP Status |
| `<prefix>/cellular/wan_ip` | IP address string | `sensor` — Cellular WAN IP |
| `<prefix>/cellular/imei` | string | `sensor`, `entity_category: diagnostic` — Cellular IMEI |
| `<prefix>/cellular/data_plantype` | free-form string | `sensor`, `entity_category: diagnostic` — Cellular Data Plan Type |
| `<prefix>/cellular/data_allotted` | number, bytes | `sensor`, `device_class: data_size`, unit bytes — Cellular Data Allotted |
| `<prefix>/cellular/data_used` | number, bytes | `sensor`, `device_class: data_size`, unit bytes — Cellular Data Used |
| `<prefix>/cellular/data_remaining` | number, bytes | `sensor`, `device_class: data_size`, unit bytes — Cellular Data Remaining |
| `<prefix>/cellular/data_remaining_days` | number | `sensor`, `device_class: duration`, unit `d` — Cellular Data Remaining Days |
| `<prefix>/cellular/data_remaining_percent` | number | `sensor`, unit `%` — Cellular Data Remaining Percent |
| `<prefix>/cellular/data_lowbalance` | `ON` or `OFF` | `binary_sensor`, `device_class: problem`, `entity_category: diagnostic` — Cellular Data Low Balance |

An empty payload on any topic is treated as "no data yet" (entity state
`unknown`), not an error — useful for a publisher that hasn't completed
its first cycle, or a status field that's genuinely inapplicable right
now (e.g. a signal reading before the radio has associated, or carrier
billing data that hasn't synced to the device yet — a publisher may
choose to simply not publish the `data_*` topics until it has a
confirmed sync, so entities hold their last-known value instead).

All entities from one config entry group under a single HA device, named
whatever you set as "Device name" during setup.

## Why not MQTT discovery?

Home Assistant's own [MQTT discovery][discovery] would let a publisher
create these entities without any custom component at all — retained
`homeassistant/.../config` payloads, picked up automatically. That's a
fine approach and this integration doesn't replace it for simpler cases.

This exists as an alternative for when you'd rather configure the
topic prefix and toggle sensors from HA's UI than bake discovery JSON
into the publisher script itself, and want the publisher and the HA
integration to evolve independently.

[discovery]: https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery

## License

MIT — see `LICENSE`.
