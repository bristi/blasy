import os
import sys
from pathlib import Path
import pyclbr
import configparser
import importlib
import inspect


class IPlugin:
    """ Custom IPlugin

    Make sure plugins load from this instead

    """


class BlasyError(Exception):
    pass


class PluginManager:
    """ Custom Plugin manager

    Use methods here transparently with PluginManager from Yapsy

    The non-standard naming convention for methods is annoying, yes.

    """

    def __init__(self, plugin_info_ext="plugin"):

        self.plugin_ext = plugin_info_ext
        self.plugin_locations = []
        self.categories_filter = {}
        self.available_plugins = []

    def setPluginPlaces(self, plugin_locations):
        """

        :return: 
        """

        # TODO: Check existense of locations?

        self.plugin_locations = plugin_locations

    def setCategoriesFilter(self, categories_filter):
        """

        :return: 
        """

        # TODO: validate?

        self.categories_filter = categories_filter

    def collectPlugins(self):
        """ Collects ALL plugins (of any category)

        Specifically any class specified in plugin dir(s) inheriting
        from class IPlugin

        :return: 
        """

        # Basic checks
        assert self.plugin_locations

        # Clear available plugins
        self.available_plugins = []
        #self.all_plugins = []

        # Collect plugins from all given locations
        for loc in self.plugin_locations:
            p = Path(loc)

            # Get conf files in current location
            plug_configs = list(p.glob('*.' + self.plugin_ext))

            for plug_config in [str(x) for x in plug_configs]:
                parser = configparser.ConfigParser()
                try:
                    parser.read(plug_config)
                except configparser.Error as e:
                    raise BlasyError(
                        "Could not read plugin config file '{0}'!\n".format(
                            plug_config
                        ))

                # Collect all info for plugin in dictionary
                plug_info = {}
                for section in parser.sections():
                    for k in parser[section]:
                        plug_info[k.lower()] = parser[section][k]

                # Get classes in module pointed to by plugin conf

                # Gets spec for module without importing
                #spec = importlib.util.find_spec("plugins.datasource_nextseq")

                # Modifying python path before and after each import
                # since plugins can be anywhere?
                #info = importlib.import_module(plug_info['module'], loc)
                sys.path.insert(0, loc)
                try:
                    imported_module = importlib.import_module(
                        plug_info['module']
                    )
                except ImportError as e:
                    # We don't really care about modules that are not able
                    # to be imported for whatever reason
                    sys.path.pop(0)
                    continue
                sys.path.pop(0)

                # Get classes in module
                # Note that we inspect to accept only
                #   classes : inspect.isclass(member)
                #   members that belong in the module :
                #     member.__module__ == imported_module.__name__
                # The last part to make sure that we don't include classes
                # that are imported in the module we are inspecting
                for name, cls_obj in inspect.getmembers(
                        imported_module,
                        lambda member: inspect.isclass(member) and member.__module__ == imported_module.__name__):

                    # We don't want any (imported?) IPlugin class
                    if name == 'IPlugin':
                        continue

                    # We only want classes where parents inherit
                    # from IPlugin
                    mro = [x.__name__ for x in cls_obj.__mro__]
                    if not 'IPlugin' in mro:
                        continue

                    # Collect class info
                    plug_info['cls_name'] = name
                    plug_info['cls_obj'] = cls_obj
                    plug_info['cls_mro'] = mro

                    # Create Plugin object and register
                    self.available_plugins.append(Plugin(plug_info))

    def getPluginsOfCategory(self, category):
        """

        :param category: 
        :return: 
        """

        # The Yapsy implementation gives class objects but let's
        # allow strings as well
        try:
            cat_class_name = self.categories_filter[category].__name__
        except AttributeError:
            cat_class_name = str(self.categories_filter[category])

        plugins_in_category = []

        for p in self.available_plugins:
            if cat_class_name in p.cls_mro:
                plugins_in_category.append(p)

        return plugins_in_category


class Plugin:
    """ Class to hold plugins before they are initialized

    """

    def __init__(self, plugin_info):
        """ Put info from plugin here; name, version, author, ... (lowercase)

        :param plugin_info: dictionary with attributes for class instance
        """

        # Set all attributes in dictionary as class attributes
        for k, v in plugin_info.items():
            if ' ' in k:
                continue
            setattr(self, k, v)


    @property
    def plugin_object(self):
        """Return object plugin class

        :return: object
        """

        return self.cls_obj()

    def plugin_object_init(self, **params):
        """Return object initialized with named parameters from plugin class

        This is non-Yapsy functionality but I want to be able to
        initialize using parameters.

        :return: object
        """

        return self.cls_obj(**params)
