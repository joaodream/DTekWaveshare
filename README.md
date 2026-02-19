# DTekWaveshare

Reusable base project for controlling Waveshare `ESP32-S3-POE-ETH-8DI-8RO-C` relay outputs over Ethernet TCP/IP.

This repository is intended to be the foundation layer for larger projects that need relay orchestration.

## What Is Included

- Python package with a relay client (`WaveshareHttpRelayClient`)
- Output router that maps logical outputs to physical device/channel
- CLI for experiments and operations
- Sample configs for:
- one board (8 outputs)
- two boards (16 outputs, including your future output 9)
- Unit tests for routing logic

## Protocol Assumption

This project uses the HTTP control endpoints from Waveshare demo firmware (`/Switch1..8`, `/AllOn`, `/AllOff`, `/getData`), which run over TCP/IP.

Important: make sure the firmware running on your board exposes these endpoints on the Ethernet interface.

## Quick Start

1. Create a virtual environment and install editable package:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

2. Copy and edit config:

```powershell
Copy-Item .\config\devices.sample.json .\config\devices.local.json
```

Set your board IP in `config/devices.local.json`.

3. Check status:

```powershell
dtek-waveshare --config .\config\devices.local.json status
```

4. Toggle or set outputs:

```powershell
dtek-waveshare --config .\config\devices.local.json toggle --output 1
dtek-waveshare --config .\config\devices.local.json set --output 1 --state on
```

## Output Strategy (Your 9 PCs)

- Current board: outputs 1-8
- Future second board: output 9 can map to board2 channel 1

Use `config/devices.two-devices.sample.json` when the second board is added.

## Tests

```powershell
python -m unittest discover -s tests -p "test_*.py"
```
