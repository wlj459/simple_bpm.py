# coding=utf-8

from django.conf.urls import patterns, include, url


urlpatterns = patterns('bpm.webservice.views_v1',

    # sphinx-doc index
    # url(r'^$', 'container.views.home', name='home'),

    # 任务列表--查询/创建任务
    url(r'^tasks/(?P<task_class_name>.*)/$', 'handle_tasks_resource'),

    # 任务详情
        url(r'^task/(?P<task_id>\d+)/$', 'handle_task_resource'),

    # # 撤销
    url(r'^task/(?P<task_id>\d+)/appointments/to-revoked/$', 'handle_appt_resrc_to_revoked'),
    #
    # # 暂停
    url(r'^task/(?P<task_id>\d+)/appointments/to-suspended/$', 'handle_appt_resrc_to_suspended'),

    # 继续执行
    url(r'^task/(?P<task_id>\d+)/transitions/to-ready/$', 'handle_trans_resrc_to_ready'),

    # # 重试--列表/创建
    url(r'^task/(?P<task_id>\d+)/tries/$', 'handle_tries_resrc'),

    #
    # # 执行轨迹
    # url(r'^task/(?P<task_id>\d+)/trace/$', 'handle_trace_resrc'),
)
