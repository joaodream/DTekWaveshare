# WORKLOG

## 2026-02-19
- Bootstrapped new project `DTekWaveshare` for Waveshare ESP32-S3-POE-ETH-8DI-8RO-C control over Ethernet TCP/IP.
- Added reusable Python package (`client`, `config`, `router`) plus CLI commands (`status`, `set`, `toggle`, `all-on`, `all-off`).
- Added one-device and two-device sample mappings including logical output 9 on a second board.
- Added basic unit tests for routing/mapping behavior.

## 2026-02-20
- Adopted `config/output-map.json` as the source-of-truth file for `PC1..PC9` logical output mapping.
- Added `DtekWaveshareController` with simple app-facing methods (`set_output`, `set_pc`, `toggle_output`, `read_output`).
- Added wrapper usage example (`examples/control_from_app.py`) and controller unit tests (`tests/test_controller.py`).
- Updated `README.md` with baseline Ethernet verification steps and stable integration workflow.

## 2026-02-23
- Updated project documentation with TCP server mode protocol (`PING`, `GET`, `SET`, `TOGGLE`, `ALL`) and board validation steps.
- Added `examples/tcp_smoke_test.ps1` to quickly validate TCP relay control from Windows PowerShell.
- Updated `.gitignore` to ignore Python packaging artifacts (`*.egg-info/`).
