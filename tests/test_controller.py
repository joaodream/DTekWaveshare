import unittest

from dtekwaveshare.controller import DtekWaveshareController, DeviceEndpoint


class FakeClient:
    def __init__(self, channel_count: int = 8):
        self.states = {idx: False for idx in range(1, channel_count + 1)}

    def set_channel(self, channel: int, target_on: bool) -> bool:
        before = self.states[channel]
        self.states[channel] = target_on
        return before != target_on

    def toggle_channel(self, channel: int) -> None:
        self.states[channel] = not self.states[channel]

    def read_states(self):
        return dict(self.states)


def fake_client_factory(device: DeviceEndpoint) -> FakeClient:
    return FakeClient(channel_count=device.channels)


class ControllerTests(unittest.TestCase):
    def test_set_output_and_set_pc(self):
        controller = DtekWaveshareController.from_output_map(
            "config/output-map.json",
            client_factory=fake_client_factory,
        )

        changed = controller.set_output(1, True)
        self.assertTrue(changed)
        self.assertTrue(controller.read_output(1))

        changed_again = controller.set_pc("PC1", True)
        self.assertFalse(changed_again)

    def test_toggle_output(self):
        controller = DtekWaveshareController.from_output_map(
            "config/output-map.json",
            client_factory=fake_client_factory,
        )

        self.assertFalse(controller.read_output(2))
        controller.toggle_output(2)
        self.assertTrue(controller.read_output(2))

    def test_unconfigured_device_ip_raises(self):
        controller = DtekWaveshareController.from_output_map("config/output-map.json")

        with self.assertRaises(RuntimeError):
            controller.set_output(9, True)


if __name__ == "__main__":
    unittest.main()
