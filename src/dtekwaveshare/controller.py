from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .client import WaveshareHttpRelayClient


@dataclass(frozen=True)
class DeviceEndpoint:
    name: str
    ip: str
    channels: int = 8
    port: int = 80
    timeout_seconds: float = 2.0


@dataclass(frozen=True)
class OutputBinding:
    pc: str
    output: int
    device: str
    channel: int


ClientFactory = Callable[[DeviceEndpoint], WaveshareHttpRelayClient]


class DtekWaveshareController:
    def __init__(
        self,
        devices: dict[str, DeviceEndpoint],
        output_bindings: dict[int, OutputBinding],
        pc_bindings: dict[str, OutputBinding],
        clients: dict[str, WaveshareHttpRelayClient],
    ) -> None:
        self._devices = devices
        self._output_bindings = output_bindings
        self._pc_bindings = pc_bindings
        self._clients = clients

    @classmethod
    def from_output_map(
        cls,
        path: str | Path,
        client_factory: ClientFactory | None = None,
    ) -> "DtekWaveshareController":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))

        devices = cls._parse_devices(raw.get("devices", []))
        output_bindings, pc_bindings = cls._parse_bindings(raw.get("pc_to_output", []), devices)

        if client_factory is None:
            def _default_factory(device: DeviceEndpoint) -> WaveshareHttpRelayClient:
                return WaveshareHttpRelayClient(
                    host=device.ip,
                    port=device.port,
                    timeout_seconds=device.timeout_seconds,
                    channel_count=device.channels,
                )
            client_factory = _default_factory

        clients: dict[str, WaveshareHttpRelayClient] = {}
        for name, device in devices.items():
            if device.ip and device.ip.upper() != "TBD":
                clients[name] = client_factory(device)

        return cls(
            devices=devices,
            output_bindings=output_bindings,
            pc_bindings=pc_bindings,
            clients=clients,
        )

    def mapped_outputs(self) -> list[int]:
        return sorted(self._output_bindings.keys())

    def set_output(self, output: int, target_on: bool) -> bool:
        binding = self._binding_for_output(output)
        return self._client_for(binding.device).set_channel(binding.channel, target_on)

    def toggle_output(self, output: int) -> None:
        binding = self._binding_for_output(output)
        self._client_for(binding.device).toggle_channel(binding.channel)

    def set_pc(self, pc_name: str, target_on: bool) -> bool:
        binding = self._binding_for_pc(pc_name)
        return self._client_for(binding.device).set_channel(binding.channel, target_on)

    def read_output(self, output: int) -> bool:
        binding = self._binding_for_output(output)
        states = self._client_for(binding.device).read_states()
        return states[binding.channel]

    def describe_output(self, output: int) -> OutputBinding:
        return self._binding_for_output(output)

    def _binding_for_output(self, output: int) -> OutputBinding:
        if output not in self._output_bindings:
            raise KeyError(f"Output {output} is not mapped.")
        return self._output_bindings[output]

    def _binding_for_pc(self, pc_name: str) -> OutputBinding:
        if pc_name not in self._pc_bindings:
            raise KeyError(f"PC '{pc_name}' is not mapped.")
        return self._pc_bindings[pc_name]

    def _client_for(self, device_name: str) -> WaveshareHttpRelayClient:
        if device_name not in self._clients:
            ip = self._devices[device_name].ip
            raise RuntimeError(
                f"Device '{device_name}' has no reachable client configured (ip={ip!r}). "
                "Set a real IP in config/output-map.json."
            )
        return self._clients[device_name]

    @staticmethod
    def _parse_devices(entries: list[dict]) -> dict[str, DeviceEndpoint]:
        if not entries:
            raise ValueError("output-map must contain at least one device.")

        devices: dict[str, DeviceEndpoint] = {}
        for entry in entries:
            name = str(entry.get("name", "")).strip()
            if not name:
                raise ValueError("Each device requires a non-empty 'name'.")
            if name in devices:
                raise ValueError(f"Duplicate device name: {name}")

            devices[name] = DeviceEndpoint(
                name=name,
                ip=str(entry.get("ip", "")).strip(),
                channels=int(entry.get("channels", 8)),
                port=int(entry.get("port", 80)),
                timeout_seconds=float(entry.get("timeout_seconds", 2.0)),
            )
        return devices

    @staticmethod
    def _parse_bindings(
        entries: list[dict],
        devices: dict[str, DeviceEndpoint],
    ) -> tuple[dict[int, OutputBinding], dict[str, OutputBinding]]:
        if not entries:
            raise ValueError("output-map must contain 'pc_to_output' bindings.")

        output_bindings: dict[int, OutputBinding] = {}
        pc_bindings: dict[str, OutputBinding] = {}

        for entry in entries:
            binding = OutputBinding(
                pc=str(entry.get("pc", "")).strip(),
                output=int(entry["output"]),
                device=str(entry["device"]).strip(),
                channel=int(entry["channel"]),
            )

            if not binding.pc:
                raise ValueError("Each binding requires a non-empty 'pc' value.")
            if binding.device not in devices:
                raise ValueError(f"Unknown device in binding: {binding.device}")
            if binding.output in output_bindings:
                raise ValueError(f"Duplicate output mapping: {binding.output}")
            if binding.pc in pc_bindings:
                raise ValueError(f"Duplicate PC mapping: {binding.pc}")

            channel_max = devices[binding.device].channels
            if binding.channel < 1 or binding.channel > channel_max:
                raise ValueError(
                    f"Invalid channel {binding.channel} for {binding.device} "
                    f"(allowed 1..{channel_max})"
                )

            output_bindings[binding.output] = binding
            pc_bindings[binding.pc] = binding

        return output_bindings, pc_bindings

