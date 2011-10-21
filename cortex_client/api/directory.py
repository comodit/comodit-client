from exceptions import NotFoundException

class Directory(object):
    def __init__(self, api):
        self._client = api.get_client()

    def get_application_uuid(self, name):
        reference = self._client.read("directory/application/" + name)
        if(not reference):
            raise NotFoundException("Application not found")
        return reference["uuid"]

    def get_platform_uuid(self, name):
        reference = self._client.read("directory/platform/" + name)
        if(not reference):
            raise NotFoundException("Platform not found")
        return reference["uuid"]

    def get_distribution_uuid(self, name):
        reference = self._client.read("directory/distribution/" + name)
        if(not reference):
            raise NotFoundException("Distribution not found")
        return reference["uuid"]

    def get_environment_uuid(self, org_name, env_name):
        path = org_name + "/" + env_name
        return self.get_environment_uuid_from_path(path)

    def get_environment_uuid_from_path(self, path):
        reference = self._client.read("directory/organization/" + path)
        if(not reference):
            raise NotFoundException("Environment not found")
        return reference["uuid"]

    def get_host_uuid(self, org_name, env_name, host_name):
        path = org_name + "/" + env_name + "/" + host_name
        self.get_host_uuid_from_path(path)

    def get_host_uuid_from_path(self, path):
        reference = self._client.read("directory/organization/" + path)
        if(not reference):
            raise NotFoundException("Host not found")
        return reference["uuid"]

    def get_organization_uuid(self, org_name):
        reference = self._client.read("directory/organization/" + org_name)
        if(not reference):
            raise NotFoundException("Organization not found")
        return reference["uuid"]

    def get_user_uuid(self, name):
        reference = self._client.read("directory/user/" + name)
        if(not reference):
            raise NotFoundException("User not found")
        return reference["uuid"]