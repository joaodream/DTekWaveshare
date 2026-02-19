from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


class RelayProtocolError(RuntimeError):
    pass


@dataclass
class WaveshareHttpRelayClient:
    host: str
    port: int = 80
    timeout_seconds: float = 2.0
    channel_count: int = 8

    def _base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def _get(self, path: str) -> str:
        url = f"{self._base_url()}{path}"
        try:
            with urlopen(url, timeout=self.timeout_seconds) as response:
                return response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            raise RelayProtocolError(f"HTTP error {exc.code} for {url}") from exc
        except URLError as exc:
            raise RelayProtocolError(f"Connection error for {url}: {exc.reason}") from exc

    def toggle_channel(self, channel: int) -> None:
        self._validate_channel(channel)
        self._get(f"/Switch{channel}")

    def all_on(self) -> None:
        self._get("/AllOn")

    def all_off(self) -> None:
        self._get("/AllOff")

    def read_states(self) -> dict[int, bool]:
        payload = self._get("/getData")
        data = json.loads(payload)
        states: dict[int, bool] = {}
        for idx in range(1, self.channel_count + 1):
            key = f"ch{idx}"
            raw = data.get(key, 0)
            states[idx] = bool(int(raw))
        return states

    def set_channel(self, channel: int, target_on: bool) -> bool:
        self._validate_channel(channel)
        before = self.read_states()
        current = before[channel]
        if current == target_on:
            return False

        self.toggle_channel(channel)
        after = self.read_states()
        if after[channel] != target_on:
            raise RelayProtocolError(
                f"Channel {channel} state mismatch after toggle: expected {target_on}, got {after[channel]}"
            )
        return True

    def _validate_channel(self, channel: int) -> None:
        if channel < 1 or channel > self.channel_count:
            raise ValueError(f"channel must be in range 1..{self.channel_count}")
