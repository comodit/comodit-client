# coding: utf-8
"""
Directory module. A directory is used to search for the UUID of an entity given
an identifier.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from exceptions import NotFoundException

class Directory(object):
    """
    An instance of Directory is an access point to the directory service of a
    cortex server. The directory allows to obtain the UUID of an entity given
    a name or a path.
    """
    def __init__(self, api):
        """
        Instantiates a directory.
        
        @param api: The access point to cortex server's API.
        """
        self._client = api.get_client()

    def get_application_uuid(self, name):
        """
        Provides the UUID of an application given its name.
        
        @param name: Application's name
        @type name: String
        """
        reference = self._client.read("directory/application/" + name)
        if(not reference):
            raise NotFoundException("Application not found")
        return reference["uuid"]

    def get_platform_uuid(self, name):
        """
        Provides the UUID of a platform given its name.
        
        @param name: Platform's name
        @type name: String
        """
        reference = self._client.read("directory/platform/" + name)
        if(not reference):
            raise NotFoundException("Platform not found")
        return reference["uuid"]

    def get_distribution_uuid(self, name):
        """
        Provides the UUID of a distribution given its name.
        
        @param name: Distribution's name
        @type name: String
        """
        reference = self._client.read("directory/distribution/" + name)
        if(not reference):
            raise NotFoundException("Distribution not found")
        return reference["uuid"]

    def get_environment_uuid(self, org_name, env_name):
        """
        Provides the UUID of an environment given its name and the name of
        its enclosing organization.
        
        @param org_name: Enclosing organization's name
        @type org_name: String
        @param env_name: Environment's name
        @type env_name: String
        """
        path = org_name + "/" + env_name
        return self.get_environment_uuid_from_path(path)

    def get_environment_uuid_from_path(self, path):
        """
        Provides the UUID of an environment given its path. The path to 
        environment "env" enclosed by organization "org" is "org/env".
        
        @param path: The path
        @type path: String
        """
        reference = self._client.read("directory/organization/" + path)
        if(not reference):
            raise NotFoundException("Environment not found")
        return reference["uuid"]

    def get_host_uuid(self, org_name, env_name, host_name):
        """
        Provides the UUID of a host given its name, the name of
        its enclosing environment and the name of environment's organization.
        
        @param org_name: Organization's name
        @type org_name: String
        @param env_name: Environment's name
        @type env_name: String
        @param host_name: Host's name
        @type host_name: String
        """
        path = org_name + "/" + env_name + "/" + host_name
        self.get_host_uuid_from_path(path)

    def get_host_uuid_from_path(self, path):
        """
        Provides the UUID of a host given its path. The path to 
        host "host" of environment I{e} is "org/env/host" where "org/env" is the
        path to environment I{e}.
        
        @param path: Host's path
        @type path: String
        """
        reference = self._client.read("directory/organization/" + path)
        if(not reference):
            raise NotFoundException("Host not found")
        return reference["uuid"]

    def get_organization_uuid(self, org_name):
        """
        Provides the UUID of an organization given its name.
        
        @param org_name: Organization's name
        @type org_name: String
        """
        reference = self._client.read("directory/organization/" + org_name)
        if(not reference):
            raise NotFoundException("Organization not found")
        return reference["uuid"]

    def get_user_uuid(self, name):
        """
        Provides the UUID of a user given its name.
        
        @param name: User's name
        @type name: String
        """
        reference = self._client.read("directory/user/" + name)
        if(not reference):
            raise NotFoundException("User not found")
        return reference["uuid"]
