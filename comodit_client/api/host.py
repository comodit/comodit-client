# coding: utf-8
"""
Provides the classes related to host entity, in particular L{Host}
and L{HostCollection}. L{Host instance entity class<Instance>} is also provided by this
module.
"""
from __future__ import print_function
from __future__ import absolute_import

from builtins import str
from builtins import object
from .exceptions import PythonApiException
import time

from comodit_client.api.audit import AuditLogCollection
from comodit_client.api.collection import Collection
from comodit_client.api.compliance import ComplianceCollection
from comodit_client.api.contexts import ApplicationContextCollection, \
    PlatformContextCollection, DistributionContextCollection
from comodit_client.api.entity import Entity
from comodit_client.api.settings import HasSettings
from comodit_client.rest.exceptions import ApiException
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.api.notificationLog import NotificationLogCollection
from comodit_client.api.agentLog import AgentLogCollection
from comodit_client.api.otherLog import OtherLogCollection
from comodit_client.api.orchestration import OrchestrationCollection


class HostCollection(Collection):
    """
    Collection of hosts. A host collection is owned by an
    L{Environment}.
    """

    def _new(self, json_data = None):
        """
        Instantiates a new Host object with given state.

        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict

        @see: L{Host}
        """

        return Host(self, json_data)

    def new(self, name, description = "", plat = None, dist = None, apps = []):
        """
        Instantiates a new host object.

        @param name: Host's name.
        @type name: string
        @param description: Host's description.
        @type description: string
        @param plat: Name of host's platform.
        @type plat: string
        @param dist: Name of host's distribution.
        @type dist: string
        @param apps: List of application installed on host.
        @type apps: list of string
        @return: a new host object.
        @rtype: L{Host}
        """

        host = self._new()
        host.name = name
        host.description = description
        host.platform_name = plat
        host.distribution_name = dist

        for a in apps:
            host.add_application(a)

        return host

    def create(self, name, description = "", plat = None, dist = None, apps = []):
        """
        Creates a remote host entity and returns associated local
        object.

        @param name: Host's name.
        @type name: string
        @param description: Host's description.
        @type description: string
        @param plat: Name of host's platform.
        @type plat: string
        @param dist: Name of host's distribution.
        @type dist: string
        @param apps: List of application installed on host.
        @type apps: list of string
        @return: a new host object.
        @rtype: L{Host}
        """

        host = self.new(name, description, plat, dist, apps)
        host.create()
        return host


class Property(JsonWrapper):
    """
    A host instance property. A property is composed of a key and a value.
    """

    @property
    def key(self):
        """
        Property's key.

        @rtype: string
        """

        return self._get_field("key")

    @property
    def value(self):
        """
        Property's value.

        @rtype: string
        """

        return self._get_field("value")

    def show(self, indent = 0):
        """
        Prints this property to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "Key:", self.key)
        print(" "*indent, "Value:", self.value)


class Vnc(JsonWrapper):
    """
    A host instance's VNC connection data.
    """

    @property
    def hostname(self):
        """
        The hostname of VNC server.

        @rtype: string
        """

        return self._get_field("hostname")

    @property
    def port(self):
        """
        The TCP port of VNC server.

        @rtype: string
        """

        return self._get_field("port")

    def show(self, indent = 0):
        """
        Prints this VNC connection data to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "hostname:", self.hostname)
        print(" "*indent, "port:", self.port)


class InstanceCollection(Collection):
    """
    Host instance collection. This collection will always contain at most one
    element.
    """

    def __init__(self, client, url):
        super(InstanceCollection, self).__init__(client, url)
        self.accept_empty_id = True

    def _new(self, json_data = None):
        return Instance(self, json_data)

    def new(self):
        """
        Instantiates a new instance object.
        """

        return self._new()

    def create(self):
        """
        Creates remotely a new instance entity and returns associated local
        object. By creating a host instance, host provisioning is triggered.
        """

        instance = self.new()
        instance.create()
        return instance


class Instance(Entity):
    """
    Host instance entity representation. An instance is associated to a host
    when it is provisioned. It has properties describing the VM or physical
    machine associated to the host (e.g. its IP address, public DNS name, etc.)
    and features operations related to VM
    handling: start, pause, resume, power-off and shutdown.
    """

    @property
    def name(self):
        return ""

    def create(self):
        """
        Creates a remote host instance using this object's state for
        initialization. If there are properties associated to this object,
        a "fake" provisioning is executed: host is set in provisioning state
        and properties are associated to the instance, but no VM creation is
        actually triggered. This allows to re-import an instance linked to a
        VM or machine that was already provisioned.
        """

        props = self._get_field("properties")
        if props == None or len(props) == 0:
            self.collection._create(self)
        else:
            self.set_json(self._http_client.create(self.url + "properties", props))

    @property
    def organization(self):
        """
        The name of the organization owning the host this instance is attached
        to.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def environment(self):
        """
        The name of the environment owning the host this instance is attached
        to.

        @rtype: string
        """

        return self._get_field("environment")

    @property
    def host(self):
        """
        The name of this instance's host.

        @rtype: string
        """

        return self._get_field("host")

    @property
    def state(self):
        """
        Instance's state. Possible values are: UNDEFINED, PENDING, RUNNING,
        PAUSED, STOPPED.

        @rtype: string
        """

        return self._get_field("state")

    def get_ip(self, interface):
        """
        Retrieves the IP address associated to given interface from instance
        properties.

        @param interface: An interface name (e.g. eth0).
        @type interface: string
        @return: An IP address or None if no address was found.
        @rtype: string
        """

        props = self.properties
        for p in props:
            if p.key == "ip." + interface:
                return p.value
        return None

    @property
    def hostname(self):
        """
        Instance's hostname.

        @rtype: string
        """

        return self._get_field("hostname")

    @property
    def vnc(self):
        """
        Fetches instance's VNC connection data from server.

        @rtype: L{Vnc}
        """

        return Vnc(self._http_client.read(self.url + "vnc"))

    @property
    def agent_state(self):
        """
        Agent's state. Possible values are 'Up' and 'Down'.

        @rtype: string
        """

        return self._get_field("synapseState")

    @property
    def properties(self):
        """
        Instance's properties.

        @rtype: list of L{Property}
        """

        return self._get_list_field("properties", lambda x: Property(x))

    def get_property(self, key):
        """
        Retrieves the value of a property.

        @param key: Property's key.
        @type key: string
        @return: Property value or None if no property was found.
        @rtype: string
        """

        for p in self.properties:
            if p.key == key:
                return p.value
        return None

    def alerts(self):
        """
        Instantiates MonitorinAlert collection.

        @return: MonitoringAlert collection.
        @rtype: L{MonitoringAlertCollection}
        """

        return MonitoringAlertCollection(self.client, self.url + "alerts/")


    def get_file_content(self, path):
        """
        Retrieves the content of a file on a host's instance.

        @param path: The absolute path to a particular file.
        @type path: string
        @return: a reader to file's content.
        @rtype: file-like object
        """

        try:
            return self._http_client.read(self.url + "files", parameters = {"path": path}, decode = False)
        except ApiException as e:
            raise PythonApiException("Unable to get file: " + e.message)

    def get_status(self, collection, sensor):
        """
        Retrieves the value of a monitoring sensor on a host's instance.

        @param collection: The collection to query (e.g. host, apache).
        @param sensor: The specific sensor to query.
        @type collection: string
        @type sensor: string
        @return: the value read from the sensor.
        @rtype: string
        """

        try:
            result = self._http_client.read(self.url + "status" + "/" + collection + "/" + sensor, decode = True)
            return result["status"][sensor]
        except ApiException as e:
            raise PythonApiException("Unable to get sensor content: " + e.message)

    def start(self):
        """
        Starts instance.
        """

        try:
            result = self._http_client.update(self.url + "_start", decode = False)
            if(result.getcode() != 202):
                raise PythonApiException("Call not accepted by server")
        except ApiException as e:
            raise PythonApiException("Unable to start host: " + e.message)

    def pause(self):
        """
        Pauses instance.
        """

        result = self._http_client.update(self.url + "_pause", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def resume(self):
        """
        Resumes instance's execution (after pause).
        """

        result = self._http_client.update(self.url + "_resume", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def shutdown(self):
        """
        Shuts instance down.
        """

        result = self._http_client.update(self.url + "_stop", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def poweroff(self):
        """
        Powers instance off.
        """

        try:
            result = self._http_client.update(self.url + "_off", decode = False)
            if(result.getcode() != 202):
                raise PythonApiException("Call not accepted by server")
        except ApiException as e:
            raise PythonApiException("Unable to power instance off: " + e.message)

    def forget(self):
        """
        Forgets instance.
        """

        try:
            result = self._http_client.update(self.url + "_forget", decode = False)
            if result.getcode() != 202:
                raise PythonApiException("Call not accepted by server")
        except ApiException as e:
            raise PythonApiException("Unable to forget instance: " + e.message)

    def _show(self, indent = 0):
        """
        Prints instance's information to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "State:", self.state)
        print(" "*indent, "Agent state:", self.agent_state)
        print(" "*indent, "Hostname:", self.hostname)
        print(" "*indent, "Vnc:")
        self.vnc.show(indent + 2)

    def show_properties(self, indent = 0):
        """
        Prints instance's properties to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "Properties:")
        props = self.properties
        for p in props:
            print(" "*(indent + 2), p.key, ":", p.value)

    def wait_for_property(self, key, time_out = 0):
        """
        Waits until a property with given key appears (or a time-out occurs) in
        remote instance's state and returns its value. If a time-out occurred, the
        method returns None.

        @param key: Property's key.
        @type key: string
        @param time_out: A time-out expressed in seconds. A time-out of 0 seconds
        means no time-out (method can wait forever).
        @type time_out: int
        @return: The value associated to given key.
        @rtype: string
        """

        self.refresh()
        start_time = time.time()
        while not self.get_property(key):
            time.sleep(3)
            now = time.time()
            if time_out > 0 and (now - start_time) > time_out:
                return None
            self.refresh()
        return self.get_property(key)

    def wait_for_address(self, time_out = 0):
        """
        Waits until remote instance's IP address or DNS name is known. If a
        time-out occurred, the method may return None. The returned value is
        one of the following (in a decreasing priority order i.e. first available
        is returned):
          1. Public DNS name
          2. Public IP address
          3. eth0 IP address

        @param time_out: A time-out expressed in seconds. A time-out of 0 seconds
        means no time-out (method can wait forever).
        @type time_out: int
        @return: The instance's address.
        @rtype: string
        """

        ip = self.wait_for_property("ip.eth0", time_out)
        hostname = self.get_property("publicDnsName")
        publicip = self.get_property("publicIp")
        if hostname:
            return hostname
        elif publicip:
            return publicip
        else:
            return ip

    def wait_for_state(self, state, time_out = 0):
        """
        Waits until instance has requested state.

        @param state: The expected state (see L{Instance.State}).
        @type state: string
        @param time_out: A time-out expressed in seconds. A time-out of 0 seconds
        means no time-out (method can wait forever).
        @type time_out: int
        """

        start_time = time.time()
        self.refresh()
        while self.state != state:
            time.sleep(3)
            now = time.time()
            if time_out > 0 and (now - start_time) > time_out:
                break
            self.refresh()

    def create_image(self, image):
        """
        Creates an image based on provided template.

        @param image: the image template
        @type image: L{Image}
        """

        result = self._http_client.update(self.url + "_create_image", item=image.get_json(), decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Could not create image")


class Task(JsonWrapper):
    """
    Represents a task of a L{host<Host>}'s particular L{change<Change>}.
    """

    @property
    def order_num(self):
        """
        The order number of this task in the change.

        @rtype: int
        """

        return self._get_field("orderNum")

    @property
    def description(self):
        """
        The description of this task.

        @rtype: string
        """

        return self._get_field("description")

    @property
    def status(self):
        """
        The task's status. Possible values are OK, PENDING or ERROR.

        @rtype: string
        """

        return self._get_field("status")

    @property
    def error(self):
        """
        If task's status is ERROR, a description of the error.

        @rtype: string
        """

        return self._get_field("error")

    def show(self, indent = 0):
        """
        Prints tasks's information to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "Number:", self.order_num)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Status:", self.status)

        if self.status == "ERROR":
            print(" "*indent, "Error: '" + self.error + "'")


class Change(Entity):
    """
    A host's change. A change is a group of ordered tasks that must be applied
    to a host to bring it in a new state. For instance, installing an
    application on a host implies that a change is queued, the change being
    composed of tasks such as the installation of a package, the update of
    configuration files, etc. Note that a change is read-only, it cannot be
    updated, but it may be deleted.
    """

    @property
    def identifier(self):
        return str(self.order_num)

    @property
    def name(self):
        return self.identifier

    @property
    def label(self):
        return self.identifier + " - " + self.description

    @property
    def order_num(self):
        """
        The order number of this change.

        @rtype: int
        """

        return self._get_field("orderNum")

    @property  
    def change_id(self):
        """
        The id of change

        @rtype: string
        """

        return self._get_field("key")

    @property
    def tasks(self):
        """
        The tasks associated to this change.

        @rtype: list of L{Task}
        """

        return self._get_list_field("tasks", lambda x: Task(x))

    def are_tasks_pending(self):
        """
        Tells if tasks of this change are still pending.

        @return: True if tasks are still pending, false otherwise.
        @rtype: bool
        """

        for t in self.tasks:
            if t.status == "PENDING":
                return True
        return False

    def get_tasks_error(self):
        """
        get all tasks in error

        @return: return a list of error tasks
        @rtype:  L{Task}
        """

        result = []
        for t in self.tasks:
            if t.status == "ERROR":
                result.append(t)
        return result

    def _show(self, indent = 0):
        print(" "*indent, "Number:", self.order_num)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Tasks:")
        tasks = self.tasks
        for t in tasks:
            t.show(indent + 2)


class ChangeCollection(Collection):
    """
    Collection of L{changes<Change>}. A change collection is owned by a
    L{Host}. Changes cannot be updated nor created, however they may be deleted.
    Also, this collection supports clear operation (i.e. deletion of all
    changes associated to a particular host).
    """

    def _new(self, json_data = None):
        return Change(self, json_data)

    def list(self, parameters = {}, show_processed = False):
        """
        Fetches the changes in this collection.

        @param parameters: Query parameters to send to ComodIT server.
        @type parameters: dict of string
        @param show_processed: If true, asks all changes to the server, including
        already processed changes.
        @return: The list of changes in this collection.
        @rtype: list of L{Change}
        """

        params = parameters.copy()
        params["show_processed"] = show_processed
        return super(ChangeCollection, self).list(parameters = params)

class MonitoringAlert(Entity):
    """
    TODO
    """

    @property
    def identifier(self):
        return str(self.timestamp)

    @property
    def name(self):
        return self.identifier

    @property
    def label(self):
        return "%s/%s: %s" % (self.plugin, self.sensor, self.output)

    @property
    def timestamp(self):
        """
        The timestamp of the alert.

        @rtype: int
        """

        return self._get_field("timestamp")

    @property
    def plugin(self):
        """
        The plugin the alert relates to.

        @rtype: string
        """

        return self._get_field("collection")

    @property
    def sensor(self):
        """
        The sendor from the plugin the alert relates to.

        @rtype: string
        """

        return self._get_field("property")

    @property
    def output(self):
        """
        The outout of the alert.

        @rtype: string
        """

        return self._get_field("output")

    @property
    def threshold(self):
        """
        The threshold of the alert.

        @rtype: string
        """

        return self._get_field("threshold")

    @property
    def level(self):
        """
        The level of the alert.

        @rtype: string
        """

        return self._get_field("level")

    @property
    def comparator(self):
        """
        The compare method used for the alert.

        @rtype: string
        """

        return self._get_field("compare_method")

    def _show(self, indent = 0):
        print(" "*indent, "Timestamp:", self.timestamp)
        print(" "*indent, "Plugin:", self.plugin)
        print(" "*indent, "Sensor:", self.sensor)
        print(" "*indent, "Output:", self.output)

class MonitoringAlertCollection(Collection):
    """
    TODO
    """

    def _new(self, json_data = None):
        return MonitoringAlert(self, json_data)

class Host(HasSettings):
    """
    A host. A host is part of an L{environment<Environment>} and has L{settings<Setting>}
    associated to it. It features a list of installed L{applications<Application>}, is associated
    to a L{platform<Platform>} and a L{distribution<Distribution>}. Applications,
    distribution and platform associated to a host can be configured using
    settings, the configuration of each application, distribution and platform
    is contained by a L{context<AbstractContext>}.
    When a host is provisioned, an L{instance<Instance>} is associated to it.

    The definition of a host can be modified by the user, however operations
    may have to be undergone on host's instance: L{changes<Change>}
    are queued and are being processed by ComodIT. As long as changes are pending,
    host's instance does not yet meet the new definition.

    Another reason for which a host's instance does comply with the definition
    of ComodIT is the modification on the host's instance of resources managed
    by ComodIT, for example the deletion of an application's file. In this case,
    a L{compliance error<ComplianceError>} is associated to the host.

    A host entity owns the following collections:
      - settings (L{settings()})
      - platform context (L{platform()})
      - distribution context (L{distribution()})
      - application contexts (L{applications()})
      - changes (L{changes()})
      - compliance errors (L{compliance()})
      - audit logs (L{audit_logs()})
    """

    class State(object):
        """
        The states a host can be in. States have the following meaning:
          - DEFINED: the host is defined in ComodIT but has not yet a VM or
          physical machine associated to it.
          - PROVISIONING: the host's instance is being created and configured (OS and
          applications are being installed).
          - READY: host has been successfully provisioned and is ready to be used.
          - UPDATING: host's instance is not yet in the state defined in ComodIT.
          This generally means that changes are pending.
          - ERROR: Host's instance is either not compliant anymore (i.e.
          resources installed on the machine have diverged from what is defined
          in ComodIT, for example when someone modified a file created by ComodIT),
          either encountered an error during an update (in this case, at least
          one change's task has an error status).
        """

        DEFINED = "DEFINED"
        PROVISIONING = "PROVISIONING"
        READY = "READY"
        UPDATING = "UPDATING"
        ERROR = "ERROR"


    @property
    def organization(self):
        """
        The name of the organization this host is part of.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def environment(self):
        """
        The name of the environment this host is part of.

        @rtype: string
        """

        return self._get_field("environment")

    @environment.setter
    def environment(self, name):
        """
        Sets the environment this host is part of. Changing this value
        will actually move the host from one environment to another on next
        call to update.

        @param name: The name of target environment.
        @type name: string
        """

        return self._set_field("environment", name)

    @property
    def platform_name(self):
        """
        The name of the platform associated to this host.

        @rtype: string
        """

        return self._get_field("platform")

    @platform_name.setter
    def platform_name(self, platform):
        """
        Sets the name of the platform associated to this host. This field is only
        considered by the server at creation time. In order to set/change the platform
        associated to a host later, one has to (re-)create the platform context
        associated to this host (see L{Host.platform()}).

        @param platform: The name of the platform.
        @type platform: string
        """

        self._set_field("platform", platform)

    @property
    def distribution_name(self):
        """
        The name of the distribution associated to this host.

        @rtype: string
        """
        return self._get_field("distribution")

    @distribution_name.setter
    def distribution_name(self, distribution):
        """
        Sets the name of the distribution associated to this host. This field is only
        considered by the server at creation time. In order to set/change the distribution
        associated to a host later, one has to (re-)create the distribution context
        associated to this host (see L{Host.distribution()}).

        @param distribution: The name of the distribution.
        @type distribution: string
        """

        self._set_field("distribution", distribution)

    @property
    def application_names(self):
        """
        The name of the applications installed on to this host.

        @rtype: list of string
        """

        return self._get_list_field("applications")

    @application_names.setter
    def application_names(self, applications):
        """
        Sets the applications installed on this host. This field is only
        considered by the server at creation time. In order to set/change the list of applications
        installed on this host later, one has to (re-)create the application contexts
        associated to this host (see L{Host.applications()}).
        """

        self._set_list_field("applications", applications)

    def add_application(self, app_name):
        """
        Adds an application to install on this host. This field is only
        considered by the server at creation time. In order to install an application
        on this host later, use L{Host.install()} or explicitly create an
        application context (see L{Host.applications()}).
        """

        self._add_to_list_field("applications", app_name)

    @property
    def state(self):
        """
        The host's state.

        @rtype: L{State}
        """

        return self._get_field("state")

    def instance(self):
        """
        Instantiates host's instance collection. This collection contains at
        most one element.

        @return: The host's instance collection.
        @rtype: L{InstanceCollection}
        """

        return InstanceCollection(self.client, self.url + "instance/")

    def get_instance(self):
        """
        Fetches host's instance.

        @return: Host's instance.
        @rtype: L{Instance}
        """

        return self.instance().get()

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Organization:", self.organization)
        print(" "*indent, "Environment:", self.environment)
        print(" "*indent, "Platform:", self.platform_name)
        print(" "*indent, "Distribution:", self.distribution_name)
        print(" "*indent, "State:", self.state)

    def provision(self):
        """
        Triggers host's provisioning. A distribution and a platform must be
        associated to the host in order to provision it.

        @return: The host's instance.
        @rtype: L{Instance}
        """

        return self.instance().create()

    def __render_file(self, collection, file_name):
        try:
            response = self._http_client.read(collection + "/files/" + file_name, decode = False)
            return self._http_client.decode(response)
        except ApiException as e:
            raise PythonApiException("Unable to render file: " + e.message)

    def render_app_file(self, app_name, file_name):
        """
        Fetches the rendered version of an application's file. The returned value
        is a file-like object like returned by C{urllib2.urlopen}.
        See U{ComodIT documentation<http://www.comodit.com/resources/api/rendering.html>}
        for more information about file rendering.

        @param app_name: The name of the application.
        @type app_name: string
        @param file_name: The name of the file to render.
        @type file_name: string
        @return: a reader to the content.
        @rtype: string
        """

        return self.__render_file(self.url + "applications/" + app_name, file_name)

    def render_dist_file(self, file_name):
        """
        Fetches the rendered version of a distribution's file. The returned value
        is a file-like object like returned by C{urllib2.urlopen}.
        See U{ComodIT documentation<http://www.comodit.com/resources/api/rendering.html>}
        for more information about file rendering.

        @param file_name: The name of the file to render.
        @type file_name: string
        @return: a reader to the content.
        @rtype: string
        """

        return self.__render_file(self.url + "distribution", file_name)

    def render_plat_file(self, file_name):
        """
        Fetches the rendered version of a platform's file. The returned value
        is a file-like object like returned by C{urllib2.urlopen}.
        See U{ComodIT documentation<http://www.comodit.com/resources/api/rendering.html>}
        for more information about file rendering.

        @param file_name: The name of the file to render.
        @type file_name: string
        @return: a reader to the content.
        @rtype: string
        """

        return self.__render_file(self.url + "platform", file_name)

    def __get_link(self, collection, file_name, short = False):
        try:
            args = {"short" : str(short)}
            result = self._http_client.read(collection + "/files/" + file_name + "/link", parameters = args)
            if "url" in result:
                return result["url"]
            else:
                raise PythonApiException("Could not recover link")
        except ApiException as e:
            raise PythonApiException("Unable to render file: " + e.message)

    def get_app_link(self, app_name, file_name, short = False):
        """
        Requests a one-time URL for a rendered application file. A one-time URL is
        accessible without authentication but has a limited life-time.

        @param app_name: The name of application.
        @type app_name: string
        @param file_name: The name of file.
        @type file_name: string
        @param short: If true, a shorter URL is generated.
        @type short: bool
        @return: A one-time URL.
        @rtype: string
        """

        return self.__get_link(self.url + "applications/" + app_name, file_name, short)

    def get_dist_link(self, file_name, short = False):
        """
        Requests a one-time URL for a rendered distribution file. A one-time URL is
        accessible without authentication but has a limited life-time.

        @param file_name: The name of file.
        @type file_name: string
        @param short: If true, a shorter URL is generated.
        @type short: bool
        @return: A one-time URL.
        @rtype: string
        """

        return self.__get_link(self.url + "distribution", file_name, short)

    def get_plat_link(self, file_name, short = False):
        """
        Requests a one-time URL for a rendered platform file. A one-time URL is
        accessible without authentication but has a limited life-time.

        @param file_name: The name of file.
        @type file_name: string
        @param short: If true, a shorter URL is generated.
        @type short: bool
        @return: A one-time URL.
        @rtype: string
        """

        return self.__get_link(self.url + "platform", file_name, short)

    def clone(self):
        """
        Requests the cloning of remote host. Cloned host have DEFINED state.

        @return: The representation of host's clone.
        @rtype: L{Host}
        """

        try:
            result = self._http_client.update(self.url + "_clone")
            return Host(self.collection, result)
        except ApiException as e:
            raise PythonApiException("Unable to clone host: " + e.message)

    def applications(self):
        """
        Instantiates application contexts collection.

        @return: Application contexts collection.
        @rtype: L{ApplicationContextCollection}
        """

        return ApplicationContextCollection(self.client, self.url + "applications/")

    def get_application(self, name):
        """
        Fetches an application context from server.

        @param name: Application's name.
        @type name: string
        @return: Requested application context.
        @rtype: L{ApplicationContext}
        """

        return self.applications().get(name)

    def platform(self):
        """
        Instantiates platform context collection.

        @return: Platform context collection.
        @rtype: L{PlatformContextCollection}
        """

        return PlatformContextCollection(self.client, self.url + "platform/")

    def get_platform(self):
        """
        Fetches the platform context from server.

        @return: The platform context.
        @rtype: L{PlatformContext}
        """

        return self.platform().get()

    def distribution(self):
        """
        Instantiates distribution context collection.

        @return: Distribution context collection.
        @rtype: L{DistributionContextCollection}
        """

        return DistributionContextCollection(self.client, self.url + "distribution/")

    def get_distribution(self):
        """
        Fetches the distribution context from server.

        @return: The distribution context.
        @rtype: L{DistributionContext}
        """

        return self.distribution().get()

    def changes(self):
        """
        Instantiates changes collection.

        @return: Changes collection.
        @rtype: L{ChangeCollection}
        """

        return ChangeCollection(self.client, self.url + "changes/")

    def all_changes(self):
        """
        Instantiates changes collection.

        @return: Changes collection.
        @rtype: L{ChangeCollection}
        """

        return ChangeCollection(self.client, self.url + "changes/").list(show_processed=True)


    def get_change(self, num):
        """
        Fetches a change from server.

        @param num: The order number of the change.
        @type num: string
        @return: The change.
        @rtype: L{Change}
        """

        return self.changes().get(num)

    def audit_logs(self):
        """
        Instantiates audit logs collection.

        @return: Audit logs collection.
        @rtype: L{AuditLogCollection}
        """

        return AuditLogCollection(self.client, self.url + "audit/")
    
    def notification_logs(self):
        """
        Instantiates the collection of notification logs associated to this host.
       
        @return: The collection of notification logs associated to this host.
        @rtype: L{NotificationLogCollection}
        """

        return NotificationLogCollection(self.client, self.url + "notification/")


    def agent_logs(self):
        """
        Instantiates the collection of agent logs associated to this host.
       
        @return: The collection of agent logs associated to this host.
        @rtype: L{AgentLogCollection}
        """

        return AgentLogCollection(self.client, self.url + "other/")

    def other_logs(self):
        """
        Instantiates the collection of other logs associated to this host.
       
        @return: The collection of other logs associated to this host.
        @rtype: L{OtherLogCollection}
        """

        return OtherLogCollection(self.client, self.url + "other/")    

    def compliance(self):
        """
        Instantiates compliance errors collection.

        @return: Compliance errors collection.
        @rtype: L{ComplianceCollection}
        """

        return ComplianceCollection(self.client, self.url + "compliance/")

    def get_compliance_error(self, identifier):
        """
        Fetches a particular compliance error from server.

        @param identifier: Compliance error's identifier. It
        must have the following form: 'applications/I{app_name}/I{collection}/I{id}'
        where I{app_name} is the name of an application installed on the host,
        I{collection} on of (services, files, packages, users, groups, repos)
        and I{id} the name of the application's resource.
        @type identifier: L{ComplianceError}
        @return: The compliance error.
        @rtype: L{ComplianceError}
        """

        return self.compliance().get(identifier)

    def live_update_file(self, app_name, file_name):
        """
        Requests the update of a file on provisioned machine. This may, for
        instance, solve a compliance error linked to target file by resetting
        file's content to its original value. A change is queued and
        exposes the result of the operation.

        @param app_name: The name of file's application.
        @type app_name: string
        @param file_name: The file's name.
        @type file_name: string
        """

        self._http_client.update(self.url + "applications/" + app_name + "/files/" + file_name + "/_update", decode = False)
        
    def run_orchestration(self, orchestration_name):
        """
        Requests to run orchestration on provisioned machine. 

        @param orchestration_name: The name of orchestration.
        @type orchestration_name: string
        """

        return self._http_client.update(self.url + "orchestration/" + orchestration_name + "/_run", decode = True)

    def get_orchestrations(self):
        """
        Requests to get orchestrations available on host 
        
        @return: The collection of orchestrations available on host.
        @rtype: L{OrchestrationCollection}

        """
        return OrchestrationCollection(self.client, self.url + "orchestrations")
        
    def live_restart_service(self, app_name, svc_name):
        """
        Requests the restart of a service on provisioned machine. This may, for
        instance, solve a compliance error linked to target service by resetting
        its state. A change is queued and exposes the result of the operation.

        @param app_name: The name of service's application.
        @type app_name: string
        @param svc_name: The service's name.
        @type svc_name: string
        """

        self._http_client.update(self.url + "applications/" + app_name + "/services/" + svc_name + "/_restart", decode = False)

    def live_update_service(self, app_name, svc_name):
        """
        Requests the update of a service on provisioned machine. This may, for
        instance, solve a compliance error linked to target service by resetting
        its state. A change is queued and exposes the result of the operation.

        @param app_name: The name of service's application.
        @type app_name: string
        @param svc_name: The service's name.
        @type svc_name: string
        """

        self._http_client.update(self.url + "applications/" + app_name + "/services/" + svc_name + "/_update", decode = False)

    def live_enable_service(self, app_name, svc_name):
        """
        Enables a service on a machine.

        @param app_name: The name of service's application.
        @type app_name: string
        @param svc_name: The service's name.
        @type svc_name: string
        """

        self._http_client.update(self.url + "applications/" + app_name + "/services/" + svc_name + "/_enable", decode = False)

    def live_disable_service(self, app_name, svc_name):
        """
        Disables a service on a machine.

        @param app_name: The name of service's application.
        @type app_name: string
        @param svc_name: The service's name.
        @type svc_name: string
        """

        self._http_client.update(self.url + "applications/" + app_name + "/services/" + svc_name + "/_disable", decode = False)

    def live_update_package(self, app_name, pkg_name, pkg_version):
        """
        Requests the update of a package on provisioned machine. This may, for
        instance, solve a compliance error linked to target package having been
        removed. A change is queued and exposes the result of the operation.

        @param app_name: The name of file's application.
        @type app_name: string
        @param pkg_name: The package's name.
        @type pkg_name: string
        @param pkg_version: The package's version.
        @type pkg_version: string
        """

        res = PackageResource()
        res.name = pkg_name
        res.release = pkg_version

        self._http_client.update(self.url + "applications/" + app_name + "/packages/" + pkg_name, res.get_json(), decode = False)

    def install(self, name, settings = {}):
        """
        Installs an application on this host.

        @param name: The name of the application to install.
        @type name: string
        @param settings: The configuration of the application. It is given in the form
        of a dict of strings: key-values are the key-values of the settings to
        create i.e. dictionary {"k":"v"} implies the creation of a single setting
        having key "k" and value "v". Value may be any valid JSON object.
        @type settings: dict
        """

        self.applications().create(name, settings)

    def uninstall(self, name):
        """
        Uninstalls an application from this host.

        @param name: The name of the application.
        @type name: string
        """

        self.applications().delete(name)

    def wait_for_state(self, state, time_out = 0):
        """
        Waits until host has requested state.

        @param state: The expected state (see L{Host.State}).
        @type state: string
        @param time_out: A time-out expressed in seconds. A time-out of 0 seconds
        means no time-out (method can wait forever).
        @type time_out: int
        """

        start_time = time.time()
        self.refresh()
        while self.state != state:
            time.sleep(3)
            now = time.time()
            if time_out > 0 and (now - start_time) > time_out:
                break
            self.refresh()

    def _are_changes_pending(self):
        for c in self.changes():
            if c.are_tasks_pending():
                return True
        return False

    def _change_terminated(self, changeId):
        for c in self.all_changes():
            if c.change_id == changeId:
                taskErrors = c.get_tasks_error()
                if taskErrors:
                    for t in taskErrors:
                        print("error ", t.error)
                    return True;
                if c.are_tasks_pending():
                    return False
        return True

    def wait_for_pending_changes(self, time_out = 0):
        """
        Waits until host has no more pending changes.

        @param time_out: A time-out expressed in seconds. A time-out of 0 seconds
        means no time-out (method can wait forever).
        @type time_out: int
        """

        start_time = time.time()
        while self._are_changes_pending():
            time.sleep(3)
            now = time.time()
            if time_out > 0 and (now - start_time) > time_out:
                break

    def wait_for_change_terminated(self, change_id, time_out = 0):
        start_time = time.time()
        while not self._change_terminated(change_id):
            time.sleep(3)
            now = time.time()
            if time_out > 0 and (now - start_time) > time_out:
                break


class PackageResource(JsonWrapper):
    
    @property
    def name(self):
        return self._get_field("name")
    
    @name.setter
    def name(self, name):
        
        self._set_field("name", name)

    @property
    def release(self):
        return self._get_field("release")
    
    @release.setter
    def release(self, release):
        
        self._set_field("release", release)