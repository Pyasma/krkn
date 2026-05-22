#!/usr/bin/env python3
import logging
import sys
import types
import unittest
from unittest.mock import MagicMock


# Stub krkn_lib so the krkn package can be imported
def _inject(name, **attrs):
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules.setdefault(name, mod)
    return sys.modules[name]


_inject("krkn_lib")
_inject("krkn_lib.utils")
_inject("krkn_lib.utils.functions", get_yaml_item_value=MagicMock())
_inject("krkn_lib.k8s", KrknKubernetes=MagicMock())
_inject("krkn_lib.models.telemetry", ScenarioTelemetry=MagicMock())
_inject("krkn_lib.telemetry.ocp", KrknTelemetryOpenshift=MagicMock())
_inject("tzlocal")
_inject("tzlocal.unix", get_localzone=MagicMock(return_value="UTC"))

from krkn.utils.TeeLogHandler import TeeLogHandler  # noqa: E402


class TestTeeLogHandler(unittest.TestCase):
    def setUp(self):
        self.handler = TeeLogHandler()
        self.handler.setFormatter(logging.Formatter("%(message)s"))
        self.handler.clear()

    def test_emit_captures_log(self):
        record = logging.LogRecord(__name__, logging.INFO, "", 0, "hello", None, None)
        self.handler.emit(record)
        self.assertIn("hello", self.handler.get_output())

    def test_get_output_joins_multiple_logs(self):
        for msg in ["line1", "line2"]:
            record = logging.LogRecord(__name__, logging.INFO, "", 0, msg, None, None)
            self.handler.emit(record)
        self.assertEqual(self.handler.get_output(), "line1\nline2")

    def test_clear_empties_logs(self):
        record = logging.LogRecord(__name__, logging.INFO, "", 0, "data", None, None)
        self.handler.emit(record)
        self.handler.clear()
        self.assertEqual(self.handler.get_output(), "")


if __name__ == "__main__":
    unittest.main()
