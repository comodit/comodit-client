from cortex_client.util.json_wrapper import JsonWrapper, StringFactory
from resource import Resource

class ApplicationResource(JsonWrapper):
    def __init__(self, json_data = None):
        super(ApplicationResource, self).__init__(json_data)

    def get_name(self):
        return self._get_field("name")

    def set_name(self, name):
        return self._set_field("name", name)

    def show(self, indent = 0):
        print " "*indent, self.get_name()


class Package(ApplicationResource):
    pass


class PackageFactory(object):
    def new_object(self, json_data):
        return Package(json_data)


class Service(ApplicationResource):
    def get_running(self):
        return self._get_field("running")

    def get_enabled(self):
        return self._get_field("enabled")

    def show(self, indent = 0):
        print " "*indent, self.get_name()+":"
        print " "*(indent+2), "enabled:", self.get_enabled()
        print " "*(indent+2), "running", self.get_running()


class ServiceFactory(object):
    def new_object(self, json_data):
        return Service(json_data)


class ApplicationFile(ApplicationResource):
    def get_owner(self):
        return self._get_field("owner")

    def get_group(self):
        return self._get_field("group")

    def get_mode(self):
        return int(self._get_field("mode"), 8)

    def get_path(self):
        return self._get_field("path")

    def get_template_uuid(self):
        return self._get_field("template")

    def set_template_uuid(self, uuid):
        self._set_field("template", uuid)

    def show(self, indent = 0):
        print " "*indent, self.get_name()+":"
        print " "*(indent+2), "owner:", self.get_owner()
        print " "*(indent+2), "group:", self.get_group()
        print " "*(indent+2), "mode:", self.get_mode()
        print " "*(indent+2), "path:", self.get_path()
        print " "*(indent+2), "template:", self.get_template_uuid()


class ApplicationFileFactory(object):
    def new_object(self, json_data):
        return ApplicationFile(json_data)


class Action(JsonWrapper):
    def __init__(self, json_data):
        super(Action, self).__init__(json_data)

    def get_type(self):
        return self._get_field("action")

    def get_resource(self):
        return self._get_field("resource")

    def show(self, indent = 0):
        print " "*indent, self.get_type(), self.get_resource()


class ActionFactory(object):
    def new_object(self, json_data):
        return Action(json_data)


class Handler(JsonWrapper):
    def __init__(self, json_data):
        super(Handler, self).__init__(json_data)

    def get_actions(self):
        return self._get_list_field("do", ActionFactory())

    def set_actions(self, actions):
        self._set_list_field("do", actions)

    def get_triggers(self):
        return self._get_list_field("on", StringFactory())

    def set_triggers(self, triggers):
        self._set_list_field("on", triggers)

    def show(self, indent = 0):
        print " "*indent, "Actions:"
        actions = self.get_actions()
        for a in actions:
            a.show(indent + 2)
        print " "*indent, "Triggers:"
        triggers = self.get_triggers()
        for t in triggers:
            print " "*(indent + 2), t


class HandlerFactory(object):
    def new_object(self, json_data):
        return Handler(json_data)


class Application(Resource):
    def __init__(self, api = None, json_data = None):
        super(Application, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(Application, self).set_api(api)
        self._set_collection(api.get_application_collection())

    def get_packages(self):
        return self._get_list_field("packages", PackageFactory())

    def set_packages(self, packages):
        self._set_list_field("packages", packages)

    def add_package(self, package):
        self._add_to_list_field("packages", package)

    def get_services(self):
        return self._get_list_field("services", ServiceFactory())

    def set_services(self, services):
        self._set_list_field("services", services)

    def get_files(self):
        return self._get_list_field("files", ApplicationFileFactory())

    def set_files(self, files):
        self._set_list_field("files", files)

    def get_handlers(self):
        return self._get_list_field("handlers", HandlerFactory())

    def set_handlers(self, handlers):
        self._set_list_field("handlers", handlers)

    def get_version(self):
        return self._get_field("version")

    def _show(self, indent = 0):
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