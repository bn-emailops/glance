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

import webob.exc

from glance.api.v2 import base
from glance.common import exception
from glance.common import wsgi
import glance.registry.db.api


class Controller(base.Controller):
    def __init__(self, conf, db=None):
        super(Controller, self).__init__(conf)
        self.db_api = db or glance.registry.db.api
        self.db_api.configure_db(conf)

    @staticmethod
    def _build_tag(image_tag):
        return {
            'value': image_tag['value'],
            'image_id': image_tag['image_id'],
        }

    def index(self, req, image_id):
        tags = self.db_api.image_tag_get_all(req.context, image_id)
        return [self._build_tag(t) for t in tags]

    def update(self, req, image_id, tag_value):
        self.db_api.image_tag_create(req.context, image_id, tag_value)

    def delete(self, req, image_id, tag_value):
        try:
            self.db_api.image_tag_delete(req.context, image_id, tag_value)
        except exception.NotFound:
            raise webob.exc.HTTPNotFound()


class ResponseSerializer(wsgi.JSONResponseSerializer):
    @staticmethod
    def _format_tag(tag):
        return tag['value']

    def index(self, response, tags):
        response.content_type = 'application/json'
        response.body = json.dumps([self._format_tag(t) for t in tags])

    def update(self, response, result):
        response.status_int = 204

    def delete(self, response, result):
        response.status_int = 204


def create_resource(conf):
    """Images resource factory method"""
    serializer = ResponseSerializer()
    controller = Controller(conf)
    return wsgi.Resource(controller, serializer=serializer)
