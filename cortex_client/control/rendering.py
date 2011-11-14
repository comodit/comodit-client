import os, pwd, grp

from cortex_client.util import globals, path

from cortex_client.control.abstract import AbstractController
from cortex_client.control.exceptions import MissingException, ControllerException

class RenderingController(AbstractController):
    def __init__(self):
        super(RenderingController, self).__init__()
        self._register(["af", "app-file"], self._app_file)
        self._register(["ks", "kickstart"], self._kickstart)
        self._register(["t", "tree"], self._tree)
        self._default_action = self._help

    def _app_file(self, argv):
        if len(argv) != 3:
            raise MissingException("This action takes 3 arguments")

        file_name = argv[0]
        app_name = argv[1]
        host_id = argv[2] # UUID or path

        options = globals.options
        if options.uuid:
            host_uuid = host_id
        else:
            host_uuid = self._api.get_directory().get_host_uuid_from_path(host_id)

        host = self._api.get_host_collection().get_resource(host_uuid)
        app_found = False
        for app_uuid in host.get_applications():
            app = self._api.get_application_collection().get_resource(app_uuid)
            if(app.get_name() == app_name):
                app_found = True
                break

        if not app_found:
            raise ControllerException("Application is not installed on host")

        print self._api.get_rendering_service().get_rendered_file(host_uuid, app_name, file_name).read()

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
        for app_uuid in apps:
            app = self._api.get_application_collection().get_resource(app_uuid)

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
    app-file <file name> <application> <host uuid or path>
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
