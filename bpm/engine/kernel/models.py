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

    _archive = models.TextField()
    _ack = models.PositiveSmallIntegerField(
        default=0,
    )
    _token = models.SlugField(
        max_length=6,
        default=utils.generate_salt(),
    )
    _ttl = models.PositiveSmallIntegerField(
        default=0,
    )

    def __unicode__(self):
        return self.name

    def appoint(self, to_state):
        if to_state in states.APPOINTMENT_STATES:
            rows = self.__class__.objects.filter(pk=self.pk,
                                                 _token=self._token)\
                                         .update(appointment=to_state)

            if rows:
                self.transit(to_state)

    @transaction.commit_on_success()
    def _callback(self, return_code=0, data='', ex_data=''):
        if self.state == states.BLOCKED:
            kwargs = {}
            to_state = states.FAILURE

            if return_code:
                kwargs['data'] = json.dumps(return_code)
                kwargs['ex_data'] = json.dumps(ex_data)
            else:
                kwargs['data'] = json.dumps(data)
                to_state = states.SUCCESS

            rows = self.__class__.objects.filter(pk=self.pk,
                                                 _token=self._token)\
                                         .update(**kwargs)

            if rows:
                self.transit(to_state)

    def callback(self, data):
        self._callback(data=data)

    def errback(self, ex_data, return_code=1):
        assert return_code == 0
        self._callback(return_code=return_code, ex_data=ex_data)

    @transaction.commit_on_success()
    def start(self, *args, **kwargs):
        if self.state == states.CREATED:
            rows = self.__class__.objects.filter(pk=self.pk,
                                                 _token=self._token)\
                                         .update(args=json.dumps(args),
                                                 kwargs=json.dumps(kwargs))

            if rows:
                self.transit(states.PENDING)

    def transit(self, to_state):
        appointment_flag = False
        if self.appointment:
            if states.can_transit(self.state, self.appointment):
                appointment_flag = True
                if states.State(to_state) < states.State(self.appointment):
                    to_state = self.appointment

        if states.can_transit(self.state, to_state):
            kwargs = {
                '_token': utils.generate_salt(),
                'state': to_state,
            }
            if appointment_flag:
                kwargs['appointment'] = ''

            rows = self.__class__.objects.filter(pk=self.pk,
                                                 _token=self._token)\
                                         .update(**kwargs)

            state_change_signal = getattr(signals, 'task_' + to_state.lower())
            if rows and state_change_signal:
                instance = self.__class__.objects.get(pk=self.pk)
                state_change_signal.send(sender=self.__class__, instance=instance)

                if not appointment_flag:
                    return instance
