import os

from blasy.blasy import PluginManager


class TestLoadingPlugin:

    # TODO: recursive, category

    def test_can_find_plugins_from_dir(self):

        pm = PluginManager(plugin_info_ext="testplug")

        test_dir = os.path.dirname(__file__)
        test_data_dir = os.path.join(test_dir, "data")

        pm.setPluginPlaces([test_data_dir])

        pm.collectPlugins()

        assert len(pm.available_plugins) == 2

