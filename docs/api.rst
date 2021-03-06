API手册
=======

bpm.py 以 HTTP GET/POST 的形式（所谓Restful）提供API给App开发者调用，以控制后台任务的起停等。

* 创建任务 :py:meth:`~bpm.webservice.kernel.tasks.Tasks.post` /tasks/(str:task_class_name)
* 任务列表 :py:meth:`~bpm.webservice.kernel.tasks.Tasks.get` /tasks/(str:task_class_name)
* 任务详情 :py:meth:`~bpm.webservice.kernel.task.Task.get` /task/(int:task_id)
* 撤销任务 :py:meth:`~bpm.webservice.kernel.appointments.AppointmentsToRevoked.post` /task/(int:task_id)/appointments/to-revoked
* 暂停任务 :py:meth:`~bpm.webservice.kernel.appointments.AppointmentsToSuspended.post` /task/(int:task_id)/appointments/to-suspended
* 继续执行 :py:meth:`~bpm.webservice.kernel.transitions.TransitionsToReady.post` /task/(int:task_id)/transitions/to-ready
* 重试列表 :py:meth:`~bpm.webservice.kernel.tries.Tries.get` /task/(int:task_id)/tries
* 重试任务 :py:meth:`~bpm.webservice.kernel.tries.Tries.post` /task/(int:task_id)/tries
* 执行轨迹 :py:meth:`~bpm.webservice.kernel.trace.Trace.get` /task/(int:task_id)/trace

.. automodule:: bpm.webservice.kernel.tasks
   :members:

.. automodule:: bpm.webservice.kernel.task
   :members:

.. automodule:: bpm.webservice.kernel.appointments
   :members:

.. automodule:: bpm.webservice.kernel.transitions
   :members:

.. automodule:: bpm.webservice.kernel.tries
   :members:

.. automodule:: bpm.webservice.kernel.trace
   :members: