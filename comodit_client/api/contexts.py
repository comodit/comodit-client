# coding: utf-8
"""
Provides all classes related to the configuration of a distribution
(L{DistributionContext}), a platform (L{PlatformContext}) or an application
(L{ApplicationContext}) when associated to a host. Related collections are also
provided by this module.
"""
from __future__ import print_function

from comodit_client.api.collection import Collection
from comodit_client.api.settings import HasSettings, add_settings


class AbstractContext(HasSettings):
    """
    Base class of all contexts. A context is a container for the settings
    configuring an entity when associated to a host. Note that a context cannot
    be renamed nor updated. In order to change the configuration of an entity,
    settings should be modified directly.
    """

    @property
    def organization(self):
        """
        The name of the organization owning the host this context is attached
        to.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def environment(self):
        """
        The name of the environment owning the host this context is attached
        to.

        @rtype: string
        """

        return self._get_field("environment")

    @property
    def host(self):
        """
        The name of the host this context is attached to.

        @rtype: string
        """

        return self._get_field("host")


class ApplicationContextCollection(Collection):
    """
    Application contexts collection. Update is not supported.
    """

    def _new(self, json_data = None):
        return ApplicationContext(self, json_data)

    def new(self, app_name, settings = {}):
        """
        Instantiates a new application context associated to a particular
        application (that must be owned by the organization this host is owned
        by).

        @param app_name: The name of the application.
        @type app_name: string
        @param settings: A dictionary describing the settings to add to this
        context (see L{this function's specification<add_settings>} for expected
        data model).
        @type settings: dict
        """

        ctxt = self._new()
        ctxt.application = app_name
        add_settings(ctxt, settings)
        return ctxt

    def create(self, app_name, settings = {}):
        """
        Creates remotely a new application context associated to a particular
        application (that must be owned by the organization this host is owned
        by). The creation of an application context means the application is
        actually installed on host.
        """

        ctxt = self.new(app_name, settings)
        ctxt.create()
        return ctxt

class ApplicationContext(AbstractContext):
    """
    An application context. An application context is attached to each application
    installed on a host.
    """

    @property
    def name(self):
        return self.application

    @property
    def label(self):
        return self.application

    @property
    def application(self):
        """
        The name of the application this context configures.

        @rtype: string
        """

        return self._get_field("application")

    @application.setter
    def application(self, application):
        """
        Sets the name of the application this context configures.

        @param application: The name of the application this context configures.
        @type application: string
        """

        self._set_field("application", application)

    def run_handler(self, name):
        """
        Requests the execution of the handler associated to given custom action key. Return changeId on host

        @param key: The key of a custom action.
        @type key: string

        @rtype: string
        """

        result = self._http_client.update(self.url + "handler/" + name + "/_run", decode = False)
        return result.read().decode('utf-8')

    def _show(self, indent = 0):
        print(" "*indent, "Application:", self.application)
        self._show_settings(indent)


class DistributionContextCollection(Collection):
    """
    Distribution context collection. Update is not supported. This collection
    will always contain at most one element. If the collection already contains
    a context, a newly created context will replace the old one.
    """

    def __init__(self, client, url):
        super(DistributionContextCollection, self).__init__(client, url)
        self.accept_empty_id = True

    def _new(self, json_data = None):
        return DistributionContext(self, json_data)

    def new(self, dist_name, settings = {}):
        """
        Instantiates a new distribution context associated to a particular
        distribution (that must be owned by the organization this host is owned
        by).

        @param dist_name: The name of the distribution.
        @type dist_name: string
        @param settings: A dictionary describing the settings to add to this
        context (see L{this function's specification<add_settings>} for expected
        data model).
        @type settings: dict
        """

        ctxt = self._new()
        ctxt.distribution = dist_name
        add_settings(ctxt, settings)
        return ctxt

    def create(self, dist_name, settings = {}):
        """
        Creates remotely a new distribution context associated to a particular
        distribution (that must be owned by the organization this host is owned
        by). If a distribution was already associated to the host, the association
        is lost and replaced by this one.
        """

        ctxt = self.new(dist_name, settings)
        ctxt.create()
        return ctxt


class DistributionContext(AbstractContext):
    """
    An distribution context. An distribution context represents the association
    of a distribution with a host.
    """

    @property
    def name(self):
        return ""

    @property
    def url(self):
        return self.collection.url

    @property
    def distribution(self):
        """
        The name of the distribution this context configures.

        @rtype: string
        """

        return self._get_field("distribution")

    @distribution.setter
    def distribution(self, distribution):
        """
        Sets the name of the distribution this context configures.

        @param distribution: The name of the distribution this context configures.
        @type distribution: string
        """

        self._set_field("distribution", distribution)

    def _show(self, indent = 0):
        print(" "*indent, "Distribution:", self.distribution)
        self._show_settings(indent)


class PlatformContextCollection(Collection):
    """
    Platform context collection. Update is not supported. This collection
    will always contain at most one element. If the collection already contains
    a context, a newly created context will replace the old one.
    """

    def __init__(self, client, url):
        super(PlatformContextCollection, self).__init__(client, url)
        self.accept_empty_id = True

    def _new(self, json_data = None):
        return PlatformContext(self, json_data)

    def new(self, plat_name, settings = {}):
        """
        Instantiates a new platform context associated to a particular
        platform (that must be owned by the organization this host is owned
        by).

        @param plat_name: The name of the platform.
        @type plat_name: string
        @param settings: A dictionary describing the settings to add to this
        context (see L{this function's specification<add_settings>} for expected
        data model).
        @type settings: dict
        """

        ctxt = self._new()
        ctxt.platform = plat_name
        add_settings(ctxt, settings)
        return ctxt

    def create(self, plat_name, settings = {}):
        """
        Creates remotely a new platform context associated to a particular
        platform (that must be owned by the organization this host is owned
        by). If a platform was already associated to the host, the association
        is lost and replaced by this one.
        """

        ctxt = self.new(plat_name, settings)
        ctxt.create()
        return ctxt

class PlatformContext(AbstractContext):
    """
    An platform context. An platform context represents the association
    of a platform with a host.
    """

    @property
    def name(self):
        return ""

    @property
    def url(self):
        return self.collection.url

    @property
    def platform(self):
        """
        The name of the platform this context configures.

        @rtype: string
        """

        return self._get_field("platform")

    @platform.setter
    def platform(self, platform):
        """
        Sets the name of the platform this context configures.

        @param platform: The name of the platform this context configures.
        @type platform: string
        """

        self._set_field("platform", platform)

    def _show(self, indent = 0):
        print(" "*indent, "Platform:", self.platform)
        self._show_settings(indent)
