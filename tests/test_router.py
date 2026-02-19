import unittest

from dtekwaveshare.config import Binding
from dtekwaveshare.router import OutputRouter


class FakeClient:
    def __init__(self, channel_count: int = 8):
        self.states_map = {idx: False for idx in range(1, channel_count + 1)}

    def toggle_channel(self, channel: int) -> None:
        self.states_map[channel] = not self.states_map[channel]

    def set_channel(self, channel: int, target_on: bool) -> bool:
        before = self.states_map[channel]
        self.states_map[channel] = target_on
        return before != target_on

    def read_states(self):
        return dict(self.states_map)

    def all_on(self):
        for key in self.states_map:
            self.states_map[key] = True

    def all_off(self):
        for key in self.states_map:
            self.states_map[key] = False


class OutputRouterTests(unittest.TestCase):
    def test_set_output_changes_state(self):
        router = OutputRouter(
            clients={"relay01": FakeClient()},
            bindings={1: Binding(output=1, device="relay01", channel=1)},
        )

        changed = router.set_output(1, True)
        self.assertTrue(changed)
        self.assertTrue(router.snapshot()[1])

        changed_again = router.set_output(1, True)
        self.assertFalse(changed_again)

    def test_two_devices_with_output_nine(self):
        router = OutputRouter(
            clients={"relay01": FakeClient(), "relay02": FakeClient()},
            bindings={
                1: Binding(output=1, device="relay01", channel=1),
                9: Binding(output=9, device="relay02", channel=1),
            },
        )

        router.set_output(9, True)
        snapshot = router.snapshot()
        self.assertTrue(snapshot[9])
        self.assertFalse(snapshot[1])


if __name__ == "__main__":
    unittest.main()
