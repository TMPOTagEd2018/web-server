import numpy as np

from . import Monitor, sigmoid


class LuxMonitor(Monitor):
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
        m = np.sum(buffer * np.arange(0, 1, 1 / len(buffer))) / 11.475 / len(buffer)

        fac = sigmoid(m / 10 - 0.7)

        self.level = m * fac + self.level * (1 - fac)

        self.threats.on_next(self.level * self.sensitivity)