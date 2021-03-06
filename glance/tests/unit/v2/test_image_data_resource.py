# Copyright 2012 OpenStack LLC.
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

import StringIO
import unittest

import webob

import glance.api.v2.image_data
from glance.common import utils
import glance.tests.unit.utils as test_utils
import glance.tests.utils


class TestImagesController(unittest.TestCase):
    def setUp(self):
        super(TestImagesController, self).setUp()

        conf = glance.tests.utils.TestConfigOpts({
                'verbose': True,
                'debug': True,
                })
        self.controller = glance.api.v2.image_data.ImageDataController(conf,
                db_api=test_utils.FakeDB(),
                store_api=test_utils.FakeStoreAPI())

    def test_download(self):
        request = test_utils.FakeRequest()
        output = self.controller.download(request, test_utils.UUID1)
        expected = {'data': 'XXX', 'size': 3}
        self.assertEqual(expected, output)

    def test_download_no_data(self):
        request = test_utils.FakeRequest()
        self.assertRaises(webob.exc.HTTPNotFound, self.controller.download,
                          request, test_utils.UUID2)

    def test_download_non_existant_image(self):
        request = test_utils.FakeRequest()
        self.assertRaises(webob.exc.HTTPNotFound, self.controller.download,
                          request, utils.generate_uuid())

    def test_upload_download(self):
        request = test_utils.FakeRequest()
        self.controller.upload(request, test_utils.UUID2, 'YYYY', 4)
        output = self.controller.download(request, test_utils.UUID2)
        expected = {'data': 'YYYY', 'size': 4}
        self.assertEqual(expected, output)

    def test_upload_non_existant_image(self):
        request = test_utils.FakeRequest()
        self.assertRaises(webob.exc.HTTPNotFound, self.controller.upload,
                          request, utils.generate_uuid(), 'YYYY', 4)

    def test_upload_data_exists(self):
        request = test_utils.FakeRequest()
        self.assertRaises(webob.exc.HTTPConflict, self.controller.upload,
                          request, test_utils.UUID1, 'YYYY', 4)

    def test_upload_download_no_size(self):
        request = test_utils.FakeRequest()
        self.controller.upload(request, test_utils.UUID2, 'YYYY', None)
        output = self.controller.download(request, test_utils.UUID2)
        expected = {'data': 'YYYY', 'size': 4}
        self.assertEqual(expected, output)


class TestImageDataDeserializer(unittest.TestCase):
    def setUp(self):
        self.deserializer = glance.api.v2.image_data.RequestDeserializer()

    def test_upload(self):
        request = test_utils.FakeRequest()
        request.headers['Content-Type'] = 'application/octet-stream'
        request.body = 'YYY'
        request.headers['Content-Length'] = 3
        output = self.deserializer.upload(request)
        data = output.pop('data')
        self.assertEqual(data.getvalue(), 'YYY')
        expected = {'size': 3}
        self.assertEqual(expected, output)

    def test_upload_chunked(self):
        request = test_utils.FakeRequest()
        request.headers['Content-Type'] = 'application/octet-stream'
        # If we use body_file, webob assumes we want to do a chunked upload,
        # ignoring the Content-Length header
        request.body_file = StringIO.StringIO('YYY')
        output = self.deserializer.upload(request)
        data = output.pop('data')
        self.assertEqual(data.getvalue(), 'YYY')
        expected = {'size': None}
        self.assertEqual(expected, output)

    def test_upload_chunked_with_content_length(self):
        request = test_utils.FakeRequest()
        request.headers['Content-Type'] = 'application/octet-stream'
        request.body_file = StringIO.StringIO('YYY')
        # The deserializer shouldn't care if the Content-Length is
        # set when the user is attempting to send chunked data.
        request.headers['Content-Length'] = 3
        output = self.deserializer.upload(request)
        data = output.pop('data')
        self.assertEqual(data.getvalue(), 'YYY')
        expected = {'size': 3}
        self.assertEqual(expected, output)

    def test_upload_with_incorrect_content_length(self):
        request = test_utils.FakeRequest()
        request.headers['Content-Type'] = 'application/octet-stream'
        # The deserializer shouldn't care if the Content-Length and
        # actual request body length differ. That job is left up
        # to the controller
        request.body = 'YYY'
        request.headers['Content-Length'] = 4
        output = self.deserializer.upload(request)
        data = output.pop('data')
        self.assertEqual(data.getvalue(), 'YYY')
        expected = {'size': 4}
        self.assertEqual(expected, output)

    def test_upload_wrong_content_type(self):
        request = test_utils.FakeRequest()
        request.headers['Content-Type'] = 'application/json'
        request.body = 'YYYYY'
        self.assertRaises(webob.exc.HTTPUnsupportedMediaType,
            self.deserializer.upload, request)


class TestImageDataSerializer(unittest.TestCase):
    def setUp(self):
        self.serializer = glance.api.v2.image_data.ResponseSerializer()

    def test_download(self):
        response = webob.Response()
        self.serializer.download(response, {'data': 'ZZZ', 'size': 3})
        self.assertEqual('ZZZ', response.body)
        self.assertEqual('3', response.headers['Content-Length'])
        self.assertEqual('application/octet-stream',
                         response.headers['Content-Type'])
