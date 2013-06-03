import json

from django.conf.urls import patterns, url
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, Resource
from tastypie.utils import trailing_slash
from tastypie.validation import CleanedDataFormValidation

from ..models import Task
from .forms import AddTaskForm


class ProcessResource(ModelResource):

    class Meta:
        authentication = Authentication()
        authorization = Authorization()
        fields = ['id', 'name']
        queryset = Task.objects.filter(parent__isnull=True)


class TaskResource(ModelResource):

    parent_id = fields.IntegerField(
        'parent_id',
        blank=True,
        null=True
    )

    class Meta:
        always_return_data = True

        authentication = Authentication()
        authorization = Authorization()

        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'patch']

        fields = ['id', 'parent_id', 'name', 'state', 'appointment', 'args', 'kwargs', 'data', 'ex_data']
        post_request_fields = ['name', 'args', 'kwargs']
        patch_fields = ['appointment']
        queryset = Task.objects.all()

    def _alter_data(self, data, mode):
        """
        mode:   (method, stage, level)
                method: the HTTP request method
                stage:  'request' or 'response'
                level:  'list' or 'detail'
        """
        method, stage, level = mode
        method = method.lower()

        for pattern in ('fields', 'excludes'):
            for attr_name in ('_'.join((method, pattern)),
                              '_'.join((method, stage, pattern)),
                              '_'.join((method, stage, level, pattern))):
                if hasattr(self._meta, attr_name):
                    locals()[pattern] = getattr(self._meta, attr_name)

        _fields = locals().get('fields')
        _excludes = locals().get('excludes')

        if _fields:
            data = {
                k: v for k, v in data.copy().iteritems() if k in _fields
            }
        elif _excludes:
            data = {
                k: v for k, v in data.copy().iteritems() if k not in _excludes
            }

        return data

    def alter_list_data_to_serialize(self, request, data):
        print 'alter_list_data_to_serialize'
        return self._alter_data(data,
                                mode=(request.method, 'response', 'list'))

    def alter_detail_data_to_serialize(self, request, bundle):
        print 'alter_detail_data_to_serialize'
        return self._alter_data(bundle.data,
                                mode=(request.method, 'response', 'detail'))

    def alter_deserialized_list_data(self, request, data):
        print 'alter_deserialized_list_data'
        return self._alter_data(data,
                                mode=(request.method, 'request', 'list'))

    def alter_deserialized_detail_data(self, request, data):
        print 'alter_deserialized_detail_data'
        return self._alter_data(data,
                                mode=(request.method, 'request', 'detail'))

    def dehydrate_args(self, bundle):
        return json.loads(bundle.data['args'])

    def dehydrate_kwargs(self, bundle):
        return json.loads(bundle.data['kwargs'])

    def hydrate_args(self, bundle):
        if 'args' in bundle.data:
            args = bundle.data['args']
        else:
            args = []

        bundle.data['args'] = json.dumps(args)

        return bundle

    def hydrate_kwargs(self, bundle):
        if 'kwargs' in bundle.data:
            kwargs = bundle.data['kwargs']
        else:
            kwargs = {}

        bundle.data['kwargs'] = json.dumps(kwargs)

        return bundle
