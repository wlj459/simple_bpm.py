# -*- coding: utf-8 -*-
class Completions(object):
    """
    结束任务的请求
    """
    def post(self):
        """
        .. http:post:: /tasks/(int:task_id)/completions

            创建对给定id的任务的结束的请求。任务的on_schedule会被执行。
            仅适用于Component，相当于把Component从BLOCKED状态转换到READY状态。人工触发on_schedule。

            :param task_id: 任务的id
            :type task_id: int
            :jsonparam return_code: 如果大于0，任务被认为是失败的任务
            :jsonparam data: 任务的返回值，返回给read()的调用者
            :jsonparam ex_data: 任务的其他返回值，用于调试
            :status 201: 结束的请求下达成功。返回JSON类型，任务详情
            :status 412: 任务处于不可结束状态。返回字符串类型，错误消息
            :status 404: 给定id的任务没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  POST /task/101/completions HTTP/1.1
                  Accept: application/vnd.bpm;v=1

                  {
                    return_code: 0,
                    data: "my_return_value",
                    ex_data: ""
                  }

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 201 CREATED
                    Content-Type: application/vnd.bpm;v=1

                    {
                        "id": 101,
                        "state": "BLOCKED",
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