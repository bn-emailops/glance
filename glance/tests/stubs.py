# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Stubouts, mocks and fixtures for the test suite"""

import os

try:
    import sendfile
    SENDFILE_SUPPORTED = True
except ImportError:
    SENDFILE_SUPPORTED = False

import webob

from glance.api.v1 import router
import glance.common.client
from glance.common import context
<<<<<<< HEAD
from glance.common import exception
from glance.registry import server as rserver
from glance.api import v1 as server
from glance.api.middleware import version_negotiation
import glance.store
import glance.store.filesystem
import glance.store.http
import glance.registry.db.api
=======
from glance.registry.api import v1 as rserver
from glance.tests import utils
>>>>>>> upstream/master


VERBOSE = False
DEBUG = False


def stub_out_registry_and_store_server(stubs, base_dir):
    """
    Mocks calls to 127.0.0.1 on 9191 and 9292 for testing so
    that a real Glance server does not need to be up and
    running
    """

    class FakeRegistryConnection(object):

        def __init__(self, *args, **kwargs):
            pass

        def connect(self):
            return True

        def close(self):
            return True

        def request(self, method, url, body=None, headers=None):
            self.req = webob.Request.blank("/" + url.lstrip("/"))
            self.req.method = method
            if headers:
                self.req.headers = headers
            if body:
                self.req.body = body

        def getresponse(self):
            sql_connection = os.environ.get('GLANCE_SQL_CONNECTION',
                                            "sqlite://")
            conf = utils.TestConfigOpts({
                    'sql_connection': sql_connection,
                    'verbose': VERBOSE,
                    'debug': DEBUG
                    })
            api = context.UnauthenticatedContextMiddleware(
                    rserver.API(conf), conf)
            res = self.req.get_response(api)

            # httplib.Response has a read() method...fake it out
            def fake_reader():
                return res.body

            setattr(res, 'read', fake_reader)
            return res

    class FakeSocket(object):

        def __init__(self, *args, **kwargs):
            pass

        def fileno(self):
            return 42

    class FakeSendFile(object):

        def __init__(self, req):
            self.req = req

        def sendfile(self, o, i, offset, nbytes):
            os.lseek(i, offset, os.SEEK_SET)
            prev_len = len(self.req.body)
            self.req.body += os.read(i, nbytes)
            return len(self.req.body) - prev_len

    class FakeGlanceConnection(object):

        def __init__(self, *args, **kwargs):
            self.sock = FakeSocket()
            self.stub_force_sendfile = kwargs.get('stub_force_sendfile',
                                                  SENDFILE_SUPPORTED)

        def connect(self):
            return True

        def close(self):
            return True

        def _clean_url(self, url):
            #TODO(bcwaldon): Fix the hack that strips off v1
            return url.replace('/v1', '', 1) if url.startswith('/v1') else url

        def putrequest(self, method, url):
            self.req = webob.Request.blank(self._clean_url(url))
            if self.stub_force_sendfile:
                fake_sendfile = FakeSendFile(self.req)
                stubs.Set(sendfile, 'sendfile', fake_sendfile.sendfile)
            self.req.method = method

        def putheader(self, key, value):
            self.req.headers[key] = value

        def endheaders(self):
            hl = [i.lower() for i in self.req.headers.keys()]
            assert not ('content-length' in hl and
                        'transfer-encoding' in hl), \
                'Content-Length and Transfer-Encoding are mutually exclusive'

        def send(self, data):
            # send() is called during chunked-transfer encoding, and
            # data is of the form %x\r\n%s\r\n. Strip off the %x and
            # only write the actual data in tests.
            self.req.body += data.split("\r\n")[1]

        def request(self, method, url, body=None, headers=None):
<<<<<<< HEAD
            self.req = webob.Request.blank("/" + url.lstrip("/"))
=======
            self.req = webob.Request.blank(self._clean_url(url))
>>>>>>> upstream/master
            self.req.method = method
            if headers:
                self.req.headers = headers
            if body:
                self.req.body = body

        def getresponse(self):
<<<<<<< HEAD
            options = {'verbose': VERBOSE,
                       'debug': DEBUG,
                       'bind_host': '0.0.0.0',
                       'bind_port': '9999999',
                       'registry_host': '0.0.0.0',
                       'registry_port': '9191',
                       'default_store': 'file',
                       'filesystem_store_datadir': FAKE_FILESYSTEM_ROOTDIR}
            api = version_negotiation.VersionNegotiationFilter(
                context.ContextMiddleware(server.API(options), options),
                options)
=======
            conf = utils.TestConfigOpts({
                    'verbose': VERBOSE,
                    'debug': DEBUG,
                    'bind_host': '0.0.0.0',
                    'bind_port': '9999999',
                    'registry_host': '0.0.0.0',
                    'registry_port': '9191',
                    'default_store': 'file',
                    'filesystem_store_datadir': base_dir,
                    'policy_file': os.path.join(base_dir, 'policy.json'),
                    })
            api = context.UnauthenticatedContextMiddleware(
                    router.API(conf), conf)
>>>>>>> upstream/master
            res = self.req.get_response(api)

            # httplib.Response has a read() method...fake it out
            def fake_reader():
                return res.body

            setattr(res, 'read', fake_reader)
            return res

    def fake_get_connection_type(client):
        """
        Returns the proper connection type
        """
        DEFAULT_REGISTRY_PORT = 9191
        DEFAULT_API_PORT = 9292

        if (client.port == DEFAULT_API_PORT and
            client.host == '0.0.0.0'):
            return FakeGlanceConnection
        elif (client.port == DEFAULT_REGISTRY_PORT and
              client.host == '0.0.0.0'):
            return FakeRegistryConnection

    def fake_image_iter(self):
        for i in self.source.app_iter:
            yield i

    def fake_sendable(self, body):
        force = getattr(self, 'stub_force_sendfile', None)
        if force is None:
            return self._stub_orig_sendable(body)
        else:
            if force:
                assert glance.common.client.SENDFILE_SUPPORTED
            return force

    stubs.Set(glance.common.client.BaseClient, 'get_connection_type',
              fake_get_connection_type)
    setattr(glance.common.client.BaseClient, '_stub_orig_sendable',
              glance.common.client.BaseClient._sendable)
    stubs.Set(glance.common.client.BaseClient, '_sendable',
              fake_sendable)
    stubs.Set(glance.common.client.ImageBodyIterator, '__iter__',
              fake_image_iter)


def stub_out_registry_server(stubs, **kwargs):
    """
    Mocks calls to 127.0.0.1 on 9191 for testing so
    that a real Glance Registry server does not need to be up and
    running
    """

    class FakeRegistryConnection(object):

        def __init__(self, *args, **kwargs):
            pass

        def connect(self):
            return True

        def close(self):
            return True

        def request(self, method, url, body=None, headers=None):
            self.req = webob.Request.blank("/" + url.lstrip("/"))
            self.req.method = method
            if headers:
                self.req.headers = headers
            if body:
                self.req.body = body

        def getresponse(self):
            sql_connection = kwargs.get('sql_connection', "sqlite:///")
            conf = utils.TestConfigOpts({
                    'sql_connection': sql_connection,
                    'verbose': VERBOSE,
                    'debug': DEBUG
                    })
            api = context.UnauthenticatedContextMiddleware(
                    rserver.API(conf), conf)
            res = self.req.get_response(api)

            # httplib.Response has a read() method...fake it out
            def fake_reader():
                return res.body

            setattr(res, 'read', fake_reader)
            return res

    def fake_get_connection_type(client):
        """
        Returns the proper connection type
        """
        DEFAULT_REGISTRY_PORT = 9191

        if (client.port == DEFAULT_REGISTRY_PORT and
            client.host == '0.0.0.0'):
            return FakeRegistryConnection

    def fake_image_iter(self):
        for i in self.response.app_iter:
            yield i

    stubs.Set(glance.common.client.BaseClient, 'get_connection_type',
              fake_get_connection_type)
    stubs.Set(glance.common.client.ImageBodyIterator, '__iter__',
              fake_image_iter)
