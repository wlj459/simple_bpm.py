import json

from django.db import models

from . import signals, states


class Definition(models.Model):

    name = models.SlugField(
        max_length=100,
    )
    category = models.PositiveSmallIntegerField(
        choices=(
            (0, 'PROCESS'),
            (1, 'COMPONENT'),
        )
    )
    content = models.TextField()

    def __unicode__(self):
        return self.name


class Task(models.Model):

    name = models.CharField(
        max_length=100,
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        related_name='sub_tasks',
    )
    ttl = models.PositiveSmallIntegerField(
        default=0,
    )
    # inputs and outputs
    args = models.TextField()
    kwargs = models.TextField()
    data = models.TextField()
    ex_data = models.TextField()
    state = models.PositiveSmallIntegerField(
        choices=tuple(states.x.iteritems()),
        default=states.PENDING,
    )
    is_locked = models.BooleanField(
        default=False,
    )
    archive = models.TextField()

    def __unicode__(self):
        return self.definition.name

    def callback(self, data):
        signals.pre_callback.send(sender=self.__class__, instance=self)

        self.__class__.objects.filter(id=self.id, state=states.STARTED)\
                              .update(state=states.SUCCESS,
                                      data=json.dumps(data))

        # Signal that the callback is complete
        signals.post_callback.send(sender=self.__class__, instance=self)

    def errback(self, ex_data):
        signals.pre_errback.send(sender=self.__class__, instance=self)

        self.__class__.objects.filter(id=self.id, state=states.STARTED)\
                              .update(state=states.FAILURE,
                                      ex_data=json.dumps(ex_data))

        # Signal that the errback is complete
        signals.post_errback.send(sender=self.__class__, instance=self)
