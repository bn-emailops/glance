# Copyright 2012 OpenStack, LLC
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

import json
import unittest

import webob

import glance.api.v2.image_tags
import glance.tests.unit.utils as test_utils


class TestImageTagsController(unittest.TestCase):
    def setUp(self):
        super(TestImageTagsController, self).setUp()
        self.db = test_utils.FakeDB()
        conf = {}
        self.controller = glance.api.v2.image_tags.Controller(conf, self.db)

    def test_list_tags(self):
        request = test_utils.FakeRequest()
        tags = self.controller.index(request, test_utils.UUID1)
        expected = [
            {'value': 'ping', 'image_id': test_utils.UUID1},
            {'value': 'pong', 'image_id': test_utils.UUID1},
        ]
        self.assertEqual(expected, tags)

    def test_create_tag(self):
        request = test_utils.FakeRequest()
        self.controller.update(request, test_utils.UUID1, 'dink')

    def test_delete_tag(self):
        request = test_utils.FakeRequest()
        self.controller.delete(request, test_utils.UUID1, 'ping')

    def test_delete_tag_not_found(self):
        request = test_utils.FakeRequest()
        self.assertRaises(webob.exc.HTTPNotFound, self.controller.delete,
                          request, test_utils.UUID1, 'what')


class TestImagesSerializer(unittest.TestCase):
    def setUp(self):
        self.serializer = glance.api.v2.image_tags.ResponseSerializer()

    def test_list_tags(self):
        fixtures = [
            {'value': 'ping', 'image_id': test_utils.UUID1},
            {'value': 'pong', 'image_id': test_utils.UUID1},
        ]
        expected = ['ping', 'pong']
        response = webob.Response()
        self.serializer.index(response, fixtures)
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(expected, json.loads(response.body))

    def test_create_tag(self):
        response = webob.Response()
        self.serializer.update(response, None)
        self.assertEqual(204, response.status_int)

    def test_delete_tag(self):
        response = webob.Response()
        self.serializer.delete(response, None)
        self.assertEqual(204, response.status_int)
