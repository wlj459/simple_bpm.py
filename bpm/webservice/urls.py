# coding=utf-8

from django.conf.urls import patterns, include, url


urlpatterns = patterns('bpm.webservice.views',

    # sphinx-doc index
    # url(r'^$', 'container.views.home', name='home'),


    url(r'^tasks/(?P<task_class_name>.*)', 'handle_tasks_resource'),
    url(r'^task/(?P<task_id>\d+)/transitions/to-ready/', 'transitions_to_ready'),
)
