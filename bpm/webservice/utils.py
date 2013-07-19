from django.template import Template
from django.template import Context
from django.template import Library
from django.template import builtins
from django.utils.safestring import mark_safe
import json

register = Library()
builtins.append(register)

ACCEPT_V1 = 'application/vnd.bpm;v=1'
CT_V1 = 'application/vnd.bpm;v=1'

example_task = """{
    "id": {{ id }},
    "state": "{{ state|default:'RUNNING' }}",
    "appointment": "{{ appointment }}",
    "task_class_name": "package.example.SomeProcess",
    # "app_code": "qtrelease",
    # "creator": "mattsu",
    # "create_time": "2013-12-8 12:00:00 01.00",
    # "complete_time": "2013-12-8 12:00:07.30",
    # "app_data": {
    #     "ijobs_task_id": "1445"
    # },
    "ref_self": "/task/{{ id }}/",
    "parent": t_instance.id,
    "exec_kwargs": t_instance.kwargs,
    "data": t_instance.data,
    "ex_data": t_instance.ex_data,
    "return_code": t_instance.return_code,
}
"""


@register.filter
def render(text, kwargs):
    kwargs = eval(kwargs)
    indention_level = kwargs.pop('indention_level', 5)
    text = Template(text).render(Context(kwargs))
    lines = []
    for i, line in enumerate(text.splitlines()):
        if i > 0:
            lines.append('    ' * indention_level + line)
        else:
            lines.append(line) # first line already indented
    return mark_safe('\n'.join(lines))


def render_doc(func):
    func.__doc__ = Template(func.__doc__).render(Context(dict(example_task=example_task)))
    return func