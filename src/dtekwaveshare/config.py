from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DeviceConfig:
    name: str
    host: str
    port: int = 80
    timeout_seconds: float = 2.0
    channel_count: int = 8


@dataclass(frozen=True)
class Binding:
    output: int
    device: str
    channel: int


@dataclass(frozen=True)
class ProjectConfig:
    devices: dict[str, DeviceConfig]
    bindings: dict[int, Binding]


def _build_default_bindings(devices: list[DeviceConfig]) -> dict[int, Binding]:
    bindings: dict[int, Binding] = {}
    output = 1
    for dev in devices:
        for channel in range(1, dev.channel_count + 1):
            bindings[output] = Binding(output=output, device=dev.name, channel=channel)
            output += 1
    return bindings


def load_project_config(path: str | Path) -> ProjectConfig:
    config_path = Path(path)
    raw = json.loads(config_path.read_text(encoding="utf-8"))

    devices_list = [
        DeviceConfig(
            name=d["name"],
            host=d["host"],
            port=int(d.get("port", 80)),
            timeout_seconds=float(d.get("timeout_seconds", 2.0)),
            channel_count=int(d.get("channel_count", 8)),
        )
        for d in raw.get("devices", [])
    ]

    if not devices_list:
        raise ValueError("Config must define at least one device in 'devices'.")

    devices = {d.name: d for d in devices_list}

    output_entries = raw.get("outputs")
    if output_entries:
        bindings = {
            int(item["output"]): Binding(
                output=int(item["output"]),
                device=item["device"],
                channel=int(item["channel"]),
            )
            for item in output_entries
        }
    else:
        bindings = _build_default_bindings(devices_list)

    for binding in bindings.values():
        if binding.device not in devices:
            raise ValueError(f"Unknown device in output map: {binding.device}")
        max_channel = devices[binding.device].channel_count
        if binding.channel < 1 or binding.channel > max_channel:
            raise ValueError(
                f"Invalid channel {binding.channel} for device {binding.device} (1..{max_channel})"
            )

    return ProjectConfig(devices=devices, bindings=bindings)
