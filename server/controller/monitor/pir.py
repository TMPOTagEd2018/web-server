import numpy as np

from . import Monitor


class PirMonitor(Monitor):
    def __init__(self, sensitivity=1):
        super().__init__()

        self.sensitivity = sensitivity

        self.query = self.data \
            .map(int) \
            .buffer_with_count(10, 5) \
            .subscribe(self.handler)

        self.level = 0

    def input(self, value):
        self.data.on_next(value)

    def handler(self, buffer: [int]):
        # observe the last 10 values and check if contact is over

        m = np.sum(buffer)

        self.level = 1 if m > 5 else 0

        self.threats.on_next(self.level * self.sensitivity)
