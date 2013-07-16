# -*- coding: utf-8 -*-
class Suspensions(object):
    """
    暂停任务的预约（请求任务在合适的时候暂停）
    """
    def post(self):
        """
        .. http:post:: /tasks/(int:task_id)/appointments/suspensions

            创建对给定id的任务的暂停预约。

            :param task_id: 任务的id
            :type task_id: int
            :status 201: 预约成功。返回JSON类型，任务详情
            :status 412: 因为任务状态不可预约失败。返回字符串类型，错误消息
            :status 404: 给定id的任务没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  POST /task/101/appointments/suspensions HTTP/1.1
                  Accept: application/vnd.bpm;v=1

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 201 CREATED
                    Content-Type: application/vnd.bpm;v=1

                    {
                        "id": 101,
                        "state": "RUNNING",
                        "appointment": "SUSPENDED",
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
        pass