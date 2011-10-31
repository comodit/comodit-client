# coding: utf-8
"""
Change requests module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from resource import Resource
from exceptions import PythonApiException

class ChangeRequest(Resource):
    """
    A change request. Change requests are used to install or uninstall
    applications from a host. Settings are also added, removed and updated
    through change requests.
    """
    def __init__(self, api = None, json_data = None):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        @param json_data: A quasi-JSON representation of change request's state.
        @type json_data: dict, list or String
        """
        super(ChangeRequest, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(ChangeRequest, self).set_api(api)
        self._set_collection(api.get_change_request_collection())

    def get_owner(self):
        """
        Provides the owner of this change request.
        @return: The owner's UUID
        @rtype: String
        """
        return self._get_field("owner")

    def set_owner(self, owner):
        """
        Sets the owner of this change request.
        @param owner: The owner's UUID
        @type owner: String
        """
        return self._set_field("owner", owner)

    def get_target(self):
        """
        Provides the target of this change request.
        @return: The target's UUID
        @rtype: String
        """
        return self._get_field("target")

    def set_target(self, target):
        """
        Sets the target of this change request.
        @param target: The target's UUID
        @type target: String
        """
        return self._set_field("target", target)

    def get_summary(self):
        """
        Provides the summary of this change request. The summary is generated
        by cortex server.
        @return: The summary
        @rtype: String
        """
        return self._get_field("summary")

    def get_created_time_stamp(self):
        """
        Provides change request's creation time.
        @return: The time stamp
        @rtype: String
        """
        return self._get_field("createdTimestamp")

    def get_applied_time_stamp(self):
        """
        Provides change request's application time.
        @return: The time stamp
        @rtype: String
        """
        return self._get_field("appliedTimestamp")

    def get_action(self):
        """
        Provides action type. Possible values are:
        @return: The action type.
        @rtype: String
        """
        return self._get_field("action")

    def _set_action(self, action):
        """
        Sets action type.
        @param action: The action type.
        @type action: String
        
        @see: L{get_action}
        """
        return self._set_field("action", action)

    def get_name(self):
        return self.get_uuid()

    def get_state(self):
        """
        Provides the state of this change request.
        @return: The state. Possible values: NEW, PENDING, APPLIED, ERROR.
        @rtype: String
        """
        return self._get_field("state")

    def apply_request(self):
        """
        Applies current change request.
        """
        result = self._client.update(self._resource_collection._resource_path + "/" +
                                          self.get_uuid() + "/_apply",
                                          decode = False)
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
    """
    Change request involving an application.
    """
    def __init__(self, api = None, json_data = None):
        super(ApplicationChangeRequest, self).__init__(api, json_data)

    def get_application(self):
        """
        Provides involved application.
        @return: Application's UUID
        @rtype: String
        """
        return self._get_field("application")

    def set_application(self, application):
        """
        Sets involved application.
        @param application: Application's UUID
        @type application: String
        """
        return self._set_field("application", application)

    def _show(self, indent = 0):
        super(ApplicationChangeRequest, self)._show(indent)
        print " "*indent, "Target host:", self.get_target()
        print " "*indent, "Application:", self.get_application()


class InstallApplicationChangeRequest(ApplicationChangeRequest):
    """
    Change request for installing an application.
    """
    ACTION = "install_application"
    def __init__(self, api = None, json_data = None):
        super(InstallApplicationChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)


class UninstallApplicationChangeRequest(ApplicationChangeRequest):
    """
    Change request for uninstalling an application.
    """
    ACTION = "uninstall_application"
    def __init__(self, api = None, json_data = None):
        super(UninstallApplicationChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)


class SettingChangeRequest(ChangeRequest):
    """
    Change request involving a setting.
    """
    def __init__(self, api = None, json_data = None):
        super(SettingChangeRequest, self).__init__(api, json_data)

    def get_value(self):
        """
        Provides the new value of setting.
        @return: The value
        @rtype: String
        """
        return self._get_field("value")

    def set_value(self, value):
        """
        Sets the new value of setting.
        @return: The value
        @rtype: String
        """
        return self._set_field("value", value)

    def _show(self, indent = 0):
        super(SettingChangeRequest, self)._show(indent)
        print " "*indent, "Value:", self.get_value()


class AddSettingChangeRequest(SettingChangeRequest):
    """
    Change request for adding a setting to a host.
    """
    ACTION = "add_setting"
    def __init__(self, api = None, json_data = None):
        super(AddSettingChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)

    def get_key(self):
        """
        Provides the key of new setting.
        @return: The key
        @rtype: String
        """
        return self._get_field("key")

    def set_key(self, key):
        """
        Sets the key of new setting.
        @param key: The key
        @param key: String
        """
        self._set_field("key", key)

    def _show(self, indent = 0):
        super(AddSettingChangeRequest, self)._show(indent)
        print " "*indent, "Target host:", self.get_target()
        print " "*indent, "Key:", self.get_key()


class UpdateSettingChangeRequest(SettingChangeRequest):
    """
    Change request for updating an existing setting.
    """
    ACTION = "update_setting"
    def __init__(self, api = None, json_data = None):
        super(UpdateSettingChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)

    def _show(self, indent = 0):
        super(UpdateSettingChangeRequest, self)._show(indent)
        print " "*indent, "Target setting:", self.get_target()


class DeleteSettingChangeRequest(SettingChangeRequest):
    """
    Change request for deleting an existing setting from a host.
    """
    ACTION = "delete_setting"
    def __init__(self, api = None, json_data = None):
        super(DeleteSettingChangeRequest, self).__init__(api, json_data)
        self._set_action(self.ACTION)

    def _show(self, indent = 0):
        super(DeleteSettingChangeRequest, self)._show(indent)
        print " "*indent, "Target setting:", self.get_target()
