# coding: utf-8
"""
Platform module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from resource import Resource
from host import SettingFactory

class Platform(Resource):
    """
    Platform's description. A platform is described by a driver and a list of
    settings.
    """
    def __init__(self, api = None, json_data = None):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict, list or String
        """
        super(Platform, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(Platform, self).set_api(api)
        self._set_collection(api.get_platform_collection())

    def get_driver(self):
        """
        Provides platform's driver class name.
        @return: Driver's class name
        @rtype: String
        """
        return self._get_field("driver")

    def set_driver(self, driver):
        """
        Sets platform's driver class name.
        @param driver: Driver's class name
        @type driver: String
        """
        return self._set_field("driver", driver)

    def get_owner(self):
        """
        Provides platform's owner UUID.
        @return: A user's UUID
        @rtype: String
        """
        return self._get_field("owner")

    def set_owner(self, owner):
        """
        Sets platform's owner.
        @param owner: A user's UUID
        @type owner: String
        """
        return self._set_field("owner", owner)

    def get_settings(self):
        """
        Provides platform's settings.
        @return: A list of settings
        @rtype: list of L{Setting}
        """
        return self._get_list_field("settings", SettingFactory())

    def set_settings(self, settings):
        """
        Sets platform's settings.
        @param settings: A list of settings
        @type settings: list of L{Setting}
        """
        return self._set_list_field("settings", settings)

    def add_setting(self, setting):
        """
        Adds a setting to platform.
        @param setting: A setting
        @type setting: L{Setting}
        """
        self._add_to_list_field("settings", setting)

    def get_version(self):
        """
        Provides platform's version number.
        @return: A version number
        @rtype: Integer
        """
        return int(self._get_field("version"))

    def _show(self, indent = 0):
        super(Platform, self)._show(indent)
        print " "*indent, "Driver:", self.get_driver()
        print " "*indent, "Owner:", self.get_owner()
        print " "*indent, "Settings:"
        settings = self.get_settings()
        for s in settings:
            s.show(indent + 2)
