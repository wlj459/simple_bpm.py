# -*- coding: utf-8 -*-
class Trace(object):
    """
    一个任务分解出的子任务构成的执行轨迹
    """
    def get(self):
        """
        .. http:get:: /tasks/(int:task_id)/trace

            列出给定id的任务的所有子类任务（包括后裔）构成的执行轨迹。

            :param task_id: 任务id
            :type task_id: int
            :status 200: 获取给定id任务的执行轨迹成功。返回JSON类型，执行轨迹
            :status 404: 给定id的任务没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  GET /tasks/99/trace HTTP/1.1
                  Accept: application/vnd.bpm;v=1

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 200 OK
                    Content-Type: application/vnd.bpm;v=1

                    {
                        "id": 99,
                        "state": "BLOCKED",
                        "task_class_name": "package.example.SomeProcess",
                        "app_code": "qtrelease",
                        "creator": "mattsu",
                        "create_time": "2013-12-8 12:00:00 01.00",
                        "complete_time": "2013-12-8 12:00:07.30",
                        "app_data": {
                            "ijobs_task_id": "1445"
                        },
                        "ref_self": "/tasks/99"
                        "tasks": [
                            {
                                "id": 100,
                                "state": "SUCCESS",
                                "task_class_name": "package.example.SomeProcess",
                                "app_code": "qtrelease",
                                "creator": "mattsu",
                                "create_time": "2013-12-8 12:00:00 01.00",
                                "complete_time": "2013-12-8 12:00:07.30",
                                "app_data": {
                                    "ijobs_task_id": "1445"
                                },
                                "ref_self": "/tasks/100"
                            }, {
                                "id": 101,
                                "state": "BLOCKED",
                                "task_class_name": "package.example.SomeProcess",
                                "app_code": "qtrelease",
                                "creator": "mattsu",
                                "create_time": "2013-12-8 12:01:00.00",
                                "complete_time": "2013-12-8 12:01:07.30",
                                "app_data": {
                                    "ijobs_task_id": "1446"
                                },
                                "ref_self": "/tasks/101",
                                tasks: [
                                    {
                                        "id": 102,
                                        "state": "SUCCESS",
                                        "task_class_name": "package.example.SomeProcess",
                                        "app_code": "qtrelease",
                                        "creator": "mattsu",
                                        "create_time": "2013-12-8 12:00:00 01.00",
                                        "complete_time": "2013-12-8 12:00:07.30",
                                        "app_data": {
                                            "ijobs_task_id": "1445"
                                        },
                                        "ref_self": "/tasks/102"
                                    }, {
                                        "id": 103,
                                        "state": "RUNNING",
                                        "task_class_name": "package.example.SomeProcess",
                                        "app_code": "qtrelease",
                                        "creator": "mattsu",
                                        "create_time": "2013-12-8 12:01:00.00",
                                        "complete_time": "2013-12-8 12:01:07.30",
                                        "app_data": {
                                            "ijobs_task_id": "1446"
                                        },
                                        "ref_self": "/tasks/103"
                                    }
                                ]
                            }
                        ]
                    }
        """
        pass