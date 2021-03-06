# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the 'License'); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import unittest

from glance.api.v2 import schemas
import glance.tests.unit.utils as test_utils
import glance.schema


class TestSchemasController(unittest.TestCase):

    def setUp(self):
        super(TestSchemasController, self).setUp()
        self.schema_api = glance.schema.API()
        self.controller = schemas.Controller({}, self.schema_api)

    def test_index(self):
        req = test_utils.FakeRequest()
        output = self.controller.index(req)
        expected = {'links': [
            {'rel': 'image', 'href': '/v2/schemas/image'},
            {'rel': 'access', 'href': '/v2/schemas/image/access'},
        ]}
        self.assertEqual(expected, output)

    def test_image(self):
        req = test_utils.FakeRequest()
        output = self.controller.image(req)
        self.assertEqual(self.schema_api.get_schema('image'), output)

    def test_access(self):
        req = test_utils.FakeRequest()
        output = self.controller.access(req)
        self.assertEqual(self.schema_api.get_schema('access'), output)
