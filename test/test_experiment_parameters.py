import unittest
from ndscan.experiment.parameters import FloatParam, IntParam


class FloatParamCase(unittest.TestCase):
    def test_describe(self):
        param = FloatParam("foo", "bar", 1.0, min=0.0, max=2.0, unit="baz", scale=1.0)
        self.assertEqual(
            param.describe(), {
                "fqn": "foo",
                "description": "bar",
                "default": "1.0",
                "spec": {
                    "min": 0.0,
                    "max": 2.0,
                    "unit": "baz",
                    "scale": 1.0,
                    "step": 0.1,
                    "is_scannable": True,
                },
                "type": "float"
            })


class IntParamCase(unittest.TestCase):
    def test_describe(self):
        param = IntParam("foo", "bar", 0, min=-1, max=1, unit="baz", scale=1)
        self.assertEqual(
            param.describe(), {
                "fqn": "foo",
                "description": "bar",
                "default": "0",
                "spec": {
                    "min": -1,
                    "max": 1,
                    "unit": "baz",
                    "scale": 1,
                    "is_scannable": True,
                },
                "type": "int"
            })
