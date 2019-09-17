from builtins import object
from collections import OrderedDict
import json
import sys

from comodit_client.util.editor import edit_text


class JsonUpdater(object):

    def __init__(self, options, ignore_not_modified=False):
        self._options = options
        self._ignore_not_modified = ignore_not_modified

    def update(self, json_data):
        if self._options.filename:
            with open(self._options.filename, 'r') as f:
                return json.load(f, object_pairs_hook=OrderedDict)
        elif self._options.json:
            return json.loads(self._options.json, object_pairs_hook=OrderedDict)
        elif self._options.stdin:
            return json.load(sys.stdin, object_pairs_hook=OrderedDict)
        else:
            original = json_data.get_real_json(indent = 4)
            updated = edit_text(original, ignore_not_modified=self._ignore_not_modified)
            return json.loads(updated, object_pairs_hook=OrderedDict)
