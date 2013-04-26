import json

from django.db import models, transaction

from . import signals, states, utils


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
        default=states.CREATED,
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

    def __unicode__(self):
        return self.name

    def appoint(self, to_state):
        if to_state in states.APPOINTMENT_STATES:
            return self.transit(to_state, appointment=True)

    def _callback(self, data='', ex_data='', return_code=0):
        if self.state == states.BLOCKED:
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

    def start(self, *args, **kwargs):
        if self.state == states.CREATED:
            self.transit(states.PENDING,
                         args=json.dumps(args),
                         kwargs=json.dumps(kwargs))

    def _transit(self, to_state, **kwargs):
        appointment_flag = 0
        if self.appointment:
            if states.can_transit(self.state, self.appointment):
                appointment_flag = 1
                if states.State(to_state) < states.State(self.appointment):
                    appointment_flag = 2
                    to_state = self.appointment

        if states.can_transit(self.state, to_state):
            kwargs = kwargs.update({
                'check_code': utils.generate_salt(),
                'state': to_state,
            })
            if appointment_flag:
                kwargs['appointment'] = ''

            rows = self.__class__.objects.filter(pk=self.pk,
                                                 check_code=self.check_code)\
                                         .update(**kwargs)

            if rows:
                _signal = getattr(signals, 'task_' + to_state.lower())

                if _signal:
                    _signal.send(sender=self.__class__, task_id=self.id)

                if appointment_flag != 2:
                    return True

        return False

    def transit(self, to_state, appointment=False, **kwargs):
        if appointment:
            rows = self.__class__.objects.filter(pk=self.pk,
                                                 check_code=self.check_code)\
                                         .update(appointment=to_state)

            return True if rows else False
        else:
            return self._transit(to_state, **kwargs)
