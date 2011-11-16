import os, pwd, grp

from cortex_client.util import globals, path

from cortex_client.control.abstract import AbstractController
from cortex_client.control.exceptions import MissingException, ControllerException

class RenderingController(AbstractController):
    def __init__(self):
        super(RenderingController, self).__init__()
        self._register(["app-file"], self._app_file, self._print_app_file_completions)
        self._register(["kickstart"], self._kickstart, self._print_kickstart_completions)
        self._register(["tree"], self._tree, self._print_tree_completions)
        self._register(["help"], self._help)
        self._default_action = self._help

    def _print_hosts(self, argv):
        resources_list = self._api.get_host_collection().get_resources()

        if len(argv) > 0:
            # Check if completions are available
            id = argv[0]
            for res in resources_list:
                if id == res.get_identifier():
                    return

        for r in resources_list:
            print r.get_identifier()

    def _get_host(self, id):
        if(globals.options.uuid):
            return self._api.get_host_collection().get_resource(id)
        else:
            return self._api.get_host_collection().get_resource_from_path(id)

    def _print_applications(self, argv):
        host = self._get_host(argv[0])

        app_list = host.get_applications()
        if len(argv) > 1:
            # Check if completions are available
            app = argv[1]
            for res in app_list:
                if app == res.get_identifier():
                    return

        for r in app_list:
            print r.get_identifier()

    def _get_application(self, host_id, app_name):
        host = self._get_host(host_id)
        app_list = host.get_applications()
        the_app = None
        for app in app_list:
            if app.get_name() == app_name:
                the_app = app
                break
        return the_app

    def _print_files(self, argv):
        app = self._get_application(argv[0], argv[1])

        file_list = app.get_files()
        if len(argv) > 2:
            # Check if completions are available
            file_name = argv[2]
            for f in file_list:
                if file_name == f.get_name():
                    return

        for r in file_list:
            print r.get_name()

    def _print_app_file_completions(self, param_num, argv):
        if param_num == 0:
            self._print_hosts(argv)
        elif param_num == 1:
            self._print_applications(argv)
        elif param_num == 2:
            self._print_files(argv)

    def _app_file(self, argv):
        if len(argv) != 3:
            raise MissingException("This action takes 3 arguments")

        host_id = argv[0] # UUID or path
        app_name = argv[1]
        file_name = argv[2]

        options = globals.options
        if options.uuid:
            host_uuid = host_id
        else:
            host_uuid = self._api.get_directory().get_host_uuid_from_path(host_id)

        host = self._api.get_host_collection().get_resource(host_uuid)
        app_found = False
        for app in host.get_applications():
            if(app.get_name() == app_name):
                app_found = True
                break

        if not app_found:
            raise ControllerException("Application is not installed on host")

        print self._api.get_rendering_service().get_rendered_file(host_uuid, app_name, file_name).read()

    def _print_kickstart_completions(self, param_num, argv):
        if param_num == 0:
            self._print_hosts(argv)

    def _kickstart(self, argv):
        if len(argv) != 1:
            raise MissingException("This action takes 1 argument")

        host_id = argv[0] # UUID or path

        options = globals.options
        if options.uuid:
            host_uuid = host_id
        else:
            host_uuid = self._api.get_directory().get_host_uuid_from_path(host_id)

        print self._api.get_rendering_service().get_rendered_kickstart(host_uuid).read()

    def _print_tree_completions(self, param_num, argv):
        if param_num == 0:
            self._print_hosts(argv)
        elif param_num == 1:
            exit(2) # Request folder completion

    def _tree(self, argv):
        if len(argv) != 2:
            raise MissingException("This action takes 2 argument")

        host_id = argv[0] # UUID or path
        root_dir = argv[1]

        path.ensure(root_dir)

        options = globals.options
        if options.uuid:
            host_uuid = host_id
        else:
            host_uuid = self._api.get_directory().get_host_uuid_from_path(host_id)
        host = self._api.get_host_collection().get_resource(host_uuid)

        apps = host.get_applications()
        rendering = self._api.get_rendering_service()
        for app in apps:
            # Render files of app
            app_files = app.get_files()
            for f in app_files:
                file_path = f.get_path()
                if file_path[0] == '/':
                    rel_path = file_path[1:] # remove heading "/"
                else:
                    rel_path = file_path

                # Output rendered file
                (dir_path, file_name) = os.path.split(rel_path)
                output_dir = os.path.join(root_dir, dir_path)
                path.ensure(output_dir)
                output_file = os.path.join(output_dir, file_name)

                content = rendering.get_rendered_file(host_uuid, app.get_name(),
                                                      f.get_name())
                with open(output_file, "w") as fd:
                    fd.write(content.read())

                # Set permissions
                mode = int(f.get_mode(), 8)
                owner = f.get_owner()
                owner_id = pwd.getpwnam(owner)[2]
                group = f.get_group()
                group_id = grp.getgrnam(group)[2]

                if not options.skip_chmod:
                    try:
                        os.chmod(output_file, mode)
                    except OSError, e:
                        raise ControllerException("Could not set permissions on file " + output_file + ": " + e.strerror)

                if not options.skip_chown:
                    try:
                        os.chown(output_file, owner_id, group_id)
                    except OSError, e:
                        raise ControllerException("Could not set ownership on file " + output_file + ": " + e.strerror)

    def _help(self, argv):
        print '''You must provide an action to perform.

Actions:
    app-file <host uuid or path> <application name> <file name>
                    Prints a rendered file.
    kickstart <host uuid or path>
                    Prints a rendered kickstart.
    tree <host uuid or path> <output directory> [--skip-chown] [--skip-chmod]
                    Outputs all files associated to a particular host to a
                    given directory. Note that if a file c has path /a/b/c and
                    output directory's path is /d/e/, the file will be written
                    to /d/e/a/b/c. File c will have proper permissions and
                    ownership unless it is asked not to do so (--skip-chown
                    and --skip-chmod flags).
'''
