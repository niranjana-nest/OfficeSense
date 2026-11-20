
import pytest

from officesense.inference.plugins.person_detector import PersonDetector
from officesense.inference.registry import ModelRegistry


def test_registry_loads_person_detector():
    registry = ModelRegistry()

    plugin = registry.load("person_detector")

    assert isinstance(plugin, PersonDetector)


def test_registry_rejects_unknown_plugin():
    registry = ModelRegistry()

    with pytest.raises(
        ValueError,
        match="Unknown inference plug-in: unknown_plugin"
    ):
        registry.load("unknown_plugin")
