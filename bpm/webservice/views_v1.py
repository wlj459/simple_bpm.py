# coding=utf-8

import httplib
import json
from django.http import HttpResponse
from django.views.decorators.http import require_GET, \
                                         require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from bpm.kernel.models import Task
from bpm.webservice.kernel.transitions import TransitionsToReady
from bpm.webservice.kernel.tasks import TasksResource
from bpm.webservice.kernel.task import TaskResource
from bpm.webservice.kernel.appointments import AppointmentsToRevoked, AppointmentsToSuspended
from bpm.webservice.kernel.tries import Tries
from bpm.webservice.utils import CT_V1


@require_http_methods(['GET', "POST"])
@csrf_exempt
def handle_tasks_resource(request, task_class_name):
    if 'GET' == request.method:
        return TasksResource.get(task_class_name)
    elif 'POST' == request.method:
        return TasksResource.post(task_class_name,
                                  json.loads(request.POST.get('exec_args', '[]')),
                                  json.loads(request.POST.get('exec_kwargs', '{}')))


@require_GET
def handle_task_resource(request, task_id):
    try:
        task_model = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return HttpResponse('Task not found by id(%s)' % task_id, CT_V1, httplib.NOT_FOUND)
    else:
        return HttpResponse(json.dumps(TaskResource.dump_task(task_model)),
                            CT_V1, httplib.OK)


@require_POST
@csrf_exempt
def handle_trans_resrc_to_ready(request, task_id):
    '''TransitionsToReady Resource'''
    try:
        task_model = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return HttpResponse('Task not found by id(%s)' % task_id, CT_V1, httplib.NOT_FOUND)
    else:
        return TransitionsToReady.post(request, task_model)


@require_POST
@csrf_exempt
def handle_appt_resrc_to_revoked(request, task_id):
    ''''''
    try:
        task_model = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return HttpResponse('Task not found by id(%s)' % task_id, CT_V1, httplib.NOT_FOUND)
    else:
        return AppointmentsToRevoked.post(request, task_model)


@require_POST
@csrf_exempt
def handle_appt_resrc_to_suspended(request, task_id):
    try:
        task_model = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return HttpResponse('Task not found by id(%s)' % task_id, CT_V1, httplib.NOT_FOUND)
    else:
        return AppointmentsToSuspended.post(request, task_model)


# @require_http_methods(['GET', "POST"]) # TODO: support GET
@require_POST
@csrf_exempt
def handle_tries_resrc(request, task_id):
    '''Tries Resource'''
    try:
        task_model = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return HttpResponse('Task not found by id(%s)' % task_id, CT_V1, httplib.NOT_FOUND)
    else:
        if 'GET' == request.method:
            return Tries.get(task_model)
        elif 'POST' == request.method:
            return Tries.post(task_model)
        
