import json

from django import forms

from ..models import Task


class AddTaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['name', 'args', 'kwargs']

    def clean_kwargs(self):
        print 'clean_kwargs'
        return self.cleaned_data['kwargs']