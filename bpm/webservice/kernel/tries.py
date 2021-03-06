# coding=utf-8

import logging
import httplib
import json
from django.http import HttpResponse
from bpm.kernel.models import Task
from bpm.webservice.kernel.task import TaskResource
from bpm.webservice.utils import CT_V1
from bpm.webservice.utils import render_doc

LOGGER = logging.getLogger(__name__)


class Tries(object):
    """
    本资源代表一个任务的所有重试集合
    """
    @classmethod
    def post(cls, task_model):
        """
        .. http:post:: /tasks/(int:task_id)/tries

            重试给定id的任务（实际是以创建一个新的任务的方式再次执行）

            :param task_id: 要被重试的任务id
            :type task_id: int
            :jsonparam exec_kwargs: 类型为dict。执行任务时使用的关键字参数（key=value形式），传递给Task.start方法
            :status 201: 创建重试的任务成功。返回JSON类型，创建的任务资源
            :status 400: 创建重试任务的请求参数不是JSON或者exec_kwargs不是dict类型。返回字符串类型，错误消息
            :status 404: 被重试的任务没有找到。返回字符串类型，错误消息
            :status 412: 被重试的任务处于不可重试的状态。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  POST /tasks/101/tries HTTP/1.1
                  Accept: application/vnd.bpm;v=1

                  {
                    "exec_kwargs": {
                        "arg1": "some value"
                    }
                  }

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 201 CREATED
                    Content-Type: application/vnd.bpm;v=1

                    {
                        "id": 102,
                        "ref_self": "/tasks/102"
                    }
        """
        try:
            result = Task.objects.retry(task_model)
        except Exception, e:
            LOGGER.exception('failed to retry task: %s' % task_model)
            return HttpResponse('Exception during retry: %s' % e,
                                CT_V1, httplib.INTERNAL_SERVER_ERROR)
        else:
            if result:
                return HttpResponse(json.dumps(TaskResource.dump_task(task_model)),
                                    CT_V1, httplib.CREATED)
            else:
                LOGGER.error('failed to retry: %s' % task_model)
                return HttpResponse('Current status is unable to retry',
                                    CT_V1, httplib.PRECONDITION_FAILED)


    @classmethod
    @render_doc
    def get(cls):
        """
        .. http:get:: /tasks/(int:task_id)/tries

            列出给定id的任务的所有重试。

            :param task_id: 要被重试的任务id
            :type task_id: int
            :status 200: 获取重试任务列表成功。返回JSON类型，任务列表
            :status 404: 给定id的任务没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  GET /tasks/101/tries HTTP/1.1
                  Accept: application/vnd.bpm;v=1

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 200 OK
                    Content-Type: application/vnd.bpm;v=1

                    {
                        "tasks": [
                            {{ example_task|render:"{'id':100, 'state':'FAILURE', 'indention_level': 7}" }}, {{ example_task|render:"{'id':101, 'state':'RUNNING', 'indention_level':7}" }}
                        ],
                        "form_retry": {
                            "action": "/tasks/101/tries",
                            "method": "POST",
                            "body": {
                                "exec_kwargs": ""
                            }
                        }
                    }
        """
        pass  # TODO