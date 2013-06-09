import celery

from .models import Record


@celery.task(ignore_result=True)
def log(created, name, revision, level, module, lineno, function, message):
    Record.objects.create(
        logger=name,
        revision=revision,
        level=level,
        date_created=created,
        module=module,
        lineno=lineno,
        function=function,
        message=message
    )
