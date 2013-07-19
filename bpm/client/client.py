import json

import requests


__all__ = ['list_tasks']


def list_tasks(task_class_name):
    url = 'http://127.0.0.1:8000/tasks/%s' % task_class_name
    response = requests.get(url)
    return json.loads(response.content)