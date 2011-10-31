# coding: utf-8
"""
Change request collection module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from collection import Collection
from change_request import *
from exceptions import PythonApiException

class ChangeRequestCollection(Collection):
    """
    Change request collection. Collection of the change requests available on a
    cortex server.
    """

    def __init__(self, api):
        """
        Creates a new ChangeRequestCollection instance.
        
        @param api: Access point to a server
        @type api: L{CortexApi}
        """
        super(ChangeRequestCollection, self).__init__("changes", api)

    def _new_resource(self, json_data):
        """
        Instantiates a new ChangeRequest object with given state.

        @param json_data: A quasi-JSON representation of change request's state.
        @type json_data: dict

        @see: L{ChangeRequest}
        """

        if(not json_data.has_key("action")):
            raise PythonApiException("Given JSON is not a change request")

        action = json_data["action"]
        if(action == InstallApplicationChangeRequest.ACTION):
            return InstallApplicationChangeRequest(self._api, json_data)
        elif (action == UninstallApplicationChangeRequest.ACTION):
            return UninstallApplicationChangeRequest(self._api, json_data)
        elif (action == AddSettingChangeRequest.ACTION):
            return AddSettingChangeRequest(self._api, json_data)
        elif (action == UpdateSettingChangeRequest.ACTION):
            return UpdateSettingChangeRequest(self._api, json_data)
        elif (action == DeleteSettingChangeRequest.ACTION):
            return DeleteSettingChangeRequest(self._api, json_data)

        raise PythonApiException("Unknown change request type: " + action)

    def get_uuid(self, identifier):
        """
        Retrieves the UUID of a change request given its identifier. A change
        request has no other identifier than the UUID itself. This method
        therefore returns given identifier unchanged.

        @param identifier: The identifier of a change request
        @type identifier: String
        """
        return identifier
