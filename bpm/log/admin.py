from django.contrib import admin

from . import models


class RecordAdmin(admin.ModelAdmin):

    list_display = ('level', 'date_created', 'module', 'function', 'lineno', 'message', 'logger', 'revision')
    list_filter = ('logger', 'revision', 'level')


admin.site.register(models.Record, RecordAdmin)