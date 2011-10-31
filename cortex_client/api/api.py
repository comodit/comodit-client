# coding: utf-8
"""
Cortex server access point module. An instance of CortexApi class provides an
access to resources and services exhibited by a particular cortex-server.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from cortex_client.rest.client import Client
from directory import Directory
from rendering_service import RenderingService
from application_collection import ApplicationCollection
from change_request_collection import ChangeRequestCollection
from distribution_collection import DistributionCollection
from environment_collection import EnvironmentCollection
from file_collection import FileCollection
from host_collection import HostCollection
from organization_collection import OrganizationCollection
from platform_collection import PlatformCollection
from user_collection import UserCollection

from application import Application
from platform import Platform
from distribution import Distribution
from file import File
from organization import Organization
from environment import Environment
from host import Host

class CortexApi(object):
    """
    Defines the access point to a particular cortex server. An instance of
    CortexApi class may be used to retrieve, create, update and delete resources
    of the server (hosts, applications, etc.).

    Resources handled by the server may listed and accessed using collections.
    There is one collection by resource type (for example, all applications
    defined on a server are part of application collection).
    A collection getter is a method that provides an access point to a collection
    of resources. This class provides all collection getters. These methods
    are named as follows: get_*_collection where * is a resource type.

    Factory methods defined by this class allow to instantiate access points to
    resources (application, distribution, host, etc.) managed by a cortex server.
    These factory methods are named as follows: new_* where * is a resource type.

    Finally, this class defines getters that provide services implemented by the
    server or this client. Currently, 2 services are defined: the directory and
    the rendering service. The directory allows to retrieve the UUID of a
    resource given an identifier (a name or a path). The rendering service
    provides the result of templates' rendering for a particular host.
    """

    def __init__(self, endpoint, username, password):
        """
        Creates an instance of CortexApi using given parameters to connect to
        the server. These parameters include the URL of cortex server's API and
        a user name and a password for authentication.
        
        @param endpoint: The URL of a cortex-server's REST API.
        @type endpoint: String
        @param username: A user name
        @type username: String
        @param password: A password
        @type password: String
        """

        self._client = Client(endpoint, username, password)
        self._directory = Directory(self)
        self._rendering = RenderingService(self)

        self._appl_collection = ApplicationCollection(self)
        self._chan_collection = ChangeRequestCollection(self)
        self._dist_collection = DistributionCollection(self)
        self._envi_collection = EnvironmentCollection(self)
        self._file_collection = FileCollection(self)
        self._host_collection = HostCollection(self)
        self._orga_collection = OrganizationCollection(self)
        self._plat_collection = PlatformCollection(self)
        self._user_collection = UserCollection(self)

    def get_client(self):
        """
        Provides the REST client used by this instance to communicate with
        cortex server's API.

        @return: The REST client
        @rtype: L{Client}
        """
        return self._client

    def get_directory(self):
        """
        Provides an access to the directory of associated cortex server.

        @return: The directory access point
        @rtype: L{Directory}
        """
        return self._directory

    def get_rendering_service(self):
        """
        Provides the rendering service associated to this instance.

        @return: A rendering service instance.
        @rtype: L{RenderingService}
        """
        return self._rendering

    def get_application_collection(self):
        """
        Provides an access to applications collection of associated cortex server.
        
        @return: The applications collection access point
        @rtype: L{ApplicationCollection}
        """
        return self._appl_collection

    def get_change_request_collection(self):
        """
        Provides an access to change requests collection of associated cortex server.

        @return: The change requests collection access point
        @rtype: L{ChangeRequestCollection}
        """
        return self._chan_collection
    
    def get_distribution_collection(self):
        """
        Provides an access to applications collection of associated cortex server.
        
        @return: The applications collection access point
        @rtype: L{ApplicationCollection}
        """
        return self._dist_collection

    def get_environment_collection(self):
        """
        Provides an access to environments collection of associated cortex server.
        
        @return: The environments collection access point
        @rtype: L{EnvironmentCollection}
        """
        return self._envi_collection

    def get_file_collection(self):
        """
        Provides an access to files collection of associated cortex server.
        
        @return: The files collection access point
        @rtype: L{FileCollection}
        """
        return self._file_collection

    def get_host_collection(self):
        """
        Provides an access to hosts collection of associated cortex server.
        
        @return: The hosts collection access point
        @rtype: L{HostCollection}
        """
        return self._host_collection

    def get_organization_collection(self):
        """
        Provides an access to organizations collection of associated cortex server.
        
        @return: The organizations collection access point
        @rtype: L{OrganizationCollection}
        """
        return self._orga_collection

    def get_platform_collection(self):
        """
        Provides an access to platforms collection of associated cortex server.
        
        @return: The platforms collection access point
        @rtype: L{PlatformCollection}
        """
        return self._plat_collection

    def get_user_collection(self):
        """
        Provides an access to users collection of associated cortex server.
        
        @return: The users collection access point
        @rtype: L{UserCollection}
        """
        return self._user_collection

    def new_application(self):
        """
        Factory method for application resource.

        @return: An application connected to associated cortex server.
        @rtype: L{Application}
        """
        return Application(self)

    def new_platform(self):
        """
        Factory method for platform resource.

        @return: A platform connected to associated cortex server.
        @rtype: L{Platform}
        """
        return Platform(self)

    def new_distribution(self):
        """
        Factory method for distribution resource.

        @return: A distribution connected to associated cortex server.
        @rtype: L{Distribution}
        """
        return Distribution(self)

    def new_file(self):
        """
        Factory method for file resource.

        @return: A file connected to associated cortex server.
        @rtype: L{File}
        """
        return File(self)

    def new_organization(self):
        """
        Factory method for organization resource.

        @return: An organization connected to associated cortex server.
        @rtype: L{Organization}
        """
        return Organization(self)

    def new_environment(self):
        """
        Factory method for environment resource.

        @return: An environment connected to associated cortex server.
        @rtype: L{Environment}
        """
        return Environment(self)

    def new_host(self):
        """
        Factory method for host resource.

        @return: A host connected to associated cortex server.
        @rtype: L{Host}
        """
        return Host(self)
