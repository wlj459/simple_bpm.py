# -*- coding: utf-8 -*-

import json

from django.db import models, transaction

from . import signals, states, utils


class Deploy(models.Model):

    name = models.CharField(
        max_length=255,
    )
    text = models.TextField()

    def __unicode__(self):
        return unicode("[#%d] %s" % (
            self.id,
            self.name
        ))


class Definition(models.Model):

    module = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    name = models.SlugField(
        max_length=100,
    )
    category = models.PositiveSmallIntegerField(
        choices=(
            (0, 'PROCESS'),
            (1, 'COMPONENT'),
        )
    )
    deploy = models.ForeignKey(Deploy)

    class Meta:
        unique_together = ('module', 'name')

    def __unicode__(self):
        return unicode("%s.%s" % (
            self.module,
            self.name,
        ))


class TaskManager(models.Manager):

    def transit(self, instance, to_state, **kwargs):
        assert isinstance(instance, self.model)

        appointment_flag = 0  # 没有处理预约
        if instance.appointment:
            if states.can_transit(instance.state, instance.appointment):
                appointment_flag = 1  # 处理了预约但未设置为预约状态
                if states.State(to_state) < states.State(instance.appointment):
                    appointment_flag = 2  # 设置为预约状态
                    to_state = instance.appointment

        if states.can_transit(instance.state, to_state):
            kwargs.update({
                'check_code': utils.generate_salt(),
                'state': to_state,
            })
            if appointment_flag:  # 一旦处理了预约，就将其置空
                kwargs['appointment'] = ''
            if to_state in states.ARCHIVE_STATES:
                kwargs['archive'] = ''

            rows = self.model.objects.filter(
                pk=instance.pk,
                check_code=instance.check_code
            ).update(**kwargs)

            if rows:
                for k, v in kwargs.iteritems():
                    setattr(instance, k, v)

                state_change_signal = getattr(signals,
                                              'task_' + to_state.lower())

                if state_change_signal:
                    state_change_signal.send(sender=instance.__class__,
                                             instance=instance)

                if appointment_flag != 2:
                    return True

        return False


class Task(models.Model):

    name = models.CharField(
        max_length=100,
    )
    parent = models.ForeignKey(
        'self',
        related_name='sub_tasks',
        null=True,
        blank=True,
    )

    # inputs and outputs
    args = models.TextField()
    kwargs = models.TextField()
    data = models.TextField()
    ex_data = models.TextField()

    state = models.CharField(
        max_length=16,
        choices=zip(states.ALL_STATES, states.ALL_STATES),
        default=states.PENDING,
    )
    appointment = models.CharField(
        max_length=16,
        choices=zip(states.APPOINTMENT_STATES, states.APPOINTMENT_STATES),
        default='',
        blank=True,
    )

    identifier_code = models.SlugField(
        max_length=6,
    )
    token_code = models.SlugField(
        max_length=6,
    )
    archive = models.TextField()
    ack = models.PositiveSmallIntegerField(
        default=0,
    )
    check_code = models.SlugField(
        max_length=6,
        default=utils.generate_salt(),
    )
    ttl = models.PositiveSmallIntegerField(
        default=0,
    )

    objects = TaskManager()

    def __unicode__(self):
        return unicode("[#%d] %s" % (
            self.id,
            self.name
        ))

    def appoint(self, to_state):
        if to_state in states.APPOINTMENT_STATES:
            return self.transit(to_state, appointment=True)

    def _callback(self, data='', ex_data='', return_code=0):
        if self.state == states.RUNNING:
            kwargs = {}
            to_state = states.FAILURE

            if return_code:
                kwargs['data'] = json.dumps(return_code)
                kwargs['ex_data'] = json.dumps(ex_data)
            else:
                kwargs['data'] = json.dumps(data)
                to_state = states.SUCCESS

            self.transit(to_state, **kwargs)

    def callback(self, data):
        self._callback(data=data)

    def errback(self, ex_data, return_code=1):
        assert return_code != 0
        self._callback(ex_data=ex_data, return_code=return_code)

    def transit(self, to_state, appointment=False, **kwargs):
        if appointment:
            rows = self.__class__.objects.filter(pk=self.pk,
                                                 check_code=self.check_code)\
                                         .update(appointment=to_state)

            return True if rows else False
        else:
            return self.__class__.objects.transit(self, to_state, **kwargs)

    def transit_lazy(self, to_state, countdown=10):
        signals.lazy_transit.send(sender=self.__class__,
                                  task_id=self.pk,
                                  to_state=to_state,
                                  countdown=countdown)
