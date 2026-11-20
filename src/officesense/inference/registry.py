from officesense.inference.plugins.person_detector import PersonDetector


class ModelRegistry:
    """Registry for available inference plug-ins."""

    def __init__(self):
        self.plugins = {
            "person_detector": PersonDetector
        }

    def load(self, plugin_name, **kwargs):
        if plugin_name not in self.plugins:
            raise ValueError(
                f"Unknown inference plug-in: {plugin_name}"
            )

        plugin_class = self.plugins[plugin_name]

        return plugin_class(**kwargs)
