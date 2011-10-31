# control.resource - Generic controller for managing cortex resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import json, os

from cortex_client.config import Config
from cortex_client.util.editor import edit_text
from cortex_client.util import globals
from cortex_client.control.resource import ResourceController
from cortex_client.control.exceptions import MissingException, ArgumentException

class FilesController(ResourceController):

    _template = "file.json"

    def __init__(self):
        super(FilesController, self).__init__()
        self._register(["r", "read"], self._read)
        self._register(["w", "write"], self._write)
        self._default_action = self._help

    def get_collection(self):
        return self._api.get_file_collection()

    def _add(self, argv):
        if(len(argv) == 0):
            raise MissingException("You must provide a file to upload")

        content_file_name = argv[0]

        if(not os.path.exists(content_file_name)):
            raise ArgumentException("Given file does not exist: " + content_file_name)

        options = globals.options
        if options.filename:
            with open(options.filename, 'r') as f:
                item = json.load(f)
                res = self.get_collection()._new_resource(item)
        elif options.json:
            item = json.loads(options.json)
            res = self.get_collection()._new_resource(item)
        else :
            template = open(os.path.join(Config().templates_path, self._template)).read()
            #template = "# To abort the request; just exit your editor without saving this file.\n\n" + template
            updated = edit_text(template)
            #updated = re.sub(r'#.*$', "", updated)
            res = self.get_collection()._new_resource(json.loads(updated))

        res.set_content(content_file_name)
        res.create()
        res.show(as_json = options.raw)

    def _read(self, argv):
        file_res = self._get_resource(argv)

        file_content = file_res.get_content()

        for line in file_content:
            print line,
        print "-"*80

    def _write(self, argv):
        options = globals.options
        if not options.filename:
            raise MissingException("You must provide a file to upload")

        content_file_name = options.filename

        if(not os.path.exists(content_file_name)):
            raise ArgumentException("Given file does not exist: " + content_file_name)

        file_res = self._get_resource(argv)

        file_res.set_content(content_file_name)
        file_res.commit()

    def _help(self, argv):
        print '''You must provide an action to perform.

Actions:
    list                       List all files available to the user
    show <uuid>                Show the details of a file
    add  <path>                Create a new file
    update <uuid>              Update the details of a file
    delete <uuid>              Delete a file
    read <uuid>                Fetch the content of a file
    write <uuid> --file <path> Update an existing file's content

A file is completely described by its details and its content. Details include a
file name as well as a list of parameters. When creating a new file (add),
details must be provided (through --file, --json or interactively), the content
is read from the file pointed by given path.
'''
