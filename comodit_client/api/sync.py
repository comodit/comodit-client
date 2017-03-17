# coding: utf-8
"""
Provides synchronization tool (L{SyncEngine}). It allows to synchronize local entities stored
on local disk (see L{exporter}) with remote entities i.e. updates made locally
can be I{pushed} remotely (uploaded to the server) and remote changes may be
I{pulled} locally (downloaded from the server).
"""

import os, json, types

from comodit_client.api.collection import EntityNotFoundException
from collections import OrderedDict


class SyncException(Exception):
    """
    Exception raised by synchronizer in case of error.
    """

    pass


class Diff(object):
    """
    Represents a diff between 2 entities' elements.
    """

    def __init__(self, diff_type, key = None, old_value = None, new_value = None):
        """
        Creates a diff instance. A diff represents a difference between
        two entities. There are 7 difference types (called diff types):
          - create: a new field must be added
          - update: an existing field must be updated
          - delete: an existing field must be deleted
          - set-file-content: A file's content must be set/overwritten
          - delete-file-content: A file's content must be cleared
          - set-thumb: A thumbnail must be set
          - delete-thumb: A thumbnail must be removed

        @param diff_type: The diff type.
        @type diff_type: string
        @param key: Diff's type (field name, file name, etc.)
        @type key: string
        @param old_value: Old field value.
        @type old_value: JSON object
        @param new_value: New field value.
        @type new_value: JSON object
        """

        self.type = diff_type
        self.key = key
        self.old_value = old_value
        self.new_value = new_value


class FileProvider(object):
    """
    Base class providing an "interface" for file access facilities.
    """

    def exists(self, name):
        """
        Checks if a file exists.

        @param name: File's name.
        @type name: string
        @return: True if the file exists, false otherwise.
        @rtype: bool
        """

        raise NotImplementedError()

    def thumb_exists(self):
        """
        Checks if a thumbnail exists.

        @return: True if the thumbnail exists, false otherwise.
        @rtype: bool
        """

        raise NotImplementedError()

    def open(self, name):
        """
        Opens an existing file.

        @param name: File's name.
        @type name: string
        @return: A readable file i.e. an object implementing a file object's
        C{read} method.
        @rtype: file-like object
        """

        raise NotImplementedError()

    def open_thumb(self):
        """
        Opens an existing thumbnail.

        @return: A readable file i.e. an object implementing a file object's
        C{read} method.
        @rtype: file-like object
        """

        raise NotImplementedError()

    def close(self, fd):
        """
        Closes given file-like object obtained through L{open} or L{open_thumb}.

        @param fd: a file-like object.
        @type fd: file-like object
        """

        raise NotImplementedError()


class LocalFileProvider(FileProvider):
    """
    Helper class providing local file access facilities.
    """

    def __init__(self, folder):
        """
        Creates a new local file provider.

        @param folder: Path to local directory.
        @type folder: string
        """

        self._folder = folder

    def exists(self, name):
        return os.path.exists(os.path.join(self._folder, "files", name))

    def thumb_exists(self):
        return os.path.exists(os.path.join(self._folder, "thumb"))

    def open(self, name):
        return open(os.path.join(self._folder, "files", name), "r")

    def open_thumb(self):
        return open(os.path.join(self._folder, "thumb"), "r")

    def close(self, fd):
        fd.close()


class RemoteFileProvider(FileProvider):
    """
    Helper class providing remote file access facilities.
    """

    def __init__(self, remote_res):
        """
        Creates a new remote file provider.

        @param remote_res: Remote entity owning files.
        @type remote_res: L{HasFiles}
        """

        self._remote_res = remote_res

    def exists(self, name):
        try:
            self._remote_res.get_file(name).get_content()
            return True
        except EntityNotFoundException:
            return False

    def thumb_exists(self):
        try:
            self._remote_res.get_thumbnail_content()
            return True
        except EntityNotFoundException:
            return False

    def open(self, name):
        return self._remote_res.get_file(name).get_content()

    def open_thumb(self):
        return self._remote_res.get_thumbnail_content()

    def close(self, fd):
        pass


class SyncEngine(object):
    """
    Synchronization tool allowing to sync local and remote entities. Synchronization
    is not bidirectional, you must choose either to update a remote entity
    using a local entity as reference, either to update a local entity using
    a remote entity as reference. First case is called I{push}, second case
    is called I{pull}.

    Local entities must be organized in the same way as L{Import} tool generates.

    Pushes and pulls may be "dry-runned" allowing to audit changes before
    actually applying them.
    """

    def __init__(self, folder_path):
        """
        Creates a new sync engine.

        @param folder_path: Path to local entity's directory.
        @type folder_path: string
        """

        if not os.path.exists(folder_path):
            raise SyncException("Provided folder does not exist")

        self._folder_path = folder_path
        self._files_folder_path = os.path.join(self._folder_path, "files")
        self._deffile_path = os.path.join(folder_path, "definition.json")
        if not os.path.exists(self._deffile_path):
            raise SyncException("Provided folder does not contain an entity definition")

        self.__push_ignored_fields = ["organization", "price", "version", "canPull", "canPush", "uuid", "publishedAs", "purchasedAs"]
        self.__pull_ignored_fields = []

    def __is_ignore(self, key, is_pull):
        return (is_pull and (key in self.__pull_ignored_fields)) or (not is_pull and (key in self.__push_ignored_fields))

    def _is_same_content(self, reader1, reader2, file_name):
        exists1 = reader1.exists(file_name)
        exists2 = reader2.exists(file_name)

        if exists1 != exists2:
            return False
        elif not exists1:
            return True

        fd1 = reader1.open(file_name)
        fd2 = reader2.open(file_name)

        is_same_content = fd1.read() == fd2.read()

        reader1.close(fd1)
        reader2.close(fd2)
        return is_same_content

    def _is_same_thumb(self, reader1, reader2):
        exists1 = reader1.thumb_exists()
        exists2 = reader2.thumb_exists()

        if exists1 != exists2:
            return False
        elif not exists1:
            return True

        fd1 = reader1.open_thumb()
        fd2 = reader2.open_thumb()

        is_same_content = fd1.read() == fd2.read()

        reader1.close(fd1)
        reader2.close(fd2)
        return is_same_content

    def _diff(self, src_dict, dest_dict, is_pull, src_reader, dest_reader):
        diffs = []
        for key, dest_value in dest_dict.iteritems():
            if self.__is_ignore(key, is_pull):
                continue

            src_value = src_dict.get(key)
            if src_value is None:
                diffs.append(Diff("delete", key))
                if key == "files":
                    for f in src_value:
                        diffs.append(Diff("delete_file_content", f["name"]))
            elif dest_value != src_value:
                diffs.append(Diff("update", key, dest_value, src_value))
                if key == "files":
                    local_names = set()
                    for f in dest_value:
                        local_names.add(f["name"])
                    remote_names = set()
                    for f in src_value:
                        remote_names.add(f["name"])

                    to_delete = local_names - remote_names
                    for file_name in to_delete:
                        diffs.append(Diff("delete_file_content", file_name))
                    to_create = remote_names - local_names
                    for file_name in to_create:
                        diffs.append(Diff("set_file_content", file_name))
                    common_files = local_names & remote_names
                    for file_name in common_files:
                        if not self._is_same_content(src_reader, dest_reader, file_name):
                            if src_reader.exists(file_name):
                                diffs.append(Diff("set_file_content", file_name))
                            else:
                                diffs.append(Diff("delete_file_content", file_name))
            elif key == "files":
                for f in dest_value:
                    file_name = f["name"]
                    if not self._is_same_content(src_reader, dest_reader, file_name):
                        if src_reader.exists(file_name):
                            diffs.append(Diff("set_file_content", file_name))
                        else:
                            diffs.append(Diff("delete_file_content", file_name))

        for key, src_value in src_dict.iteritems():
            if self.__is_ignore(key, is_pull):
                continue
            dest_value = dest_dict.get(key)
            if dest_value is None:
                diffs.append(Diff("create", key, None, src_value))
                if key == "files":
                    for f in src_value:
                        diffs.append(Diff("set_file_content", f["name"]))

        # Thumbnails
        if not self._is_same_thumb(src_reader, dest_reader):
            if src_reader.thumb_exists():
                diffs.append(Diff("set_thumb"))
            else:
                diffs.append(Diff("delete_thumb"))

        return diffs

    def _print_dict_diff(self, level, new_dict, old_dict):
        did_output = False
        for key, old_value in old_dict.iteritems():
            new_value = new_dict.get(key)
            if new_value is None:
                print level * " " + "'" + key + "' will be removed"
                did_output = True
            elif old_value != new_value:
                if type(old_value) != type(new_value):
                    print level * " " + "Different types for key '", key + "'", type(old_value), "->", type(new_value)
                    did_output = True
                elif type(old_value) is types.DictType:
                    did_output = self._print_dict_diff(level + 2, new_value, old_value) or did_output
                elif type(old_value) is types.ListType:
                    did_output = self._print_list_diff(level + 2, new_value, old_value) or did_output
                else:
                    print level * " " + "Different values for key '" + key + "'", old_value, "->", new_value
                    did_output = True

        for key, new_value in new_dict.iteritems():
            old_value = old_dict.get(key)
            if old_value is None:
                print level * " " + "'" + key + "' will be added"
                did_output = True

        return did_output

    def _dictify(self, key, input_list):
        output_dict = {}
        for e in input_list:
            if not type(e) is types.DictType:
                return None
            if not e.has_key(key):
                return None
            if output_dict.has_key(key):
                return None
            output_dict[e[key]] = e
        return output_dict

    def _try_print_dictified_list(self, level, key_name, src_list, dest_list):
        src_dict = self._dictify(key_name, src_list)
        if src_dict is None:
            raise SyncException("Could not dictify source list")

        dest_dict = self._dictify(key_name, dest_list)
        if dest_dict is None:
            raise SyncException("Could not dictify destination list")

        return self._print_dict_diff(level, src_dict, dest_dict)

    def _print_list_diff(self, level, src_list, dest_list):
        for key_name in ("name", "id", "key"):
            try:
                if self._try_print_dictified_list(level, key_name, src_list, dest_list):
                    return True
                else:
                    print level * " " + "only elements order is different"
                    return False
            except SyncException:
                pass
        print level * " " + "different lists"
        return True

    def _print_diff(self, diffs):
        for d in diffs:
            if d.type == "delete":
                print "Deletion of field '" + d.key + "'"
            elif d.type == "create":
                print "Creation of field '" + d.key + "'"
            elif d.type == "update":
                if type(d.old_value) != type(d.new_value):
                    print "Conflicting types for field '", d.key + "':", type(d.old_value), "->", type(d.new_value)
                elif type(d.old_value) is types.DictType:
                    print "Conflicting values for dict field '" + d.key + "':"
                    self._print_dict_diff(2, d.new_value, d.old_value)
                elif type(d.old_value) is types.ListType:
                    print "Conflicting values for list field '" + d.key + "':"
                    self._print_list_diff(2, d.new_value, d.old_value)
                else:
                    print "Conflicting values for field '" + d.key + "':", d.old_value, "->", d.new_value
            elif d.type == "delete_file_content":
                print "Deletion of file '" + d.key + "' content"
            elif d.type == "set_file_content":
                print "Creation/update of file '" + d.key + "' content"
            elif d.type == "set_thumb":
                print "Set thumbnail content"
            elif d.type == "delete_thumb":
                print "Delete thumbnail"

    def _apply_pull_diff(self, diffs, local_dict, remote_res):
        files_dir = os.path.join(self._folder_path, "files")
        for d in diffs:
            if d.type == "delete_file_content":
                os.remove(os.path.join(files_dir, d.key))
            elif d.type == "set_file_content":
                content_reader = remote_res.get_file(d.key).get_content()
                with open(os.path.join(files_dir, d.key), "w") as fd:
                    fd.write(content_reader.read())
            elif d.type == "set_thumb":
                content_reader = remote_res.get_thumbnail_content()
                with open(os.path.join(self._folder_path, "thumb"), "w") as fd:
                    fd.write(content_reader.read())
            elif d.type == "delete_thumb":
                os.remove(os.path.join(self._folder_path, "thumb"))
        remote_res.dump(self._folder_path)

    def _apply_push_diff(self, diffs, local_dict, remote_res):
        remote_res.load(self._folder_path)

        # Delete handlers if any
        handlers = remote_res.get_json().get("handlers")
        if not handlers is None:
            remote_res.handlers = []
            remote_res.update()
            # Reload local content
            remote_res.load(self._folder_path)

        # Reset sub-collections
        for d in diffs:
            if d.key == "files":
                if d.type == "delete" or d.type == "update":
                    # Delete all
                    for f in remote_res.files():
                        f.delete()

                if d.type == "create" or d.type == "update":
                    # (Re)-create all
                    for f in remote_res.files_f:
                        remote_res.files()._create(f)

            if d.key == "parameters":
                if d.type == "delete" or d.type == "update":
                    # Delete all
                    for p in remote_res.parameters():
                        p.delete()

                if d.type == "create" or d.type == "update":
                    # (Re)-create all
                    for p in remote_res.parameters_f:
                        remote_res.parameters()._create(p)

            if d.key == "settings":
                if d.type == "delete" or d.type == "update":
                    # Delete all
                    for s in remote_res.settings():
                        s.delete()

                if d.type == "create" or d.type == "update":
                    # (Re)-create all
                    for s in remote_res.settings_f:
                        remote_res.settings()._create(s)

        # Reset file contents
        for d in diffs:
            if d.type == "set_file_content":
                content_path = os.path.join(self._folder_path, "files", d.key)
                if os.path.exists(content_path):
                    remote_res.get_file(d.key).set_content(content_path)
            elif d.type == "set_thumb":
                remote_res.set_thumbnail_content(os.path.join(self._folder_path, "thumb"))

        # Update remaining fields
        remote_res.update()

    def pull(self, remote_res, dry_run = False):
        """
        Pulls changes from remote entity.

        @param remote_res: Remote entity representation.
        @type remote_res: L{Entity}
        @param dry_run: Dry run flag. If true, diffs are displayed on standard
        output but not applied.
        @type dry_run: bool
        """

        remote_json = remote_res.get_json()
        local_json = json.load(open(self._deffile_path, "r"), object_pairs_hook=OrderedDict)

        diffs = self._diff(remote_json, local_json, True, RemoteFileProvider(remote_res), LocalFileProvider(self._folder_path))
        if dry_run:
            self._print_diff(diffs)
        else:
            self._apply_pull_diff(diffs, local_json, remote_res)

    def push(self, remote_res, dry_run = False):
        """
        Pushes changes to remote entity.

        @param remote_res: Remote entity representation.
        @type remote_res: L{Entity}
        @param dry_run: Dry run flag. If true, diffs are displayed on standard
        output but not applied.
        @type dry_run: bool
        """

        remote_json = remote_res.get_json()
        local_json = json.load(open(self._deffile_path, "r"), object_pairs_hook=OrderedDict)

        diffs = self._diff(local_json, remote_json, False, LocalFileProvider(self._folder_path), RemoteFileProvider(remote_res))
        if dry_run:
            self._print_diff(diffs)
        else:
            self._apply_push_diff(diffs, local_json, remote_res)
