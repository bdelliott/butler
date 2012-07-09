from django.contrib import admin
from sync.models import Show, SyncJob

class SyncJobAdmin(admin.ModelAdmin):
    list_display = ['start', 'end']

admin.site.register(SyncJob, SyncJobAdmin)
admin.site.register(Show)
