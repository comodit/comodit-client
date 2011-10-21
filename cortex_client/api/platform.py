from resource import Resource
from host import SettingFactory

class Platform(Resource):
    def __init__(self, api = None, json_data = None):
        super(Platform, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(Platform, self).set_api(api)
        self._set_collection(api.get_platform_collection())

    def get_driver(self):
        return self._get_field("driver")

    def set_driver(self, owner):
        return self._set_field("driver", owner)

    def get_owner(self):
        return self._get_field("owner")

    def set_owner(self, owner):
        return self._set_field("owner", owner)

    def get_settings(self):
        return self._get_list_field("settings", SettingFactory())

    def set_settings(self, owner):
        return self._set_list_field("settings", owner)

    def add_setting(self, setting):
        self._add_to_list_field("settings", setting)

    def get_version(self):
        return self._get_field("version")

    def _show(self, indent = 0):
        super(Platform, self)._show(indent)
        print " "*indent, "Driver:", self.get_driver()
        print " "*indent, "Owner:", self.get_owner()
        print " "*indent, "Settings:"
        settings = self.get_settings()
        for s in settings:
            s.show(indent + 2)
