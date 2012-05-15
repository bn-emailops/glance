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

import json

import jsonschema
import webob.exc

from glance.api.v2 import base
from glance.api.v2 import schemas
from glance.common import exception
from glance.common import wsgi
import glance.registry.db.api


class ImagesController(base.Controller):
    def __init__(self, conf, db_api=None):
        super(ImagesController, self).__init__(conf)
        self.db_api = db_api or glance.registry.db.api
        self.db_api.configure_db(conf)

    def create(self, req, image):
        if 'owner' not in image:
            image['owner'] = req.context.owner
        elif not req.context.is_admin:
            raise webob.exc.HTTPForbidden()

        #TODO(bcwaldon): this should eventually be settable through the API
        image['status'] = 'queued'

        return self.db_api.image_create(req.context, image)

    def index(self, req):
        filters = {'deleted': False}
        return self.db_api.image_get_all(req.context, filters=filters)

    def show(self, req, image_id):
        try:
            return self.db_api.image_get(req.context, image_id)
        except exception.NotFound:
            raise webob.exc.HTTPNotFound()

    def update(self, req, image_id, image):
        try:
            return self.db_api.image_update(req.context, image_id, image)
        except exception.NotFound:
            raise webob.exc.HTTPNotFound()

    def delete(self, req, image_id):
        try:
            self.db_api.image_destroy(req.context, image_id)
        except exception.NotFound:
            raise webob.exc.HTTPNotFound()


class RequestDeserializer(wsgi.JSONRequestDeserializer):
    def __init__(self, conf, schema_api):
        super(RequestDeserializer, self).__init__()
        self.conf = conf
        self.schema_api = schema_api

    def _validate(self, request, obj):
        schema = self.schema_api.get_schema('image')
        jsonschema.validate(obj, schema)

    def create(self, request):
        output = super(RequestDeserializer, self).default(request)
        body = output.pop('body')
        self._validate(request, body)
        output['image'] = body
        return output

    def update(self, request):
        output = super(RequestDeserializer, self).default(request)
        body = output.pop('body')
        self._validate(request, body)
        output['image'] = body
        return output


class ResponseSerializer(wsgi.JSONResponseSerializer):
    def __init__(self, schema_api):
        super(ResponseSerializer, self).__init__()
        self.schema_api = schema_api

    def _get_image_href(self, image, subcollection=''):
        base_href = '/v2/images/%s' % image['id']
        if subcollection:
            base_href = '%s/%s' % (base_href, subcollection)
        return base_href

    def _get_image_links(self, image):
        return [
            {'rel': 'self', 'href': self._get_image_href(image)},
            {'rel': 'file', 'href': self._get_image_href(image, 'file')},
            {'rel': 'describedby', 'href': '/v2/schemas/image'},
        ]

    def _filter_allowed_image_attributes(self, image):
        schema = self.schema_api.get_schema('image')
        attrs = schema['properties'].keys()
        return dict((k, v) for (k, v) in image.iteritems() if k in attrs)

    def _format_image(self, image):
        _image = dict(image['properties'])
        _image = self._filter_allowed_image_attributes(_image)

        for key in ['id', 'name']:
            _image[key] = image[key]

        _image['links'] = self._get_image_links(image)
        return _image

    def create(self, response, image):
        response.body = json.dumps({'image': self._format_image(image)})
        response.location = self._get_image_href(image)

    def show(self, response, image):
        response.body = json.dumps({'image': self._format_image(image)})

    def update(self, response, image):
        response.body = json.dumps({'image': self._format_image(image)})

    def index(self, response, images):
        body = {
            'images': [self._format_image(i) for i in images],
            'links': [],
        }
        response.body = json.dumps(body)

    def delete(self, response, result):
        response.status_int = 204


def create_resource(conf, schema_api):
    """Images resource factory method"""
    deserializer = RequestDeserializer(conf, schema_api)
    serializer = ResponseSerializer(schema_api)
    controller = ImagesController(conf)
    return wsgi.Resource(controller, deserializer, serializer)
