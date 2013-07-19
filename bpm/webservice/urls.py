# coding=utf-8

from django.conf.urls import patterns, include, url


urlpatterns = patterns('bpm.webservice.views',

    # sphinx-doc index
    # url(r'^$', 'container.views.home', name='home'),


    url(r'^tasks/(?P<task_class_name>[a-z_]{1}[a-z0-9_]*(\.[a-z_]{1}[a-z0-9_]*)*)', 'list_tasks'),
    url(r'^task/(?P<task_id>\d+)/transitions/to-ready/', 'transitions_to_ready'),
)
