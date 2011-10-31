# coding: utf-8
"""
Application module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from cortex_client.util.json_wrapper import JsonWrapper, StringFactory
from resource import Resource

class ApplicationResource(JsonWrapper):
    """
    Base resource associated to an application.
    @see: L{Application}
    """

    def __init__(self, json_data = None):
        """
        Sets the state of a new instance of ApplicationResource with
        given state.
        
        @param json_data: A quasi-JSON representation of object's state
        @type json_data: dict
        """
        super(ApplicationResource, self).__init__(json_data)

    def get_name(self):
        """
        Provides the name of the resource
        
        @return: The name of the resource
        @rtype: String
        """
        return self._get_field("name")

    def set_name(self, name):
        """
        Sets the name of the resource

        @param name: The new name of the resource
        @type name: String
        """
        return self._set_field("name", name)

    def show(self, indent = 0):
        """
        Prints this resource.

        @param indent: The number of white spaces inserted before each printed
        line
        @type indent: Integer
        """
        print " "*indent, self.get_name()


class Package(ApplicationResource):
    """
    Application's package resource.
    @see: L{Application}
    """
    pass


class PackageFactory(object):
    """
    Application's package factory.
    
    @see: L{Package}
    @see: L{cortex_client.util.json_wrapper.JsonWrapper._get_list_field}
    """
    def new_object(self, json_data):
        """
        Instantiates a Package object using given state.
        
        @param json_data: A quasi-JSON representation of a Package instance's state.
        @type json_data: String, dict or list
        
        @return: A package object
        @rtype: L{Package}
        """
        return Package(json_data)


class Service(ApplicationResource):
    """
    Application's service resource.
    @see: L{Application}
    """

    def is_enabled(self):
        """
        Indicates if the service should be enabled at boot time.

        @return: True if the service is enabled at boot time.
        @rtype: Boolean
        """
        return self._get_field("enabled") != "false"

    def show(self, indent = 0):
        """
        Prints the state of this object to standard output in a user-friendly
        way.

        @param indent: The number of spaces to insert at begining of each
        printed line
        @type indent: Integer
        """
        print " "*indent, self.get_name() + ":"
        print " "*(indent + 2), "enabled:", self.is_enabled()


class ServiceFactory(object):
    """
    Application's service factory.
    
    @see: L{Service}
    @see: L{cortex_client.util.json_wrapper.JsonWrapper._get_list_field}
    """
    def new_object(self, json_data):
        """
        Instantiates a Service object using given state.
        
        @param json_data: A quasi-JSON representation of a Package instance's state.
        @type json_data: String, dict or list
        
        @return: A service object
        @rtype: L{Service}
        """
        return Service(json_data)


class ApplicationFile(ApplicationResource):
    """
    Application's file resource.
    
    @see: L{Application}
    """

    def get_owner(self):
        """
        Provides file's owner name.
        @return: An owner name
        @rtype: String
        """
        return self._get_field("owner")

    def get_group(self):
        """
        Provides file's group name.
        @return: A group name
        @rtype: String
        """
        return self._get_field("group")

    def get_mode(self):
        """
        Provides the permission string of this file. This string contains 3
        octal digits.
        @return: Permission string
        @rtype: String
        """
        return self._get_field("mode")

    def get_path(self):
        """
        Provides this file's path.
        @return: A path
        @rtype String
        """
        return self._get_field("path")

    def get_template_uuid(self):
        """
        Provides this file's template UUID.
        @return: A UUID
        @rtype: String
        """
        return self._get_field("template")

    def set_template_uuid(self, uuid):
        """
        Sets this file's template UUID.
        @param uuid: A UUID
        @type uuid: String
        """
        self._set_field("template", uuid)

    def show(self, indent = 0):
        """
        Prints the state of this object to standard output in a user-friendly
        way.

        @param indent: The number of spaces to insert at beginning of each
        printed line
        @type indent: Integer
        """
        print " "*indent, self.get_name() + ":"
        print " "*(indent + 2), "owner:", self.get_owner()
        print " "*(indent + 2), "group:", self.get_group()
        print " "*(indent + 2), "mode:", self.get_mode()
        print " "*(indent + 2), "path:", self.get_path()
        print " "*(indent + 2), "template:", self.get_template_uuid()


class ApplicationFileFactory(object):
    """
    Application's file factory.
    
    @see: L{Application}
    @see: L{cortex_client.util.json_wrapper.JsonWrapper._get_list_field}
    """
    def new_object(self, json_data):
        """
        Instantiates an ApplicationFile object using given state.
        
        @param json_data: A quasi-JSON representation of an ApplicationFile
        instance's state.
        @type json_data: String, dict or list
        
        @return: A file object
        @rtype: L{ApplicationFile}
        """
        return ApplicationFile(json_data)


class Action(JsonWrapper):
    """
    An action a handler may execute.
    @see: L{Handler}
    """
    def __init__(self, json_data):
        """
        @param json_data: A quasi-JSON representation of an Action.
        """
        super(Action, self).__init__(json_data)

    def get_type(self):
        """
        Provides action's type.
        @return: An action type (possible values: update, execute, restart,
        reload)
        @rtype: String
        """
        return self._get_field("action")

    def get_resource(self):
        """
        Provides the resource this action is applied on. This may be a service
        or a file.
        @return: A resource of the application. A file resource is given as
        file://<file name> and a service resource as service://<service name>
        @rtype: String
        """
        return self._get_field("resource")

    def show(self, indent = 0):
        """
        Prints the state of this object to standard output in a user-friendly
        way.

        @param indent: The number of spaces to insert at beginning of each
        printed line
        @type indent: Integer
        """
        print " "*indent, self.get_type(), self.get_resource()


class ActionFactory(object):
    """
    Application's action factory.
    
    @see: L{Action}
    @see: L{cortex_client.util.json_wrapper.JsonWrapper._get_list_field}
    """
    def new_object(self, json_data):
        """
        Instantiates an Action object using given state.
        
        @param json_data: A quasi-JSON representation of an Action
        instance's state.
        @type json_data: String, dict or list
        
        @return: An action object
        @rtype: L{Action}
        """
        return Action(json_data)


class Handler(JsonWrapper):
    """
    An application handler. A handler defines actions to execute given one or
    more triggers.
    @see: L{Action}
    """
    def __init__(self, json_data):
        """
        @param json_data: A quasi-JSON representation of an Action.
        """
        super(Handler, self).__init__(json_data)

    def get_actions(self):
        """
        Provides actions to perform.
        @return: A list of actions
        @rtype: list of L{Action}
        """
        return self._get_list_field("do", ActionFactory())

    def set_actions(self, actions):
        """
        Sets actions to perform.
        @param actions: A list of actions
        @type actions: list of L{Action}
        """
        self._set_list_field("do", actions)

    def add_action(self, action):
        """
        Adds an action for associated handler.
        @param action: An action
        @type action: L{Action}
        """
        self._add_to_list_field("do", action)

    def get_triggers(self):
        """
        Provides triggers for associated actions.
        @return: A list of actions
        @rtype: list of L{Action}
        """
        return self._get_list_field("on", StringFactory())

    def set_triggers(self, triggers):
        """
        Sets the triggers for associated actions.
        @param triggers: A list of actions
        @type triggers: list of String
        """
        self._set_list_field("on", triggers)

    def add_trigger(self, trigger):
        """
        Adds a triggers for associated actions.
        @param trigger: A trigger
        @type trigger: String
        """
        self._add_to_list_field("on", trigger)

    def show(self, indent = 0):
        """
        Prints the state of this object to standard output in a user-friendly
        way.

        @param indent: The number of spaces to insert at beginning of each
        printed line
        @type indent: Integer
        """
        print " "*indent, "Actions:"
        actions = self.get_actions()
        for a in actions:
            a.show(indent + 2)
        print " "*indent, "Triggers:"
        triggers = self.get_triggers()
        for t in triggers:
            print " "*(indent + 2), t


class HandlerFactory(object):
    """
    Application's handler factory.
    
    @see: L{Handler}
    @see: L{cortex_client.util.json_wrapper.JsonWrapper._get_list_field}
    """
    def new_object(self, json_data):
        """
        Instantiates a Handler object using given state.
        
        @param json_data: A quasi-JSON representation of an Action
        instance's state.
        @type json_data: String, dict or list
        
        @return: An action object
        @rtype: L{Action}
        """
        return Handler(json_data)


class Application(Resource):
    """
    An application. An application is defined by a list of associated packages,
    service and file resources as well as handlers. A handler defines one or more
    triggers for one or more actions to perform.
    """
    def __init__(self, api = None, json_data = None):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict, list or String
        """
        super(Application, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(Application, self).set_api(api)
        self._set_collection(api.get_application_collection())

    def get_packages(self):
        """
        Provides the packages associated to this application.
        @return: The list of packages
        @rtype: list of L{Package}
        """
        return self._get_list_field("packages", PackageFactory())

    def set_packages(self, packages):
        """
        Sets the packages associated to this application.
        @param packages: The list of packages
        @type packages: list of L{Package}
        """
        self._set_list_field("packages", packages)

    def add_package(self, package):
        """
        Adds a package associated to this application.
        @param package: The package
        @type package: L{Package}
        """
        self._add_to_list_field("packages", package)

    def get_services(self):
        """
        Provides the services associated to this application.
        @return: The list of services
        @rtype: list of L{Service}
        """
        return self._get_list_field("services", ServiceFactory())

    def set_services(self, services):
        """
        Sets the services associated to this application.
        @param services: The list of services
        @type services: list of L{Service}
        """
        self._set_list_field("services", services)

    def add_service(self, service):
        """
        Adds a service associated to this application.
        @param service: The service
        @type service: L{Service}
        """
        self._add_to_list_field("services", service)

    def get_files(self):
        """
        Provides the files associated to this application.
        @return: The list of files
        @rtype: list of L{ApplicationFile}
        """
        return self._get_list_field("files", ApplicationFileFactory())

    def set_files(self, files):
        """
        Sets the files associated to this application.
        @param files: The list of files
        @type files: list of L{ApplicationFile}
        """
        self._set_list_field("files", files)

    def add_file(self, app_file):
        """
        Adds a file associated to this application.
        @param app_file: The file
        @type app_file: L{ApplicationFile}
        """
        self._add_to_list_field("files", app_file)

    def get_handlers(self):
        """
        Provides the handlers associated to this application.
        @return: The list of handlers
        @rtype: list of L{Handler}
        """
        return self._get_list_field("handlers", HandlerFactory())

    def set_handlers(self, handlers):
        """
        Sets the handlers associated to this application.
        @param handlers: The list of handlers
        @type handlers: list of L{Handler}
        """
        self._set_list_field("handlers", handlers)

    def add_handler(self, handler):
        """
        Adds a handler associated to this application.
        @param handler: The handler
        @type handler: L{Handler}
        """
        self._add_to_list_field("handlers", handler)

    def get_version(self):
        """
        Provides the version of the application.
        @return: The version
        @rtype: Integer
        """
        return int(self._get_field("version"))

    def _show(self, indent = 0):
        """
        Prints the state of this object to standard output in a user-friendly
        way.

        @param indent: The number of spaces to insert at beginning of each
        printed line
        @type indent: Integer
        """
        print " "*indent, "UUID:", self.get_uuid()
        print " "*indent, "Name:", self.get_name()
        print " "*indent, "Description:", self.get_description()
        print " "*indent, "Packages:"
        packages = self.get_packages()
        for p in packages:
            p.show(indent + 2)
        print " "*indent, "Services:"
        services = self.get_services()
        for s in services:
            s.show(indent + 2)
        print " "*indent, "Files:"
        files = self.get_files()
        for f in files:
            f.show(indent + 2)
        print " "*indent, "Handlers:"
        handlers = self.get_handlers()
        for f in handlers:
            f.show(indent + 2)
