# coding=utf-8
from bpm.webservice.utils import render_doc

class AppointmentsToRevoked(object):
    """
    撤销任务的预约（请求任务在合适的时候撤销）
    """
    @classmethod
    @render_doc
    def post(cls):
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
        pass


class AppointmentsToSuspended(object):
    """
    暂停任务的预约（请求任务在合适的时候暂停）
    """
    @classmethod
    @render_doc
    def post(cls):
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
        pass