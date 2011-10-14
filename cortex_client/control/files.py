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
from cortex_client.control.abstract import AbstractController
from cortex_client.util import globals, prompt, fileupload
from cortex_client.rest.client import Client
from cortex_client.control.exceptions import NotFoundException, MissingException
from cortex_client.util.editor import edit_text

import urlparse

class FilesController(AbstractController):

    _resource = "files"
    _template = "file.json"
    _parameters = {}

    def __init__(self):
        super(FilesController, self).__init__()
        self._register(["l", "list"], self._list)
        self._register(["s", "show"], self._show)
        self._register(["r", "read"], self._read)
        self._register(["u", "update"], self._update)
        self._register(["a", "add"], self._add)
        self._register(["w", "write"], self._write)
        self._register(["d", "delete"], self._delete)
        self._register(["h", "help"], self._help)
        self._default_action = self._help

    def _list(self, argv):
        options = globals.options
        client = Client(self._endpoint(), options.username, options.password)
        result = client.read(self._resource, parameters=self._parameters)

        if options.raw:
            print json.dumps(result, sort_keys=True, indent=4)
        else:
            if (result['count'] == "0"):
                print "Request returned 0 object."
            else:
                for o in result['items']:
                    self._render(o)

    def _read(self, argv):
        options = globals.options

        # Require an object as argument
        if len(argv) == 0:
            raise MissingException("You must provide a valid object identifier")

        # Validate input parameters
        uuid = argv[0]

        # Query the server
        client = Client(self._endpoint(), options.username, options.password)
        result = client.read(self._resource + "/" + uuid, decode=False)

        # Display the result
        for line in result:
                print line,

    def _show(self, argv):
        options = globals.options

        # Require an object as argument
        if len(argv) == 0:
            raise MissingException("You must provide a valid object identifier")

        # Validate input parameters
        uuid = argv[0]

        # Query the server
        client = Client(self._endpoint(), options.username, options.password)
        result = client.read(self._resource + "/" + uuid + "/_meta")

        # Display the result
        if options.raw:
            print json.dumps(result, sort_keys=True, indent=4)
        else:
            self._render(result, detailed=True)

    def _update(self, argv):
        options = globals.options
        self._parameters = {}

        client = Client(self._endpoint(), options.username, options.password)

        if options.filename:
            with open(options.filename, 'r') as f:
                item = json.load(f)
                uuid = item.get("uuid")
        elif options.json:
            item = json.loads(options.json)
            uuid = item.get("uuid")
        elif len(argv) > 0:
            # Get the uuid/path from the command line
            uuid = argv[0]
            # Find the resource
            item = client.read(self._resource + "/" + uuid + "/_meta")
            if not item: raise NotFoundException(uuid)
            # Edit the resouce
            original = json.dumps(item, sort_keys=True, indent=4)
            #original = "# To abort the request; just exit your editor without saving this file.\n\n" + original
            updated = edit_text(original)
            #updated = re.sub(r'#.*$', "", updated)
            item = json.loads(updated)

        if options.force: self._parameters["force"] = "true"

        result = client.update(self._resource + "/" + uuid + "/_meta", item, self._parameters)

        if options.raw:
            print json.dumps(result, sort_keys=True, indent=4)
        else:
            self._render(result)

    def _add(self, argv):
        options = globals.options

        if options.filename:
            with open(options.filename, 'r') as f:
                item = json.load(f)
        elif options.json:
            item = json.loads(options.json)
        else :
            template = open(os.path.join(Config().templates_path, self._template)).read()
            #template = "# To abort the request; just exit your editor without saving this file.\n\n" + template
            updated = edit_text(template)
            #updated = re.sub(r'#.*$', "", updated)
            item = json.loads(updated)

        template_file_name = item["name"]
        with open(template_file_name, 'r') as f:
            url = urlparse.urlparse(self._endpoint() + "/" + self._resource)
            response = fileupload.post_multipart(url.netloc, url.path,
                                                 [("test", "none")],
                                                 [("file", template_file_name, f.read())],
                                                 {"Authorization": "Basic " + (options.username + ":" + options.password).encode("base64").rstrip()})

        uuid = json.loads(response)[0];

        if options.force: self._parameters["force"] = "true"

        client = Client(self._endpoint(), options.username, options.password)
        result = client.update(self._resource + "/" + uuid + "/_meta", item, self._parameters)

        if options.raw:
            print json.dumps(result, sort_keys=True, indent=4)
        else:
            self._render(result)

    def _write(self, argv):
        options = globals.options

        if len(argv) == 0:
            raise MissingException("You must provide a valid object identifier")
        uuid = argv[0]

        if not options.filename:
            raise MissingException("You must provide a file to upload (--file)")

        with open(options.filename, 'r') as f:
            url = urlparse.urlparse(self._endpoint() + "/" + self._resource + "/" + uuid)
            response = fileupload.post_multipart(url.netloc, url.path, [("test", "none")], [("file", options.filename, f.read())], {"Authorization": "Basic " + (options.username + ":" + options.password).encode("base64").rstrip()})

        result = json.loads(response);

        if options.raw:
            print json.dumps(result, sort_keys=True, indent=4)
        else:
            if (len(result) == "0"):
                print "Request returned 0 object."
            else:
                for o in result:
                    print o

    def _delete(self, argv):
        options = globals.options

        # Require an object as argument
        if len(argv) == 0:
            raise MissingException("You must provide a valid object identifier")

        # Validate input parameters
        uuid = argv[0]

        client = Client(self._endpoint(), options.username, options.password)
        item = client.read(self._resource + "/" + uuid + "/_meta")

        if (prompt.confirm(prompt="Delete " + item['name'] + " ?", resp=False)) :
            client.delete(self._resource + "/" + uuid)

    def _render(self, item, detailed=False):
        if not detailed:
            print item['uuid'], item['name']
        else:
            print "Name:", item['name']
            print "UUID:", item['uuid']
            if(item.has_key("parameters")):
                print "Parameters:",
                parameters = item['parameters']
                for p in parameters:
                    print p["key"],
                print


    def _resolv(self, path):
        pass

    def _endpoint(self):
        options = globals.options
        return options.api

    def _help(self, argv):
        print '''You must provide an action to perfom.

Actions:
    list            List all files available to the user
    show <uuid>     Show the details of a file
    add             Create a new file (see below for more details)
    update <uuid>   Update the details of a file
    delete <uuid>   Delete a file
    read <uuid>     Fetch the content of a file
    write <uuid>    Update the content of a file (content is read from file
                    whose name must be provided through --file option)

A file is completely described by its details and its content. Details include a
file name as well as a list of parameters. When creating a new file (add),
details must be provided (through --file, --json or interactively), the content
is read from file whose name is given in the details.
'''
