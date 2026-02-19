from __future__ import annotations

from dataclasses import dataclass

from .client import WaveshareHttpRelayClient
from .config import Binding, ProjectConfig


@dataclass
class OutputAddress:
    device: str
    channel: int


class OutputRouter:
    def __init__(self, clients: dict[str, WaveshareHttpRelayClient], bindings: dict[int, Binding]):
        self._clients = clients
        self._bindings = bindings

    @classmethod
    def from_config(cls, config: ProjectConfig) -> "OutputRouter":
        clients = {
            name: WaveshareHttpRelayClient(
                host=device.host,
                port=device.port,
                timeout_seconds=device.timeout_seconds,
                channel_count=device.channel_count,
            )
            for name, device in config.devices.items()
        }
        return cls(clients=clients, bindings=config.bindings)

    def mapped_outputs(self) -> list[int]:
        return sorted(self._bindings.keys())

    def resolve(self, output: int) -> OutputAddress:
        if output not in self._bindings:
            raise KeyError(f"Output {output} is not mapped.")
        binding = self._bindings[output]
        return OutputAddress(device=binding.device, channel=binding.channel)

    def toggle_output(self, output: int) -> None:
        address = self.resolve(output)
        self._clients[address.device].toggle_channel(address.channel)

    def set_output(self, output: int, target_on: bool) -> bool:
        address = self.resolve(output)
        return self._clients[address.device].set_channel(address.channel, target_on)

    def all_on(self, device_name: str) -> None:
        self._clients[device_name].all_on()

    def all_off(self, device_name: str) -> None:
        self._clients[device_name].all_off()

    def snapshot(self) -> dict[int, bool | None]:
        state_cache: dict[str, dict[int, bool]] = {}
        result: dict[int, bool | None] = {}
        for output, binding in sorted(self._bindings.items()):
            try:
                if binding.device not in state_cache:
                    state_cache[binding.device] = self._clients[binding.device].read_states()
                result[output] = state_cache[binding.device].get(binding.channel)
            except Exception:
                result[output] = None
        return result
