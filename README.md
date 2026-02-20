# DTekWaveshare

Reusable base project for controlling Waveshare `ESP32-S3-POE-ETH-8DI-8RO-C` relays over Ethernet TCP/IP.

## What Is Included

- Python relay client (`WaveshareHttpRelayClient`)
- Router-based API (`OutputRouter`) for output-to-device mappings
- Source-of-truth output map (`config/output-map.json`) for `PC1..PC9`
- Small app-facing wrapper API (`DtekWaveshareController`) with `set_output(...)`
- CLI tools and unit tests

## Protocol Assumption

This project uses firmware endpoints compatible with:

- `/Switch1` ... `/Switch8`
- `/AllOn`
- `/AllOff`
- `/getData`

These are HTTP over TCP/IP. In production, use the Ethernet interface.

## Baseline Record (Do This Once)

1. Flash board firmware and verify relay control.
2. Confirm Ethernet works from your PC:

```powershell
ping <board_eth_ip>
Invoke-WebRequest http://<board_eth_ip>/Switch1
Invoke-WebRequest http://<board_eth_ip>/getData
```

3. Put the final board IP in `config/output-map.json` (`devices[].ip`).
4. Keep `config/output-map.json` as the only mapping source for future projects.

## Mapping File

Edit `config/output-map.json`:

- `devices`: board name and IP.
- `pc_to_output`: logical mapping from `PCx` and `OUTx` to device channel.

Current layout:

- `PC1..PC8` -> `relay01 CH1..CH8`
- `PC9` -> reserved for `relay02 CH1`

## Quick Start

1. Install and run from this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

2. Use wrapper API in your application:

```python
from dtekwaveshare import DtekWaveshareController

ctl = DtekWaveshareController.from_output_map("config/output-map.json")
ctl.set_output(1, True)   # turn ON output 1
ctl.set_output(1, False)  # turn OFF output 1
```

3. Or use CLI:

```powershell
dtek-waveshare --config .\config\devices.sample.json status
dtek-waveshare --config .\config\devices.sample.json set --output 1 --state on
```

## Tests

```powershell
python -m unittest discover -s tests -p "test_*.py"
```
