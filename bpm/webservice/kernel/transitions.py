# -*- coding: utf-8 -*-
from django.http import HttpResponse
from bpm.kernel.models import Task
from bpm.kernel.states import READY
from bpm.webservice.kernel.task import TaskResource
from bpm.webservice.utils import CT_V1


class TransitionsToReady(object):
    """
    继续执行任务的请求
    """
    @classmethod
    def post(cls, request, task_instance):
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

                    {
                        "id": 101,
                        "state": "SUSPENDED",
                        "task_class_name": "package.example.SomeProcess",
                        "app_code": "qtrelease",
                        "creator": "mattsu",
                        "create_time": "2013-12-8 12:00:00 01.00",
                        "complete_time": "2013-12-8 12:00:07.30",
                        "app_data": {
                            "ijobs_task_id": "1445"
                        },
                        "ref_self": "/tasks/101"
                    }
        """
        try:
            result = Task.objects.transit(task_instance, READY)
        except Exception, e:
            return HttpResponse('Exception during transition: %s' % e,
                                CT_V1, 500)
        else:
            if result:
                return HttpResponse(TaskResource.output(task_instance),
                                    CT_V1, 200)
            else:
                return HttpResponse('Current status is unable to transit to ready',
                                    CT_V1, 412)
