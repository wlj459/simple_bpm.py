from django.contrib import admin

from bpm.kernel import models


class TaskAdmin(admin.ModelAdmin):

    list_display = ('__unicode__', 'parent', 'state')
    list_filter = ('state',)


admin.site.register(models.Task, TaskAdmin)