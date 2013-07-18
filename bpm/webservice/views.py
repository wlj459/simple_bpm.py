# coding=utf-8

from django.http import HttpResponse
from django.views.decorators.http import require_GET, \
                                         require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from bpm.webservice.kernel.transitions import TransitionsToReady
from bpm.kernel


@require_POST
@csrf_exempt
def transitions_to_ready(request, task_id):

    return TransitionsToReady.post(request, task_id)
