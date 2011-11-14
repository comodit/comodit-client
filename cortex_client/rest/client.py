# rest.client - Generic client for crud opetations in a REST-Json API.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import urllib, urllib2, json, urlparse
import cortex_client.util.fileupload as fileupload
from urllib2 import HTTPError
from cortex_client.util import urllibx
from cortex_client.rest.exceptions import ApiException


class Client:

    def __init__(self, endpoint, username, password):
        self.endpoint = endpoint.rstrip('/')
        self.username = username
        self.password = password

    def create(self, resource, item, parameters = {}, decode = True):
        url = self.endpoint + "/" + resource
        if len(parameters) > 0:
            url = url + "?" + urllib.urlencode(parameters)

        req = urllibx.RequestWithMethod(url, method = "POST", headers = self._headers(), data = json.dumps(item))
        raw = self._urlopen(req)
        if decode:
            return json.load(raw)
        else:
            return raw

    def read(self, resource, parameters = {}, decode = True):
        url = self.endpoint + "/" + urllib.quote(resource)
        if len(parameters) > 0:
            url = url + "?" + urllib.urlencode(parameters)

        req = urllibx.RequestWithMethod(url, method = "GET", headers = self._headers())
        raw = self._urlopen(req)
        if decode:
            return json.load(raw)
        else:
            return raw

    def update(self, resource, item = None, parameters = {}, decode = True):
        url = self.endpoint + "/" + urllib.quote(resource)
        if len(parameters) > 0:
            url = url + "?" + urllib.urlencode(parameters)

        req = urllibx.RequestWithMethod(url, method = "PUT", headers = self._headers())
        if item: req.add_data(json.dumps(item))
        raw = self._urlopen(req)
        if decode:
            return json.load(raw)
        else:
            return raw

    def delete(self, resource, parameters = {}):
        url = self.endpoint + "/" + urllib.quote(resource)
        if len(parameters) > 0:
            url = url + "?" + urllib.urlencode(parameters)

        req = urllibx.RequestWithMethod(url, method = 'DELETE', headers = self._headers())
        self._urlopen(req)
        return

    def upload_new_file(self, file_name, upload_url = None):
        with open(file_name, 'r') as f:
            if upload_url is None:
                url = urlparse.urlparse(self.endpoint + "/files")
            else:
                url = upload_url
            response = fileupload.post_multipart(url.netloc, url.path,
                                                 [("test", "none")],
                                                 [("file", file_name, f.read())],
                                                 {"Authorization": "Basic " + (self.username + ":" + self.password).encode("base64").rstrip()})

        return json.loads(response)[0];

    def upload_to_exising_file(self, file_name, uuid):
        return self.upload_to_exising_file_with_path(file_name, "files/" + uuid)

    def upload_to_exising_file_with_path(self, file_name, path):
        url = urlparse.urlparse(self.endpoint + "/" + path)
        response = fileupload.post_multipart(url.netloc, url.path,
                                             [("test", "none")],
                                             [("file", file_name)],
                                             {"Authorization": "Basic " + (self.username + ":" + self.password).encode("base64").rstrip()})

    def _headers(self):
        s = self.username + ":" + self.password
        headers = {
                   "Authorization": "Basic " + s.encode("base64").rstrip(),
                   "Content-Type": "application/json",
                   }
        return headers

    def _urlopen(self, request):
        try:
            return urllib2.urlopen(request)
        except HTTPError as err:
            try:
                data = json.load(err)
                message = data["error"]
                errno = err.code
            except:
                message = err.msg
                errno = err.code
            raise ApiException(message, errno)

