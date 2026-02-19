from __future__ import annotations

import argparse
import sys

from .config import load_project_config
from .router import OutputRouter


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DTekWaveshare relay orchestrator")
    parser.add_argument(
        "--config",
        default="config/devices.sample.json",
        help="Path to JSON config file",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Read all mapped outputs")

    toggle = sub.add_parser("toggle", help="Toggle logical output")
    toggle.add_argument("--output", type=int, required=True)

    set_cmd = sub.add_parser("set", help="Set logical output on/off")
    set_cmd.add_argument("--output", type=int, required=True)
    set_cmd.add_argument("--state", choices=["on", "off"], required=True)

    all_on = sub.add_parser("all-on", help="Turn all channels on for one device")
    all_on.add_argument("--device", required=True)

    all_off = sub.add_parser("all-off", help="Turn all channels off for one device")
    all_off.add_argument("--device", required=True)

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    config = load_project_config(args.config)
    router = OutputRouter.from_config(config)

    if args.command == "status":
        states = router.snapshot()
        for output in router.mapped_outputs():
            state = states.get(output)
            label = "UNKNOWN" if state is None else ("ON" if state else "OFF")
            address = router.resolve(output)
            print(f"OUT {output:02d} -> {address.device}:CH{address.channel} = {label}")
        return 0

    if args.command == "toggle":
        router.toggle_output(args.output)
        print(f"Output {args.output} toggled")
        return 0

    if args.command == "set":
        changed = router.set_output(args.output, args.state == "on")
        if changed:
            print(f"Output {args.output} set to {args.state}")
        else:
            print(f"Output {args.output} already {args.state}")
        return 0

    if args.command == "all-on":
        router.all_on(args.device)
        print(f"Device {args.device} all outputs ON")
        return 0

    if args.command == "all-off":
        router.all_off(args.device)
        print(f"Device {args.device} all outputs OFF")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
