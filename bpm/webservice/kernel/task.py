# -*- coding: utf-8 -*-

import json
from bpm.webservice.utils import render_doc

class TaskResource(object):
    """任务资源，代表一个任务（也是一次执行）
    """
    @classmethod
    @render_doc
    def get(cls):
        """
        .. http:get:: /task/(int:task_id)

            列出给定id的任务的详情。

            :param task_id: 任务的id
            :type task_id: int
            :status 200: 获取任务详情成功。返回JSON类型，任务详情
            :status 404: 给定id的任务没有找到。返回字符串类型，错误消息
            :status 500: 其他错误。返回字符串类型，错误消息

            **请求的例子**:

               .. sourcecode:: http

                  GET /task/101 HTTP/1.1
                  Accept: application/vnd.bpm;v=1

            **响应的例子**:

                .. sourcecode:: http

                    HTTP/1.1 200 OK
                    Content-Type: application/vnd.bpm;v=1

                    {{ example_task|indent }}
        """
        pass


    @classmethod
    def output(cls, t_instance):
        task_info = {
            "id": t_instance.id,
            "state": t_instance.state,
            "task_class_name": t_instance.name,
            # "app_code": "qtrelease",
            # "creator": "mattsu",
            # "create_time": "2013-12-8 12:00:00 01.00",
            # "complete_time": "2013-12-8 12:00:07.30",
            # "app_data": {
            #     "ijobs_task_id": "1445"
            # },
            "ref_self": "/task/101/",
            "parent": t_instance.id,
            "exec_kwargs": t_instance.kwargs,
            "data": t_instance.data,
            "ex_data": t_instance.ex_data,
            "return_code": t_instance.return_code,
        }
        return json.dumps(task_info)
