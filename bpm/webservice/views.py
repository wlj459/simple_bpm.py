# coding=utf-8

from django.http import HttpResponse
from django.views.decorators.http import require_GET, \
                                         require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from bpm.kernel.models import Task
from bpm.webservice.kernel.transitions import TransitionsToReady
from bpm.webservice.kernel.tasks import TasksResource
from bpm.webservice.utils import CT_V1
import httplib


@require_POST
@csrf_exempt
def transitions_to_ready(request, task_id):
    try:
        task_model = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return HttpResponse('Task not found by id(%s)' % task_id, CT_V1, 404)
    else:
        return TransitionsToReady.post(request, task_model)

@csrf_exempt
def handle_tasks_resource(request, task_class_name):
    if 'GET' == request.method:
        return TasksResource.get(task_class_name)
    elif 'POST' == request.method:
        return TasksResource.post(task_class_name, request.POST.get('exec_kwargs'))
    else:
        return HttpResponse(status_code=httplib.METHOD_NOT_ALLOWED)

