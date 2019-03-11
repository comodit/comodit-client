# coding: utf-8
"""
Provides all classes related to application entity, in particular L{Application}
and L{ApplicationCollection}. Other classes include application resources
(representing OS entities managed by ComodIT) and
handlers describing actions to manipulate the application resources when triggered.

Application resources:
  - files (L{ApplicationFile})
  - packages (L{Package})
  - services (L{Service})
  - users (L{User})
  - groups (L{Group})
  - repositories (L{Repository})

Handler: L{Handler}
"""
from __future__ import print_function
from __future__ import absolute_import

from comodit_client.api.collection import Collection
from comodit_client.api.exceptions import PythonApiException
from comodit_client.api.files import FileEntity
from comodit_client.api.parameters import HasParameters
from comodit_client.api.store import IsStoreCapable
from comodit_client.rest.exceptions import ApiException
from comodit_client.util.json_wrapper import JsonWrapper
from .files import File


class ApplicationCollection(Collection):
    """
    Collection of applications. An application collection is owned by an
    L{Organization}.
    """

    def _new(self, json_data = None):
        """
        Instantiates a new application object from given state (if any).

        @param json_data: JSON representation of an application.
        @type json_data: dict
        @rtype: L{Application}
        """

        return Application(self, json_data)

    def new(self, name, description = ""):
        """
        Instantiates a new application object.

        @param name: The name of new application.
        @type name: string
        @param description: The description of new application.
        @type description: string
        @rtype: L{Application}
        """

        app = self._new()
        app.name = name
        app.description = description
        return app

    def create(self, name, description = ""):
        """
        Creates a remote application entity and returns associated local
        object.

        @param name: The name of new application.
        @type name: string
        @param description: The description of new application.
        @type description: string
        @rtype: L{Application}
        """

        app = self.new(name, description)
        app.create()
        return app


class ApplicationResource(JsonWrapper):
    """
    Base application resource representation.
    """

    @property
    def name(self):
        """
        Resource's name.

        @rtype: string
        """

        return self._get_field("name")

    @name.setter
    def name(self, name):
        """
        Sets resource's name.

        @type name: string
        """

        return self._set_field("name", name)

    def show(self, indent = 0):
        """
        Prints this resource's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, self.name)


class Package(ApplicationResource):
    """
    Application's package resource. This resource represents a package (RPM,
    DEB, etc.) associated to the application.
    """

    pass


class Repository(ApplicationResource):
    """
    Application's repository resource. This resource represents a package
    repository. A repository is generally described by a name and a URL.
    """

    @property
    def location(self):
        """
        Location of the repository. This is generally a URL.
        
        @rtype: string
        """

        return self._get_field("location")

    @location.setter
    def location(self, location):
        """
        Sets repository's location.
        
        @param location: New repository's location.
        @type location: string
        """

        return self._set_field("location", location)

    def show(self, indent = 0):
        """
        Prints this repository's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, self.name + ":")
        print(" "*(indent + 2), "Location:", self.location)


class User(ApplicationResource):
    """
    Application's user resource. This resource represents a user of the operating
    system the application might be installed on.
    """

    @property
    def login_group(self):
        """
        User's login group.
        
        @rtype: string
        """

        return self._get_field("loginGroup")

    @login_group.setter
    def login_group(self, group):
        """
        Sets user's login group.

        @param group: New user's login group.
        @type group: string
        """

        return self._set_field("loginGroup", group)

    @property
    def groups(self):
        """
        List of user's groups.

        @rtype: list of string
        """

        return self._get_list_field("groups")

    @groups.setter
    def groups(self, groups):
        """
        Sets list of user's groups.

        @param groups: New list of user's groups.
        @type groups: list of string
        """

        return self._set_list_field("groups", groups)

    def add_group(self, group):
        """
        Adds a group to user's groups.

        @param group: A group name.
        @type group: string
        """

        self._add_to_list_field("groups", group)

    @property
    def gid(self):
        """
        User's GID.

        @rtype: string
        """

        return self._get_field("gid")

    @gid.setter
    def gid(self, gid):
        """
        Sets user's GID.

        @param gid: User's new GID.
        @type gid: string
        """

        return self._set_field("gid", gid)

    @property
    def uid(self):
        """
        User's UID.

        @rtype: string
        """

        return self._get_field("uid")

    @uid.setter
    def uid(self, uid):
        """
        Sets user's UID.

        @param uid: User's UID.
        @type uid: string
        """

        return self._set_field("uid", uid)

    @property
    def password(self):
        """
        User's password.

        @rtype: string
        """

        return self._get_field("password")

    @password.setter
    def password(self, password):
        """
        Sets user's password.

        @param password: User's password.
        @type password: string
        """

        return self._set_field("password", password)

    @property
    def home(self):
        """
        User's home directory.
        
        @rtype: string
        """

        return self._get_field("home")

    @home.setter
    def home(self, home):
        """
        Sets user's home directory.

        @param home: User's home directory.
        @type home: string
        """

        return self._set_field("home", home)

    @property
    def full_name(self):
        """
        User's full name.

        @rtype: string
        """

        return self._get_field("fullName")

    @full_name.setter
    def full_name(self, full_name):
        """
        Sets user's full name.

        @param full_name: User's full name.
        @type full_name: string
        """

        return self._set_field("fullName", full_name)

    @property
    def shell(self):
        """
        User's shell.
        
        @rtype: string
        """

        return self._get_field("shell")

    @shell.setter
    def shell(self, shell):
        """
        Sets user's shell.

        @param shell: User's shell.
        @type shell: string
        """

        return self._set_field("shell", shell)

    @property
    def system(self):
        """
        Flag telling if the user should be created as a system user or not.

        @rtype: bool
        """

        return self._get_field("system")

    @system.setter
    def system(self, system):
        """
        Sets user's system flag.

        @param system: User's system flag.
        @type system: bool
        """

        return self._set_field("system", system)

    def show(self, indent = 0):
        """
        Prints this user's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, self.name + ":")
        print(" "*(indent + 2), "Login group:", self.login_group)
        print(" "*(indent + 2), "Groups:")
        for g in self.groups:
            print(" "*(indent + 4), g)
        print(" "*(indent + 2), "Password:", self.password)
        print(" "*(indent + 2), "UID:", self.uid)
        print(" "*(indent + 2), "GID:", self.gid)
        print(" "*(indent + 2), "Home:", self.home)
        print(" "*(indent + 2), "Full name:", self.full_name)
        print(" "*(indent + 2), "Shell:", self.shell)
        print(" "*(indent + 2), "System:", self.system)


class Group(ApplicationResource):
    """
    Application's group resource. This resource represents a group of the operating
    system the application might be installed on.
    """

    @property
    def gid(self):
        """
        Group's GID.

        @rtype: string
        """

        return self._get_field("gid")

    @gid.setter
    def gid(self, gid):
        """
        Sets group's GID.

        @param gid: Group's new GID.
        @type gid: string
        """

        return self._set_field("gid", gid)

    def show(self, indent = 0):
        """
        Prints this group's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, self.name + ":")
        print(" "*(indent + 2), "GID:", self.gid)


class Service(ApplicationResource):
    """
    Application's service resource. This resource represents a service of the
    operating system.
    """

    @property
    def enabled(self):
        """
        Indicates if the service should be enabled at boot time.

        @rtype: bool
        """

        return self._get_field("enabled")

    @enabled.setter
    def enabled(self, enabled):
        """
        Sets that the service should be enabled at boot time or not.

        @param enabled: True if the service should be enabled at boot time, false otherwise.
        @type enabled: bool
        """

        return self._set_field("enabled", enabled)

    def show(self, indent = 0):
        """
        Prints this service's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, self.name + ":")
        print(" "*(indent + 2), "enabled:", self.enabled)


class ApplicationFile(FileEntity):
    """
    Application's file resource. This resource represents a file of the
    operating system. This is a special application resource: it is also a
    ComodIT entity with an associated collection. Rules when dealing with
    ComodIT entities should therefore be followed.

    @see: L{Entity}
    """

    @property
    def owner(self):
        """
        File's owner name.

        @rtype: string
        """

        return self._get_field("owner")

    @owner.setter
    def owner(self, owner):
        """
        Sets file's owner name.

        @param owner: New file's owner.
        @type owner: string
        """

        self._set_field("owner", owner)

    @property
    def group(self):
        """
        File's group name.

        @rtype: string
        """

        return self._get_field("group")

    @property
    def mode(self):
        """
        File mode (in the form of 3 or 4 octal digits).

        @rtype: string
        """

        return self._get_field("mode")

    @property
    def file_path(self):
        """
        File's absolute path.

        @rtype: string
        """
        return self._get_field("path")

    @property
    def template(self):
        """
        File's template. Note that this template is not associated to any
        collection.

        @rtype: L{File}
        """

        return self._get_field("template", lambda x: File(None, x))

    @template.setter
    def template(self, template):
        """
        Sets file's template.

        @param template: A template.
        @type template: L{File}
        """
        self._set_field("template", template)

    def _show(self, indent = 0):
        """
        Prints this file's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, self.name + ":")
        print(" "*(indent + 2), "owner:", self.owner)
        print(" "*(indent + 2), "group:", self.group)
        print(" "*(indent + 2), "mode:", self.mode)
        print(" "*(indent + 2), "path:", self.file_path)
        template = self.template
        if template:
            print(" "*(indent + 2), "template:")
            template._show(indent + 4)


class ApplicationFileCollection(Collection):
    """
    Application file resources collection.
    """

    def _new(self, json_data = None):
        """
        Instantiates a new application file resource object.
        
        @param json_data: initial state of the object.
        @type json_data: dict
        @return: A new instance of application file resource.
        @rtype: L{ApplicationFile}
        """

        return ApplicationFile(self, json_data)


class Action(JsonWrapper):
    """
    An handler's action.

    @see: L{Handler}
    """

    @property
    def type(self):
        """
        Action's type. Possible values are 'update', 'execute', 'restart' and 'reload'.

        @rtype: string
        """

        return self._get_field("action")

    @property
    def resource(self):
        """
        The application resource this action is applied on.
        This may be a service or a file. Resources are referred to using the
        following notation: I{type}://I{name} where I{type} is resource type (file
        or service) and I{name} is resource's name.

        @rtype: string
        """

        return self._get_field("resource")

    def show(self, indent = 0):
        """
        Prints this action's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, self.type, self.resource)


class Handler(JsonWrapper):
    """
    An application handler. A handler defines actions to execute when one of its
    associated triggers is "pulled". A trigger is generally the key of a setting.
    When the value of a setting changes and its key is in the list of triggers
    associated to a handler, then this handler's actions are executed. There
    are also 2 reserved triggers: _install and _uninstall which are respectively
    pulled when installing and uninstalling the application associated to this
    handler.

    @see: L{Application}
    """

    @property
    def actions(self):
        """
        The actions associated to this handler.

        @rtype: list of L{Action}
        """

        return self._get_list_field("do", lambda x: Action(x))

    @actions.setter
    def actions(self, actions):
        """
        Sets the actions associated to this handler.

        @param actions: A list of actions
        @type actions: list of L{Action}
        """

        self._set_list_field("do", actions)

    def add_action(self, action):
        """
        Adds an action to this handler's list.

        @param action: An action
        @type action: L{Action}
        """

        self._add_to_list_field("do", action)

    @property
    def triggers(self):
        """
        The triggers associated to this handler.

        @rtype: list of string
        """

        return self._get_list_field("on")

    @triggers.setter
    def triggers(self, triggers):
        """
        Sets the triggers associated to this handler.

        @param triggers: A list of triggers
        @type triggers: list of string
        """

        self._set_list_field("on", triggers)

    def add_trigger(self, trigger):
        """
        Adds a triggers to this handler's list.

        @param trigger: A trigger
        @type trigger: string
        """
        self._add_to_list_field("on", trigger)

    def show(self, indent = 0):
        """
        Prints this handler's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "Actions:")
        actions = self.actions
        for a in actions:
            a.show(indent + 2)
        print(" "*indent, "Triggers:")
        triggers = self.triggers
        for t in triggers:
            print(" "*(indent + 2), t)


class CustomAction(JsonWrapper):
    """
    A custom action's representation.
    """

    @property
    def identifier(self):
        """
        Custom action's identifier.

        @rtype: string
        """

        return self.key

    @property
    def key(self):
        """
        Custom action's key.

        @rtype: string
        """

        return self._get_field("key")

    @key.setter
    def key(self, key):
        """
        Sets custom action's key.

        @param key: The key
        @type key: string
        """

        self._set_field("key", key)

    @property
    def name(self):
        """
        Name of this custom action.

        @rtype: string
        """

        return self._get_field("name")

    @name.setter
    def name(self, name):
        """
        Sets the name of this custom action.

        @param name: Custom action's new name.
        @type name: string
        """

        self._set_field("name", name)

    @property
    def description(self):
        """
        The description of this custom action.

        @rtype: string
        """

        return self._get_field("description")

    @description.setter
    def description(self, description):
        """
        Sets the description of this custom action.

        @param description: The new description.
        @type description: string
        """

        self._set_field("description", description)

    def show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Key:", self.key)


class CompatibilityRule(JsonWrapper):
    @property
    def os_type(self):
        """
        An OS type (centos, fedora, debian, etc.).

        @rtype: string
        """

        return self._get_field("type")

    @os_type.setter
    def os_type(self, os_type):
        """
        Sets the OS type.

        @param os_type: The OS type.
        @type os_type: string
        """

        self._set_field("type", os_type)

    @property
    def version(self):
        """
        The OS version.

        @rtype: string
        """

        return self._get_field("version")

    @version.setter
    def version(self, version):
        """
        Sets the OS version.

        @param version: The new OS version.
        @type version: string
        """

        self._set_field("version", version)

    def show(self, indent = 0):
        """
        Prints this rule to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "OS type:", self.os_type)
        print(" "*indent, "OS version:", self.version)


class Application(HasParameters, IsStoreCapable):
    """
    Application entity representation. An application defines resources 
    of an operating system (files, users, etc.) as well as handlers which define
    a way to interact with these resources when some event occurs (like
    application install, a setting's value update, etc.)

    Parameters may be associated to an application: they define the settings that
    can be used to configure the application when installed on a host. The
    configuration of the application is then hold by an
    L{application context<contexts.ApplicationContext>}.

    An application entity owns 2 collections:
        - parameters (L{Parameter})
        - application files (L{ApplicationFile})
    """

    @property
    def packages(self):
        """
        The packages associated to this application.

        @rtype: list of L{Package}
        """

        return self._get_list_field("packages", lambda x: Package(x))

    @packages.setter
    def packages(self, packages):
        """
        Sets the packages associated to this application.

        @param packages: The new list of packages to associate to this application.
        @type packages: list of L{Package}
        """

        self._set_list_field("packages", packages)

    def add_package(self, package):
        """
        Adds a package to this application.

        @type package: L{Package}
        """

        self._add_to_list_field("packages", package)

    @property
    def groups(self):
        """
        The groups associated to this application.

        @rtype: list of L{Group}
        """

        return self._get_list_field("groups", lambda x: Group(x))

    @property
    def users(self):
        """
        The users associated to this application.

        @rtype: list of L{User}
        """

        return self._get_list_field("users", lambda x: User(x))

    @property
    def services(self):
        """
        The services associated to this application.

        @rtype: list of L{Service}
        """

        return self._get_list_field("services", lambda x: Service(x))

    @services.setter
    def services(self, services):
        """
        Sets the services associated to this application.

        @param services: The new list of services to associate to this application.
        @type services: list of L{Service}
        """

        self._set_list_field("services", services)

    def add_service(self, service):
        """
        Adds a service to this application.

        @param service: A service
        @type service: L{Service}
        """

        self._add_to_list_field("services", service)

    @property
    def files_f(self):
        """
        The files associated to this application. The entities returned in this
        list are "connected" to their collection, they can therefore be used to
        alter remote entities.

        @rtype: list of L{ApplicationFile}
        """

        return self._get_list_field("files", lambda x: ApplicationFile(self.files(), x))

    @files_f.setter
    def files_f(self, files):
        """
        Sets the files associated to this application. This field will only be
        taken into account on application creation. Afterwards, use application
        files collection instead (see L{files}).

        @param files: A list of files.
        @type files: list of L{ApplicationFile}
        """

        self._set_list_field("files", files)

    def add_file(self, app_file):
        """
        Adds a file to this application. This field will only be
        taken into account on application creation. Afterwards, use application
        files collection instead (see L{files}).

        @param app_file: A file.
        @type app_file: L{ApplicationFile}
        """
        self._add_to_list_field("files", app_file)

    def files(self):
        """
        Instantiates the collection of application files associated to the
        application.

        @rtype: L{ApplicationFileCollection}
        """

        return ApplicationFileCollection(self.client, self.url + "files/")

    def get_file(self, name):
        """
        Fetches a particular file from remote collection.
        
        @param name: The name of the file.
        @type name: string
        """

        return self.files().get(name)

    @property
    def actions(self):
        """
        The custom actions associated to this application.

        @rtype: list of L{CustomAction}
        """

        return self._get_list_field("actions", lambda x: CustomAction(x))

    @actions.setter
    def actions(self, actions):
        """
        Sets the actions associated to this application.

        @param packages: The new list of packages to associate to this application.
        @type packages: list of L{CustomAction}
        """

        self._set_list_field("actions", actions)

    def add_custom_action(self, action):
        """
        Adds a custom action to this application.

        @type package: L{CustomAction}
        """

        self._add_to_list_field("actions", action)

    @property
    def handlers(self):
        """
        The handlers associated to this application.

        @rtype: list of L{Handler}
        """

        return self._get_list_field("handlers", lambda x: Handler(x))

    @handlers.setter
    def handlers(self, handlers):
        """
        Sets the handlers associated to this application.

        @param handlers: The list of handlers
        @type handlers: list of L{Handler}
        """

        self._set_list_field("handlers", handlers)

    def add_handler(self, handler):
        """
        Adds a handler to this application.

        @param handler: A handler.
        @type handler: L{Handler}
        """

        self._add_to_list_field("handlers", handler)

    def clone(self, clone_name):
        """
        Requests the cloning of remote entity. Clone will have given name.
        This name should not already be in use.

        @param clone_name: The name of the clone.
        @type clone_name: string
        @return: The representation of application's clone.
        @rtype: L{Application}
        """

        try:
            result = self._http_client.update(self.url + "_clone", parameters = {"name": clone_name})
            return Application(self.collection, result)
        except ApiException as e:
            raise PythonApiException("Unable to clone application: " + e.message)

    @property
    def organization(self):
        """
        Name of the organization owning this application.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def repositories(self):
        """
        The repositories associated to this application.

        @rtype: list of L{Repository}
        """

        return self._get_list_field("repositories", lambda x: Repository(x))

    @repositories.setter
    def repositories(self, repositories):
        """
        Sets the repositories associated to this application.

        @param repositories: The new list of repositories to associate to this application.
        @type repositories: list of L{Repository}
        """

        self._set_list_field("repositories", repositories)

    def add_repository(self, repo):
        """
        Adds a repository to this application.

        @param repo: A repository
        @type repo: L{Repository}
        """

        self._add_to_list_field("repositories", repo)

    @property
    def compatibility(self):
        """
        The compatibility rules associated to this application.

        @rtype: list of L{CompatibilityRule}
        """

        return self._get_list_field("compatibility", lambda x: CompatibilityRule(x))

    @compatibility.setter
    def compatibility(self, compatibility):
        """
        Sets the compatibility rules associated to this application.

        @param compatibility: The new list of compatibility rules to associate to this application.
        @type compatibility: list of L{CompatibilityRule}
        """

        self._set_list_field("compatibility", compatibility)

    def add_compatibility_rule(self, rule):
        """
        Adds a compatibility rule to this application.

        @type package: L{CompatibilityRule}
        """

        self._add_to_list_field("compatibility", rule)
        
    def show_action(self, key):
        """
        Show custom action and handler for the given key

        @param key: key of the custom action
        """
        for c in self.actions:
            if c.key == key:
                c.show(2)
        for h in self.handlers:
            if any(key in s for s in h.triggers):
                h.show(4)

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)

        self._show_parameters(indent)

        print(" "*indent, "Compatibility rules:")
        rules = self.compatibility
        for r in rules:
            r.show(indent + 2)
        print(" "*indent, "Packages:")
        packages = self.packages
        for p in packages:
            p.show(indent + 2)
        print(" "*indent, "Services:")
        services = self.services
        for s in services:
            s.show(indent + 2)
        print(" "*indent, "Files:")
        files = self.files_f
        for f in files:
            f._show(indent + 2)
        print(" "*indent, "Groups:")
        groups = self.groups
        for g in groups:
            g.show(indent + 2)
        print(" "*indent, "Users:")
        users = self.users
        for u in users:
            u.show(indent + 2)
        print(" "*indent, "Repositories:")
        repos = self.repositories
        for r in repos:
            r.show(indent + 2)
        print(" "*indent, "Custom actions:")
        actions = self.actions
        for c in actions:
            c.show(indent + 2)
        print(" "*indent, "Handlers:")
        handlers = self.handlers
        for f in handlers:
            f.show(indent + 2)

        self._show_store_fields(indent)
