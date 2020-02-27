# rest.client - Generic client for crud opetations in a REST-Json API.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from future import standard_library
import base64
import six
standard_library.install_aliases()
from builtins import object
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, json
import comodit_client.util.fileupload as fileupload
from urllib.error import HTTPError
from comodit_client.util import urllibx
from comodit_client.rest.exceptions import ApiException, RetryApiException
from collections import OrderedDict


class HttpClient(object):
    def __init__(self, endpoint, username, password, token, insecure_upload = False, mfa = None):
        self.endpoint = endpoint.rstrip('/')
        self.username = username
        self.password = password
        self.token = token
        self.mfa = mfa
        self._insecure_upload = insecure_upload
        self.retryErrorCount = 0

    def create(self, entity, item = None, parameters = {}, decode = True):
        url = self._encode_url(entity, parameters)

        if not item is None:
            try:
                json_data = json.dumps(item)
            except Exception as e:
                raise ApiException("Could not encode given data: " + e.message, 0)
            req = self._new_request_with_data(url, "POST", json_data)
        else:
            req = self._new_request(url, "POST")
            # Fix regarding Nginx not supporting empty requests with no
            # Content-Length
            req.add_header("Content-Length", 0)
        try:
            raw = self._urlopen(req)
        except RetryApiException:
            return self.create(entity, item, parameters, decode)

        if decode:
            try:
                return self._decode_and_keep_key_order(raw)
            except:
                raise ApiException("Could not decode response: " + raw.read(), 0)
        else:
            return raw

    def _decode_and_keep_key_order(self, response):
        return json.loads(self.decode(response), object_pairs_hook=OrderedDict)

    def decode(self, response):
        return response.read().decode('utf-8', errors = 'ignore')

    def read(self, entity, parameters = {}, decode = True):
        url = self._encode_url(entity, parameters)
        req = self._new_request(url, "GET")
        try:
            raw = self._urlopen(req)
        except RetryApiException:
            return self.read(entity, parameters, decode)

        if decode:
            return self._decode_and_keep_key_order(raw)
        else:
            return raw

    def update(self, entity, item = None, parameters = {}, decode = True):
        url = self._encode_url(entity, parameters)
        if item is not None:
            req = self._new_request_with_data(url, "PUT", json.dumps(item))
        else:
            req = self._new_request(url, "PUT")
            # Fix regarding Nginx not supporting empty requests with no
            # Content-Length
            req.add_header("Content-Length", 0)
        try:
            raw = self._urlopen(req)
        except RetryApiException:
            return self.update(entity, item, parameters, decode)

        if decode:
            return self._decode_and_keep_key_order(raw)
        else:
            return raw

    def delete(self, entity, parameters = {}):
        url = self._encode_url(entity, parameters)
        req = self._new_request(url, "DELETE")

        try:
            self._urlopen(req)
        except RetryApiException:
            self.delete(entity, parameters)

    def _encode_url(self, entity, parameters):
        url = self.endpoint + "/" + urllib.parse.quote(entity, "/%")
        if len(parameters) > 0:
            url = url + "?" + urllib.parse.urlencode(parameters)
        return url

    def upload_to_exising_file_with_path(self, file_name, path):
        fileupload.post_multipart(self._encode_url(path, []), [],
                                             [("file", file_name)],
                                             insecure = self._insecure_upload,
                                             headers = self._auth_headers())

    def _auth_headers(self):
        if self._is_token_available():
            return {
                       "X-ComodIT-AppKey": self._get_app_key_field(),
                    }
        else:
            if self._is_mfa_enabled():
                return {
                           "Authorization": self._get_basic_authorization_field(),
                           "X-ComodIT-TotpToken": self._get_mfa_field(),
                        }
            else :
                return {
                    "Authorization": self._get_basic_authorization_field(),
                }

    def _is_token_available(self):
        return self.token

    def _is_mfa_enabled(self):
        return self.mfa

    def _get_basic_authorization_field(self):
        s = six.b(self.username + ":" + self.password)
        return "Basic " + base64.b64encode(s).decode('utf-8')

    def _headers(self):
        headers = self._auth_headers()
        headers["Content-Type"] = "application/json"
        return headers

    def _get_app_key_field(self):
        return self.token

    def _get_mfa_field(self):
        return self.mfa

    def _urlopen(self, request):
        try:
            result = urllib.request.urlopen(request)
            self.retryErrorCount = 0
            return result
        except HTTPError as err:
            if self.retryErrorCount < 3 and err.code == 401 and self._is_mfa_enabled():
                self.retryErrorCount +=1
                self.mfa = input("[%s] Invalid credential please verify mfa: " % self.retryErrorCount)
                raise RetryApiException("Invalid credential", err.code)

            err_content = err.read().decode('utf-8', errors = 'ignore')
            try:
                data = json.loads(err_content)
                msg_list = data["error"]
                message = "["
                if len(msg_list) > 0:
                    i = 0
                    while i < len(msg_list) - 1:
                        message += msg_list[i] if msg_list[i] else "None"
                        message += ", "
                        i += 1
                    message += msg_list[len(msg_list) - 1] if msg_list[len(msg_list) - 1] else "None"
                message += "]"
            except Exception:
                message = err_content

            raise ApiException(message, err.code)

    def _new_request(self, url, m):
        return urllibx.RequestWithMethod(url, method = m, headers = self._headers())

    def _new_request_with_data(self, url, m, d):
        return urllibx.RequestWithMethod(url, method = m, headers = self._headers(), data = six.b(d))
