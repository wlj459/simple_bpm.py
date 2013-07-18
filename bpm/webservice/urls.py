# coding=utf-8

from django.conf.urls import patterns, include, url


urlpatterns = patterns('bpm.webservice.views',

    # sphinx-doc index
    # url(r'^$', 'container.views.home', name='home'),


    # url(r'^tasks/', kernel.tasks),
    url(r'^task/(?P<task_id>\d+)/transitions/to-ready/', 'transitions_to_ready'),
)
