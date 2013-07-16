# -*- coding: utf-8 -*-
class Tasks(object):
    """任务列表资源，代表某一类任务
    """
    def post(self):
        """
        .. http:post:: /tasks/(str:task_class_name)

            创建并执行任务，任务的定义由task_class_name对应的python类提供。暂时未实现定时和定期执行的功能。

            :param task_class_name: 任务定义的Python类名
            :type task_class_name: str
            :jsonparam exec_kwargs: 类型为dict。执行任务时使用的关键字参数（key=value形式），传递给Task.start方法
            :status 201: 创建任务成功。返回JSON类型，创建的任务资源
            :status 400: 创建任务的请求参数不是JSON或者exec_kwargs不是dict类型。返回字符串类型，错误消息
            :status 501: 执行的任务定义没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  POST /tasks/package.example.SomeProcess HTTP/1.1
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
                        "id": 17643,
                        "ref_self": "/tasks/17643"
                    }
        """
        pass

    def get(self):
        """
        .. http:get:: /tasks/(str:task_class_name)

            列出给定任务定义的所有任务实例。

            :param task_class_name: 任务定义的Python类名
            :type task_class_name: str
            :status 200: 获取任务列表成功。返回JSON类型，任务列表
            :status 501: 执行的任务定义没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  GET /tasks/package.example.SomeProcess HTTP/1.1
                  Accept: application/vnd.bpm;v=1

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 200 OK
                    Content-Type: application/vnd.bpm;v=1

                    {
                        "tasks": [
                            {
                                "id": 17643,
                                "state": "RUNNING",
                                "task_class_name": "package.example.SomeProcess",
                                "app_code": "qtrelease",
                                "creator": "mattsu",
                                "create_time": "2013-12-8 12:00:00 01.00",
                                "complete_time": "2013-12-8 12:00:07.30",
                                "app_data": {
                                    "ijobs_task_id": "1445"
                                },
                                "ref_self": "/tasks/17643"
                            }, {
                                "id": 17644,
                                "state": "RUNNING",
                                "task_class_name": "package.example.SomeProcess",
                                "app_code": "qtrelease",
                                "creator": "mattsu",
                                "create_time": "2013-12-8 12:01:00.00",
                                "complete_time": "2013-12-8 12:01:07.30",
                                "app_data": {
                                    "ijobs_task_id": "1446"
                                },
                                "ref_self": "/tasks/17644"
                            }
                        ],
                        "ref_self": "/tasks/package.example.SomeProcess/by-50-tasks-pages/103",
                        "ref_previous": "/tasks/package.example.SomeProcess/by-50-tasks-pages/102",
                        "form_create_task": {
                            "action": "/tasks/package.example.SomeProcess",
                            "method": "POST",
                            "body": {
                                "exec_kwargs": ""
                            }
                        }
                    }
        """
        pass