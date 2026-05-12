"""Result Task Admin interface."""

import re

from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


def _decode_unicode_escapes(value):
    """Convert \\uXXXX escape sequences to actual Unicode characters for display."""
    if not isinstance(value, str):
        return value

    def replace_unescape(m):
        return chr(int(m.group(1), 16))

    return re.sub(r'\\u([0-9a-fA-F]{4})', replace_unescape, value)


try:
    ALLOW_EDITS = settings.DJANGO_CELERY_RESULTS['ALLOW_EDITS']
except (AttributeError, KeyError):
    ALLOW_EDITS = False
    pass

from .models import GroupResult, TaskResult


class TaskResultAdmin(admin.ModelAdmin):
    """Admin-interface for results of tasks."""

    model = TaskResult
    date_hierarchy = 'date_done'
    list_display = ('task_id', 'periodic_task_name', 'task_name', 'date_done',
                    'status', 'worker')
    list_filter = ('status', 'date_done', 'periodic_task_name', 'task_name',
                   'worker')
    readonly_fields = ('date_created', 'date_started', 'date_done',
                       'display_result', 'meta')
    search_fields = ('task_name', 'task_id', 'status', 'task_args',
                     'task_kwargs')
    fieldsets = (
        (None, {
            'fields': (
                'task_id',
                'task_name',
                'periodic_task_name',
                'status',
                'worker',
                'content_type',
                'content_encoding',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Parameters'), {
            'fields': (
                'display_task_args',
                'display_task_kwargs',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Result'), {
            'fields': (
                'display_result',
                'date_created',
                'date_started',
                'date_done',
                'traceback',
                'meta',
            ),
            'classes': ('extrapretty', 'wide')
        }),
    )

    def display_task_args(self, obj):
        return _decode_unicode_escapes(obj.task_args)
    display_task_args.short_description = _('Task Positional Arguments')

    def display_task_kwargs(self, obj):
        return _decode_unicode_escapes(obj.task_kwargs)
    display_task_kwargs.short_description = _('Task Named Arguments')

    def display_result(self, obj):
        return _decode_unicode_escapes(obj.result)
    display_result.short_description = _('Result Data')

    def get_readonly_fields(self, request, obj=None):
        if ALLOW_EDITS:
            return self.readonly_fields
        else:
            return list({
                field.name for field in self.model._meta.fields
            } | {'display_task_args', 'display_task_kwargs', 'display_result'})


admin.site.register(TaskResult, TaskResultAdmin)


class GroupResultAdmin(admin.ModelAdmin):
    """Admin-interface for results  of grouped tasks."""

    model = GroupResult
    date_hierarchy = 'date_done'
    list_display = ('group_id', 'date_done')
    list_filter = ('date_done',)
    readonly_fields = ('date_created', 'date_done', 'result')
    search_fields = ('group_id',)


admin.site.register(GroupResult, GroupResultAdmin)
