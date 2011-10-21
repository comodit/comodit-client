from resource import Resource
from exceptions import PythonApiException

__all__ = ["ChangeRequest",
           "InstallApplicationChangeRequest",
           "UninstallApplicationChangeRequest",
           "AddSettingChangeRequest",
           "UpdateSettingChangeRequest",
           "DeleteSettingChangeRequest"]

class ChangeRequest(Resource):
    def __init__(self, api = None, json_data = None):
        super(ChangeRequest, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(ChangeRequest, self).set_api(api)
        self._set_collection(api.get_change_request_collection())

    def get_owner(self):
        return self._get_field("owner")

    def set_owner(self, owner):
        return self._set_field("owner", owner)

    def get_target(self):
        return self._get_field("target")

    def set_target(self, target):
        return self._set_field("target", target)

    def get_summary(self):
        return self._get_field("summary")

    def get_created_time_stamp(self):
        return self._get_field("createdTimestamp")

    def set_created_time_stamp(self, time_stamp):
        return self._set_field("createdTimestamp", time_stamp)

    def get_applied_time_stamp(self):
        return self._get_field("appliedTimestamp")

    def set_applied_time_stamp(self, time_stamp):
        return self._set_field("appliedTimestamp", time_stamp)

    def get_action(self):
        return self._get_field("action")

    def _set_action(self, action):
        return self._set_field("action", action)

    def get_name(self):
        return self.get_uuid()

    def get_state(self):
        """
        Possible values: NEW, PENDING, APPLIED, ERROR
        """
        return self._get_field("state")

    def apply_request(self):
        result = self._client.update(self._resource_collection._resource_path + "/" +
                                          self.get_uuid() + "/_apply",
                                          decode=False)
        if(result.code != 200):
            raise PythonApiException(result.read())

    def dump(self, output_folder):
        raise NotImplementedError

    def load(self, input_folder):
        raise NotImplementedError

    def _show(self, indent = 0):
        print " "*indent, "Summary:", self.get_summary()
        print " "*indent, "Created:", self.get_created_time_stamp()
        state = self.get_state()
        print " "*indent, "State:", state
        if(state == "APPLIED"):
            print " "*indent, "State:", self.get_applied_time_stamp()

    def get_identifier(self):
        return self.get_summary()


class ApplicationChangeRequest(ChangeRequest):
    def __init__(self, api = None, json_data = None):
        super(ApplicationChangeRequest, self).__init__(api, json_data)

    def get_application(self):
        return self._get_field("application")

    def set_application(self, application):
        return self._set_field("application", application)

    def _show(self, indent = 0):
        super(ApplicationChangeRequest, self)._show(indent)
        print " "*indent, "Target host:", self.get_target()
        print " "*indent, "Application:", self.get_application()


class InstallApplicationChangeRequest(ApplicationChangeRequest):
    ACTION = "install_application"
    def __init__(self, api = None, json_data = None):
        super(InstallApplicationChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)


class UninstallApplicationChangeRequest(ApplicationChangeRequest):
    ACTION = "uninstall_application"
    def __init__(self, api = None, json_data = None):
        super(UninstallApplicationChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)


class SettingChangeRequest(ChangeRequest):
    def __init__(self, api = None, json_data = None):
        super(SettingChangeRequest, self).__init__(api, json_data)

    def get_value(self):
        return self._get_field("value")

    def set_value(self, value):
        return self._set_field("value", value)

    def _show(self, indent = 0):
        super(SettingChangeRequest, self)._show(indent)
        print " "*indent, "Value:", self.get_value()


class AddSettingChangeRequest(SettingChangeRequest):
    ACTION = "add_setting"
    def __init__(self, api = None, json_data = None):
        super(AddSettingChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)

    def get_key(self):
        return self._get_field("key")
    
    def set_key(self, key):
        self._set_field("key", key)

    def _show(self, indent = 0):
        super(AddSettingChangeRequest, self)._show(indent)
        print " "*indent, "Target host:", self.get_target()
        print " "*indent, "Key:", self.get_key()


class UpdateSettingChangeRequest(SettingChangeRequest):
    ACTION = "update_setting"
    def __init__(self, api = None, json_data = None):
        super(UpdateSettingChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)

    def _show(self, indent = 0):
        super(UpdateSettingChangeRequest, self)._show(indent)
        print " "*indent, "Target setting:", self.get_target()


class DeleteSettingChangeRequest(SettingChangeRequest):
    ACTION = "delete_setting"
    def __init__(self, api = None, json_data = None):
        super(DeleteSettingChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)

    def _show(self, indent = 0):
        super(DeleteSettingChangeRequest, self)._show(indent)
        print " "*indent, "Target setting:", self.get_target()
