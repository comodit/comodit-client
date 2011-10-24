class RenderingService(object):
    def __init__(self, api):
        self._client = api.get_client()

    def get_rendered_file(self, host_uuid, app_name, file_name):
        content = self._client.read("cms/resources/" + host_uuid + "/" +
                                    app_name + "/" + file_name,
                                    decode=False)
        return content

    def get_rendered_kickstart(self, host_uuid):
        content = self._client.read("provisioner/kickstart.cfg",
                                    parameters = {"hostId" : host_uuid},
                                    decode=False)
        return content
