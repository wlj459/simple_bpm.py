import json

import requests
import requests.packages.urllib3.util


__all__ = ['list_tasks', 'create_task']


def list_tasks(task_class_name):
    url = make_url_absolute('/tasks/%s' % task_class_name)
    response = requests.get(url)
    return json.loads(response.content)['tasks']


def create_task(task_class_name, **exec_kwargs):
    url = make_url_absolute('/tasks/%s' % task_class_name)
    response = requests.get(url)
    form_create_task = json.loads(response.content)['form_create_task']
    http_call = getattr(requests, form_create_task['method'].lower())
    body = form_create_task['body']
    body['exec_kwargs'] = exec_kwargs
    url = make_url_absolute(form_create_task['action'])
    response = http_call(url, json.dumps(body))
    return json.loads(response.content)


def make_url_absolute(url):
    scheme, auth, host, port, path, query, fragment = requests.packages.urllib3.util.parse_url(url)
    if not scheme:
        return 'http://127.0.0.1:8000%s' % url
    else:
        return url