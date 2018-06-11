# coding: utf-8
"""
The modules in this package provide classes that describe entities handled
by a ComodIT server (hosts, applications, etc.) as well as tools easing the
handling of these entities. 

All ComodIT entity representations inherit from L{Entity} class which
defines generic operations, in particular creation, update and deletion of
remote entities. Note that a C{Entity} instance is
only the local (i.e. in RAM) representation of a remote instance. Therefore,
altering the state of a local instance does not automatically update remote
object (see L{Entity} class for more details).

Entities are accessed through collections. Each collection is represented by
a class that inherits from L{Collection}. 
Collections may be associated to a particular entity. In this case, the
entity I{owns} the collection and all the entities in the collection.
Collections that are not associated to an entity are called I{root collections}.
These are accessible through an instance of L{Client} which represents a
connection to a ComodIT server. This object is mandatory to any interaction
with a server using this library.

Any entity is reachable starting from one of root collections' entity.
Indeed, ComodIT's data model defines the following structure (each item represents
an entity type or collection, entity representation is given; when an item has a
sub-list, it means each entity of the collection has a collection associated
to it):
  - organizations (see L{Organization})
    - settings (see L{Setting})
    - applications (see L{Application})
      - parameters (see L{Parameter})
      - application files (see L{ApplicationFile})
    - platforms (see L{Platform})
      - parameters (see L{Parameter})
      - settings (see L{Setting})
    - distributions (see L{Distribution})
      - parameters (see L{Parameter})
      - settings (see L{Setting})
    - environments (see L{Environment})
      - settings (see L{Setting})
      - hosts (see L{Host})
        - settings (see L{Setting})
    - groups (see L{organization.Group})
    - purchased applications (see L{PurchasedEntity})
    - purchased distributions (see L{PurchasedEntity})
  - flavors (see L{Flavor})
  - published applications (see L{PublishedApplication})
  - published distributions (see L{PublishedDistribution})

Below script illustrates the usage of defined classes. I{org} is an instance
of L{Organization}, I{host} is an instance of L{Host}.

    >>> from comodit_client.api import Client
    ... 
    ... # Connect to ComodIT
    ... client = Client('https://my.comodit.com/api', 'UUU', 'PPP')
    ... 
    ... # Create host
    ... org = client.get_organization('OOO')
    ... host = org.get_environment('Default').hosts().create('my-new-host', '', 'Demo Platform', 'Demo Distribution')
    ... 
    ... # Provision host
    ... host.provision()
    ... host.wait_for_state('READY')
    ... 
    ... # Install an application
    ... host.install('Wordpress', {'wp_admin_password': 'XXX', 'wp_admin_email': 'YYY@ZZZ'})
    ... host.wait_for_pending_changes()
    ... 
    ... # Retrieve instance's hostname
    ... hostname = host.get_instance().get_property('publicDnsName')
    ... print "Wordpress available at http://" + hostname + "/"
    ... 
    ... # Delete host and its instance
    ... host.get_instance().delete()
    ... host.delete()
"""
from __future__ import absolute_import

from builtins import object
from comodit_client.rest.client import HttpClient

from .flavors import FlavorCollection, Flavor
from .organization import OrganizationCollection, Organization
from .store import AppStoreCollection, DistStoreCollection
from .application import Application
from .distribution import Distribution
from .platform import Platform
from .environment import Environment
from .host import Host


class Client(object):
    """
    Represents a connection to a particular ComodIT server. An instance of
    this class gives access to most collections as well as helpers easing the
    access to ComodIT entities.
    """

    def __init__(self, endpoint, username, password, token, insecure_upload = False):
        """
        Client constructor. In order to create a client, the URL to a ComodIT
        server's REST API (e.g. http://my.comodit.com/api) must be provided, in
        addition to connection credentials (username and password).

        @param endpoint: The URL of a ComodIT server's REST API.
        @type endpoint: String
        @param username: A user name
        @type username: String
        @param password: A password
        @type password: String
        @param token: A token
        @type token: String
        """

        self._http_client = HttpClient(endpoint, username, password, token, insecure_upload)
        self._organizations = OrganizationCollection(self)
        self._flavors = FlavorCollection(self)
        self._app_store = AppStoreCollection(self)
        self._dist_store = DistStoreCollection(self)


    # Flavors helpers

    def flavors(self):
        """
        Provides root collection of flavors.

        @rtype: L{FlavorCollection}
        """

        return self._flavors

    def get_flavor(self, name):
        """
        Fetches a particular flavor given its name.

        @param name: Flavor's name.
        @type name: string
        @rtype: L{Flavor}
        """

        return self.flavors().get(name)


    # Store helpers

    def app_store(self):
        """
        Provides root collection of published applications.

        @rtype: L{AppStoreCollection}
        """

        return self._app_store

    def get_published_app(self, uuid, org_name = None):
        """
        Fetches a published application given its UUID. Note that an organization
        name may also be provided in order to access private published
        applications i.e. applications published to a limited audience.

        @param uuid: Published application's UUID.
        @type uuid: string
        @param org_name: Organization through which you want to access published
        application (mandatory if the access is restricted).
        @type org_name: string
        @rtype: L{PublishedApplication}
        """

        return self.app_store().get(uuid, org_name = org_name)

    def dist_store(self):
        """
        Provides root collection of published distributions.

        @rtype: L{DistStoreCollection}
        """

        return self._dist_store

    def get_published_dist(self, uuid, org_name = None):
        """
        Fetches a published distribution given its UUID. Note that an organization
        name may also be provided in order to access private published
        distributions i.e. distributions published to a limited audience.

        @param uuid: Published distribution's UUID.
        @type uuid: string
        @param org_name: Organization through which you want to access published
        distribution (mandatory if the access is restricted).
        @type org_name: string
        @rtype: L{PublishedDistribution}
        """

        return self.dist_store().get(uuid, org_name = org_name)


    # Organizations helpers

    def organizations(self):
        """
        Provides root collection of organizations. The organizations that may
        be accessed through this collection depend on the access rights of
        used principal.
        
        @rtype: L{OrganizationCollection}
        """
        return self._organizations

    def __get_unresolved_org(self, name):
        return self.organizations().new(name)

    def get_organization(self, name):
        """
        Fetches an organization given its name.

        @param name: Organization's name.
        @type name: string
        @rtype: L{Organization}
        """
        return self.organizations().get(name)


    # Applications helpers

    def applications(self, org_name):
        """
        Instantiates the collection of applications associated to named
        organization.

        @param org_name: The name of the organization owning requested collection.
        @type org_name: string
        @rtype: L{ApplicationCollection}
        """
        return self.__get_unresolved_org(org_name).applications()

    def __get_unresolved_app(self, org_name, name):
        return self.applications(org_name).new(name)

    def get_application(self, org_name, name):
        """
        Fetches an application given the name of owning organization and its
        name.

        @param org_name: The name of the organization owning requested application.
        @type org_name: string
        @param name: The name of the application.
        @type name: string
        @rtype: L{Application}
        """
        return self.applications(org_name).get(name)


    # Distributions helpers

    def distributions(self, org_name):
        """
        Instantiates the collection of distributions associated to named
        organization.

        @param org_name: The name of the organization owning requested collection.
        @type org_name: string
        @rtype: L{DistributionCollection}
        """
        return self.__get_unresolved_org(org_name).distributions()

    def __get_unresolved_dist(self, org_name, name):
        return self.distributions(org_name).new(name)

    def get_distribution(self, org_name, name):
        """
        Fetches a distribution given the name of owning organization and its
        name.

        @param org_name: The name of the organization owning requested distribution.
        @type org_name: string
        @param name: The name of the distribution.
        @type name: string
        @rtype: L{Distribution}
        """
        return self.distributions(org_name).get(name)


    # Platforms helpers

    def platforms(self, org_name):
        """
        Instantiates the collection of platforms associated to named
        organization.

        @param org_name: The name of the organization owning requested collection.
        @type org_name: string
        @rtype: L{PlatformCollection}
        """

        return self.__get_unresolved_org(org_name).platforms()

    def __get_unresolved_plat(self, org_name, name):
        return self.platforms(org_name).new(name)

    def get_platform(self, org_name, name):
        """
        Fetches a platform given the name of owning organization and its
        name.

        @param org_name: The name of the organization owning requested platform.
        @type org_name: string
        @param name: The name of the platform.
        @type name: string
        @rtype: L{Platform}
        """

        return self.platforms(org_name).get(name)


    # Environments helpers

    def environments(self, org_name):
        """
        Instantiates the collection of environments associated to named
        organization.

        @param org_name: The name of the organization owning requested collection.
        @type org_name: string
        @rtype: L{EnvironmentCollection}
        """

        return self.__get_unresolved_org(org_name).environments()

    def jobs(self, org_name):
        """
        Instantiates the collection of jobs associated to named
        organization.

        @param org_name: The name of the organization owning requested collection.
        @type org_name: string
        @rtype: L{JobCollection}
        """

        return self.__get_unresolved_org(org_name).jobs()
    
    def notifications(self, org_name):
        """
        Instantiates the collection of notifications associated to named
        organization.

        @param org_name: The name of the organization owning requested collection.
        @type org_name: string
        @rtype: L{NotificationCollection}
        """

        return self.__get_unresolved_org(org_name).notifications()

    def __get_unresolved_env(self, org_name, name):
        return self.environments(org_name).new(name)

    def get_environment(self, org_name, name):
        """
        Fetches an environment given the name of owning organization and its
        name.

        @param org_name: The name of the organization owning requested platform.
        @type org_name: string
        @param name: The name of the environment.
        @type name: string
        @rtype: L{Environment}
        """

        return self.environments(org_name).get(name)


    # Hosts helpers

    def hosts(self, org_name, env_name):
        """
        Instantiates the collection of hosts associated to a particular
        environment.

        @param org_name: The name of the organization owning the environment.
        @type org_name: string
        @param env_name: The name of the environment owning requested collection.
        @type env_name: string
        @rtype: L{HostCollection}
        """

        return self.__get_unresolved_env(org_name, env_name).hosts()

    def __get_unresolved_host(self, org_name, env_name, name):
        return self.hosts(org_name, env_name).new(name)

    def get_host(self, org_name, env_name, name):
        """
        Fetches a host given its name and owning environment.

        @param org_name: The name of the organization owning the environment.
        @type org_name: string
        @param env_name: The name of the environment owning the host.
        @type env_name: string
        @param name: The name of the host.
        @type name: string
        @rtype: L{Host}
        """

        return self.hosts(org_name, env_name).get(name)


    # Application Keys helpers

    def application_keys(self, org_name):
        """
        Instantiates the collection of environments associated to named
        organization.

        @param org_name: The name of the organization owning requested collection.
        @type org_name: string
        @rtype: L{EnvironmentCollection}
        """

        return self.__get_unresolved_org(org_name).application_keys()

    def __get_unresolved_application_key(self, org_name, token):
        return self.application_keys(org_name).new(token)

    def get_application_key(self, org_name, token):
        """
        Fetches an environment given the name of owning organization and its
        name.

        @param org_name: The name of the organization owning requested platform.
        @type org_name: string
        @param name: The name of the environment.
        @type name: string
        @rtype: L{Environment}
        """

        return self.application_keys(org_name).get(token)
