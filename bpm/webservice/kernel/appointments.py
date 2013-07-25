# coding=utf-8
import logging
import httplib
import json
from django.http import HttpResponse

from bpm.kernel import states
from bpm.kernel.models import Task
from bpm.webservice.utils import render_doc
from bpm.webservice.kernel.task import TaskResource
from bpm.webservice.utils import CT_V1
from bpm.webservice.utils import render_doc

LOGGER = logging.getLogger(__name__)


def _appointment(task_model, to_state):
    try:
        result = task_model.appoint(to_state)
    except Exception, e:
        LOGGER.exception('failed to appoint task to %s: %s' % (to_state, task_model))
        return HttpResponse('Exception during appointment: %s' % e,
                            CT_V1, httplib.INTERNAL_SERVER_ERROR)
    else:
        if result:
            return HttpResponse(json.dumps(TaskResource.dump_task(task_model)),
                                CT_V1, httplib.OK)
        else:
            LOGGER.error('failed to appoint task to %s: %s' % (to_state, task_model))
            return HttpResponse('Current status is unable to transit to ready',
                                CT_V1, httplib.PRECONDITION_FAILED)


class AppointmentsToRevoked(object):
    """
    撤销任务的预约（请求任务在合适的时候撤销）
    """
    @classmethod
    @render_doc
    def post(cls, task_model):
        """
        .. http:post:: /tasks/(int:task_id)/appointments/to-revoked

            创建对给定id的任务的撤销预约。

            :param task_id: 任务的id
            :type task_id: int
            :status 201: 预约成功。返回JSON类型，任务详情
            :status 412: 因为任务状态不可预约失败。返回字符串类型，错误消息
            :status 404: 给定id的任务没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  POST /task/101/appointments/to-revoked HTTP/1.1
                  Accept: application/vnd.bpm;v=1

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 201 CREATED
                    Content-Type: application/vnd.bpm;v=1

                    {{ example_task|render:"{'id':101,'appointment':'REVOKED'}" }}
        """
        _appointment(task_model, states.REVOKED)


class AppointmentsToSuspended(object):
    """
    暂停任务的预约（请求任务在合适的时候暂停）
    """
    @classmethod
    @render_doc
    def post(cls, task_model):
        """
        .. http:post:: /tasks/(int:task_id)/appointments/to-suspended

            创建对给定id的任务的暂停预约。

            :param task_id: 任务的id
            :type task_id: int
            :status 201: 预约成功。返回JSON类型，任务详情
            :status 412: 因为任务状态不可预约失败。返回字符串类型，错误消息
            :status 404: 给定id的任务没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  POST /task/101/appointments/to-suspended HTTP/1.1
                  Accept: application/vnd.bpm;v=1

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 201 CREATED
                    Content-Type: application/vnd.bpm;v=1

                    {{ example_task|render:"{'id':101,'appointment':'SUSPENDED'}" }}
        """
        return _appointment(task_model, states.SUSPENDED)