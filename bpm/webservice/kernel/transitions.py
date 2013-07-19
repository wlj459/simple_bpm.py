# -*- coding: utf-8 -*-
from django.http import HttpResponse
from bpm.kernel.models import Task
from bpm.kernel.states import READY
from bpm.webservice.kernel.task import TaskResource
from bpm.webservice.utils import CT_V1
from bpm.webservice.utils import render_doc
import logging

LOGGER = logging.getLogger(__name__)


class TransitionsToReady(object):
    """
    继续执行任务的请求
    """
    @classmethod
    @render_doc
    def post(cls, request, task_model):
        """
        .. http:post:: /task/(int:task_id)/transitions/to-ready

            创建对给定id的任务的继续执行的请求。可以用来继续执行被暂停的任务，也可以用来外部通知组件回调。

            :param task_id: 任务的id
            :type task_id: int
            :status 200: 继续执行的请求下达成功。返回JSON类型，任务详情
            :status 412: 因为任务状态不可继续执行失败。返回字符串类型，错误消息
            :status 404: 给定id的任务没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  POST /task/101/transitions/to-ready HTTP/1.1
                  Accept: application/vnd.bpm;v=1

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 201 CREATED
                    Content-Type: application/vnd.bpm;v=1

                    {{ example_task|render:"{'id':101,'state':'READY'}" }}
        """
        try:
            result = Task.objects.transit(task_model, READY)
        except Exception, e:
            LOGGER.exception('failed to transit task to ready: %s' % task_model)
            return HttpResponse('Exception during transition: %s' % e,
                                CT_V1, 500)
        else:
            if result:
                return HttpResponse(TaskResource.dump_task(task_model),
                                    CT_V1, 200)
            else:
                LOGGER.error('failed to transit task to ready: %s' % task_model)
                return HttpResponse('Current status is unable to transit to ready',
                                    CT_V1, 412)
