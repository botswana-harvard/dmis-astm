from django.contrib import admin

from .models import History


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):

    date_hierarchy = 'read_datetime'

    list_display = ('start_read_id', 'end_read_id', 'read_datetime', 'target', 'read_model', 'comment')
    list_filter = ('read_datetime', 'target', 'read_model')
