# coding: utf-8
"""
Rendering service module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

class RenderingService(object):
    """
    Rendering service. This service is used to render templates given context.
    Rendering service does not exist as is server-side. It uses functionalities
    exposed by server's cms and provisioner services.
    """
    def __init__(self, api):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        """
        self._client = api.get_client()

    def get_rendered_file(self, host_uuid, app_name, file_name):
        """
        Renders the file of a given application if it were installed on a
        particular host.
        @param host_uuid: The UUID of a host
        @type host_uuid: String
        @param app_name: The name of an application
        @type app_name: String
        @param file_name: The name of a file of given application
        @type file_name: String
        """
        content = self._client.read("cms/resources/" + host_uuid + "/" +
                                    app_name + "/" + file_name,
                                    decode = False)
        return content

    def get_rendered_kickstart(self, host_uuid):
        """
        Renders the kickstart file of a given host.
        @param host_uuid: The UUID of a host
        @type host_uuid: String
        """
        content = self._client.read("provisioner/kickstart.cfg",
                                    parameters = {"hostId" : host_uuid},
                                    decode = False)
        return content
