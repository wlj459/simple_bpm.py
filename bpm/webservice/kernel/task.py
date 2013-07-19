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

                    {{ example_task|render:"{'id':101}" }}
        """
        pass


    @classmethod
    def dump_task(cls, task_model):
        task_resource = {
            "id": task_model.id,
            "state": task_model.state,
            "task_class_name": task_model.name,
            # "app_code": "qtrelease",
            # "creator": "mattsu",
            # "create_time": "2013-12-8 12:00:00 01.00",
            # "complete_time": "2013-12-8 12:00:07.30",
            # "app_data": {
            #     "ijobs_task_id": "1445"
            # },
            "ref_self": "/task/101/",
            "parent": task_model.id,
            "exec_kwargs": task_model.kwargs,
            "data": task_model.data,
            "ex_data": task_model.ex_data,
            "return_code": task_model.return_code,
        }
        return task_resource
