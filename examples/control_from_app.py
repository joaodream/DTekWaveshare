from dtekwaveshare import DtekWaveshareController


def main() -> None:
    controller = DtekWaveshareController.from_output_map("config/output-map.json")

    # Example: power cycle logical output 1.
    controller.set_output(1, True)
    controller.set_output(1, False)


if __name__ == "__main__":
    main()
