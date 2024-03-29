# coding: utf-8
"""
Provides the classes related to organization entity, in particular L{Organization}
and L{OrganizationCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from .environment import EnvironmentCollection
from .distribution import DistributionCollection
from .platform import PlatformCollection
from .application import ApplicationCollection
from comodit_client.api.settings import HasSettings
from comodit_client.rest.exceptions import ApiException
from comodit_client.api.exceptions import PythonApiException
from comodit_client.api.audit import AuditLogCollection
from comodit_client.api.purchased import PurchasedCollection
from comodit_client.api.application_key import ApplicationKeyCollection
from comodit_client.api.job import JobCollection
from comodit_client.api.notification import NotificationCollection
from comodit_client.api.agentLog import AgentLogCollection
from comodit_client.api.otherLog import OtherLogCollection
from comodit_client.api.orchestration import OrchestrationCollection
from comodit_client.api.pipeline import PipelineCollection
from comodit_client.api.webhook import WebhookCollection
from comodit_client.api.hostGroup import HostGroupCollection
from comodit_client.api.group import GroupCollection
from comodit_client.api.group import Group
from comodit_client.api.group import GroupOrganizationTreeCollection


class OrganizationCollection(Collection):
    """
    Collection of L{organizations<Organization>}. This is a root collections.
    """

    def __init__(self, client):
        """
        Creates a new organizations collection instance.

        @param client: The client.
        @type client: L{Client}
        """

        super(OrganizationCollection, self).__init__(client, "organizations/")

    def _new(self, json_data = None):
        return Organization(self, json_data)

    def new(self, name):
        """
        Instantiates a new organization representation.
        
        @param name: The name of the new organization.
        @type name: string
        @return: The new organization representation.
        @rtype: L{Organization}
        """

        org = self._new()
        org.name = name
        return org

    def create(self, name, populate = True):
        """
        Creates a new remote organization and returns the associated instance.

        @param name: The name of the new organization.
        @type name: string
        @param populate: If true, new organization is pre-filled by ComodIT.
        @type populate: bool
        @return: The new organization representation.
        @rtype: L{Organization}
        """

        org = self.new(name)
        org.create(parameters = {"populate" : "true" if populate else "false"})
        return org


class Organization(HasSettings):
    """
    An organization's representation. An organization contains a list of
    L{environments<Environment>}, L{applications<Application>}, L{platforms<Platform>}
    and L{distributions<Distribution>}. The L{hosts<Host>} defined
    in organization's environments can only use platforms, distributions and
    applications from this organization. Note that applications and distributions
    of an organization may have been purchased from store.
    Several ComodIT users can share the
    same organization, access control is configured by adding/removing users
    from organization's L{groups<Group>}.
    An organization may have settings, these settings being available to all
    hosts in its environment.

    An organization owns the following collections:
      - settings (L{settings()})
      - environments (L{environments()})
      - applications (L{applications()})
      - distributions (L{distributions()})
      - platforms (L{platforms()})
      - audit logs (L{audit_logs()})
      - groups (L{groups()})
      - purchased applications (L{purchased_apps()})
      - purchased distributions (L{purchased_dists()})
    """

    @property
    def environment_names(self):
        """
        The name of organization's environments.

        @rtype: list of string
        """

        return self._get_list_field("environments")

    @property
    def group_names(self):
        """
        The name of organization's groups.

        @rtype: list of string
        """

        return self._get_list_field("groups")

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Access Key:", self.access_key)
        print(" "*indent, "Secret Key:", self.secret_key)

        print(" "*indent, "Environments:")
        for e in self.environment_names:
            print(" "*(indent + 2), e)

        print(" "*indent, "Groups:")
        for g in self.group_names:
            print(" "*(indent + 2), g)

    def applications(self):
        """
        Instantiates the collection of applications associated to this organization.

        @return: The collection of applications associated to this organization.
        @rtype: L{ApplicationCollection}
        """

        return ApplicationCollection(self.client, self.url + "applications/")

    def get_application(self, name):
        """
        Fetches an application of this organization given its name.

        @param name: The name of the application.
        @type name: string
        @rtype: L{Application}
        """

        return self.applications().get(name, return_error_code=self.return_error_code)

    def platforms(self):
        """
        Instantiates the collection of applications associated to this organization.

        @return: The collection of applications associated to this organization.
        @rtype: L{ApplicationCollection}
        """

        return PlatformCollection(self.client, self.url + "platforms/")

    def get_platform(self, name):
        """
        Fetches an application of this organization given its name.

        @param name: The name of the application.
        @type name: string
        @rtype: L{Application}
        """

        return self.platforms().get(name, return_error_code=self.return_error_code)

    def distributions(self):
        """
        Instantiates the collection of distributions associated to this organization.

        @return: The collection of distributions associated to this organization.
        @rtype: L{DistributionCollection}
        """

        return DistributionCollection(self.client, self.url + "distributions/")

    def get_distribution(self, name):
        """
        Fetches a distribution of this organization given its name.

        @param name: The name of the distribution.
        @type name: string
        @rtype: L{Distribution}
        """

        return self.distributions().get(name, return_error_code=self.return_error_code)

    def environments(self):
        """
        Instantiates the collection of environments associated to this organization.

        @return: The collection of environments associated to this organization.
        @rtype: L{EnvironmentCollection}
        """

        return EnvironmentCollection(self.client, self.url + "environments/")

    def jobs(self):
        """
        Instantiates the collection of jobs associated to this organization.

        @return: The collection of jobs associated to this organization.
        @rtype: L{JobCollection}
        """

        return JobCollection(self.client, self.url + "jobs/")

    def orchestrations(self):
        """
        Instantiates the collection of orchestrations associated to this organization.

        @return: The collection of orchestrations associated to this organization.
        @rtype: L{OrchestrationCollection}
        """

        return OrchestrationCollection(self.client, self.url + "orchestrations/")

    def pipelines(self):
        """
        Instantiates the collection of pipelines associated to this organization.

        @return: The collection of pipelines associated to this organization.
        @rtype: L{PipelineCollection}
        """

        return PipelineCollection(self.client, self.url + "pipelines/")

    def webhooks(self):
        """
        Instantiates the collection of webhooks associated to this organization.

        @return: The collection of webhooks associated to this organization.
        @rtype: L{WebhookCollection}
        """

        return WebhookCollection(self.client, self.url + "webhooks/")

    def host_groups(self):
        """
        Instantiates the collection of hostGroups associated to this organization.

        @return: The collection of hostGroups associated to this organization.
        @rtype: L{HostGroupCollection}
        """

        return HostGroupCollection(self.client, self.url + "hostgroups/")

    def get_host_groups(self, name):
        return self.host_groups().get(name)

    def notifications(self):
        """
        Instantiates the collection of notifications associated to this organization.

        @return: The collection of notifications associated to this organization.
        @rtype: L{NotificationCollection}
        """
        return NotificationCollection(self.client, self.url + "notifications/")

    def get_environment(self, name):
        """
        Fetches an environment of this organization given its name.

        @param name: The name of the environment.
        @type name: string
        @rtype: L{Environment}
        """

        return self.environments().get(name)

    def groups(self):
        """
        Instantiates the collection of groups associated to this organization.

        @return: The collection of groups associated to this organization.
        @rtype: L{GroupCollection}
        """

        return GroupCollection(self.client, self.url + "groups/")

    def groupsTree(self):
        """
        Get all groups defined in all organization

        @return: The collection of groups associated to this organization.
        @rtype: L{GroupOrganizationTreeCollection}
        """
        return GroupOrganizationTreeCollection(self.client, self.url + "groups").get("/tree")

    def get_group(self, name):
        """
        Fetches a group of this organization given its name.

        @param name: The name of the group.
        @type name: string
        @rtype: L{Group}
        """

        return self.groups().get(name)

    @property
    def access_key(self):
        """
        The access key of this organization.

        @rtype: string
        """

        access = self._get_field("access")
        if not access is None:
            return access["accessKey"]
        else:
            return None

    @property
    def secret_key(self):
        """
        The secret key of this organization.

        @rtype: string
        """

        access = self._get_field("access")
        if not access is None:
            return access["secretKey"]
        else:
            return None

    def reset_secret(self):
        """
        Resets the secret key of this organization.
        """

        try:
            self._http_client.create(self.url + "access")
        except ApiException as e:
            raise PythonApiException("Could not reset secret key: " + e.message)

    def audit_logs(self):
        """
        Instantiates the collection of audit logs associated to this organization.

        @return: The collection of audit logs associated to this organization.
        @rtype: L{AuditLogCollection}
        """

        return AuditLogCollection(self.client, self.url + "audit/")
    
    def notification_logs(self):
        """
        Instantiates the collection of notification logs associated to this organization.
       
        @return: The collection of notification logs associated to this organization.
        @rtype: L{NotificationLogCollection}
        """

        return NotificationLogCollection(self.client, self.url + "notification/")

    def agent_logs(self):
        """
        Instantiates the collection of agent logs associated to this organization.
       
        @return: The collection of agent logs associated to this organization.
        @rtype: L{AgentLogCollection}
        """

        return AgentLogCollection(self.client, self.url + "agent/")

    def other_logs(self):
        """
        Instantiates the collection of other logs associated to this organization.
       
        @return: The collection of other logs associated to this organization.
        @rtype: L{OtherLogCollection}
        """

        return OtherLogCollection(self.client, self.url + "other/")

    def purchased_apps(self):
        """
        Instantiates the collection of purchased applications associated to this organization.

        @return: The collection of purchased applications associated to this organization.
        @rtype: L{PurchasedCollection}
        """

        return PurchasedCollection(self.client, self.url + "purchased/applications/")

    def get_purchased_app(self, uuid):
        """
        Fetches a purchased application.

        @param uuid: The UUID of the purchased application.
        @type uuid: string
        @rtype: L{PurchasedEntity}
        """

        return self.purchased_apps().get(uuid)

    def purchased_dists(self):
        """
        Instantiates the collection of purchased distributions associated to this organization.

        @return: The collection of purchased distributions associated to this organization.
        @rtype: L{PurchasedCollection}
        """

        return PurchasedCollection(self.client, self.url + "purchased/distributions/")

    def get_purchased_dist(self, uuid):
        """
        Fetches a purchased distribution.

        @param uuid: The UUID of the purchased distribution.
        @type uuid: string
        @rtype: L{PurchasedEntity}
        """

        return self.purchased_dists().get(uuid)

    def application_keys(self):
        """
        Instantiates the collection of application keys associated to this organization.

        @return: The collection of application keys associated to this organization.
        @rtype: L{ApplicationKeyCollection}
        """

        return ApplicationKeyCollection(self.client, self.url + "applicationkeys/")

    def get_application_key(self, name):
        """
        Instantiates the collection of application keys associated to this organization.

        @return: The collection of application keys associated to this organization.
        @rtype: L{ApplicationKeyCollection}
        """

        return ApplicationKey(self.client, self.url + "applicationkeys/" + name)
