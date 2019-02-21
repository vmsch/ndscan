"""
Tests for subscan functionality.
"""

import json
from ndscan.experiment import run_fragment_once
from ndscan.fragment import *
from ndscan.scan_generator import LinearGenerator, ScanOptions
from ndscan.subscan import setattr_subscan

from fixtures import AddOneFragment, ReboundAddOneFragment
from mock_environment import ExpFragmentCase


class Scan1DFragment(ExpFragment):
    def build_fragment(self, klass):
        self.setattr_fragment("child", klass)
        scan = setattr_subscan(self, "scan", self.child, [(self.child, "value")])
        assert self.scan == scan

    def run_once(self):
        return self.scan.run([(self.child.value, LinearGenerator(0, 3, 4, False))],
                             ScanOptions(seed=1234))


class SubscanCase(ExpFragmentCase):
    def test_1d_subscan_return(self):
        parent = self.create(Scan1DFragment, AddOneFragment)
        self._test_1d(parent, parent.child.result)

    def test_1d_rebound_subscan_return(self):
        parent = self.create(Scan1DFragment, ReboundAddOneFragment)
        self._test_1d(parent, parent.child.add_one.result)

    def _test_1d(self, parent, result_channel):
        coords, values = parent.run_once()

        expected_values = [float(n) for n in range(0, 4)]
        expected_results = [v + 1 for v in expected_values]
        self.assertEqual(coords, {parent.child.value: expected_values})
        self.assertEqual(values, {result_channel: expected_results})

    def test_1d_result_channels(self):
        parent = self.create(Scan1DFragment, AddOneFragment)
        results = run_fragment_once(parent)

        expected_values = [float(n) for n in range(0, 4)]
        expected_results = [v + 1 for v in expected_values]
        self.assertEqual(results[parent.scan_axis_0], expected_values)
        self.assertEqual(results[parent.scan_channel_result], expected_results)

        spec = json.loads(results[parent.scan_spec])
        self.assertEqual(spec["fragment_fqn"], "fixtures.AddOneFragment")
        self.assertEqual(spec["seed"], 1234)

        curve_annotation = {
            "kind": "computed_curve",
            "parameters": {
                "function_name": "lorentzian",
                "associated_channel": "channel_result"
            },
            "data": {
                "x0": {
                    "kind": "analysis_result",
                    "analysis_name": "fit_lorentzian",
                    "result_key": "x0"
                },
                "fwhm": {
                    "kind": "analysis_result",
                    "analysis_name": "fit_lorentzian",
                    "result_key": "fwhm"
                },
                "y0": {
                    "kind": "analysis_result",
                    "analysis_name": "fit_lorentzian",
                    "result_key": "y0"
                },
                "a": {
                    "kind": "analysis_result",
                    "analysis_name": "fit_lorentzian",
                    "result_key": "a"
                }
            }
        }
        location_annotation = {
            "kind": "location",
            "coordinates": {
                "axis_0": {
                    "kind": "analysis_result",
                    "analysis_name": "fit_lorentzian",
                    "result_key": "x0"
                }
            },
            "data": {
                "axis_0_error": {
                    "kind": "analysis_result",
                    "analysis_name": "fit_lorentzian",
                    "result_key": "x0_error"
                }
            }
        }
        self.assertEqual(spec["annotations"], [curve_annotation, location_annotation])
        self.assertEqual(
            spec["online_analyses"], {
                "fit_lorentzian": {
                    "data": {
                        "y": "channel_result",
                        "x": "axis_0"
                    },
                    "fit_type": "lorentzian",
                    "kind": "named_fit"
                }
            })
        self.assertEqual(
            spec["channels"], {
                "result": {
                    "description": "",
                    "scale": 1.0,
                    "path": "child/result",
                    "type": "float",
                    "unit": ""
                }
            })
        self.assertEqual(spec["axes"], [{
            "min": 0,
            "max": 3,
            "path": "child",
            "param": {
                "description": "Value to return",
                "default": "0.0",
                "fqn": "fixtures.AddOneFragment.value",
                "spec": {
                    "scale": 1.0,
                    "step": 0.1
                },
                "type": "float"
            },
            "increment": 1.0
        }])
