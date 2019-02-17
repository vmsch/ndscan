"""
Common fragments/… for unit tests.
"""

from artiq.experiment import *
from ndscan.fragment import *


class AddOneFragment(ExpFragment):
    def build_fragment(self):
        self.setattr_param("value", FloatParam, "Value to return", 0.0)
        self.setattr_result("result", FloatChannel)

        self.num_host_setup_calls = 0
        self.num_device_setup_calls = 0

    def host_setup(self):
        self.num_host_setup_calls += 1

    def device_setup(self):
        self.num_device_setup_calls += 1

    def run_once(self):
        self.result.push(self.value.get() + 1)


class ReboundAddOneFragment(ExpFragment):
    def build_fragment(self):
        self.setattr_fragment("add_one", AddOneFragment)
        self.setattr_param_rebind("value", self.add_one)

    def host_setup(self):
        self.add_one.host_setup()

    def device_setup(self):
        self.add_one.device_setup()

    def run_once(self):
        self.add_one.run_once()


class TrivialKernelFragment(ExpFragment):
    def build_fragment(self):
        pass

    @kernel
    def device_setup(self):
        pass

    @kernel
    def run_once(self):
        pass