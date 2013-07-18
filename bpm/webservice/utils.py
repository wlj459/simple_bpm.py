from mako.template import Template

ACCEPT_V1 = 'application/vnd.bpm;v=1'
CT_V1 = 'application/vnd.bpm;v=1'


example_task="""
{
    "id": 101,
    "state": "RUNNING",
    "task_class_name": "package.example.SomeProcess",
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
"""

def generate_example_task(indention_levels=5):
    lines = []
    for line in example_task.splitlines():
        lines.append('    ' * indention_levels + line)
    return '\n'.join(lines)

def apimethod(func):
    func.__doc__ = Template(func.__doc__.decode('utf8'), output_encoding='utf8').render(
        generate_example_task=generate_example_task)
    return staticmethod(func)