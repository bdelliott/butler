from django.contrib import admin
from sync.models import LibraryItem, Show, SyncJob, WishKeyword

class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ['show', 'downloaded', 'decoded', 'h264', 'hinted']

class ShowAdmin(admin.ModelAdmin):
    list_display = ['date', 'title', 'duration', 'size']
    ordering = ['date', 'title']

class SyncJobAdmin(admin.ModelAdmin):
    list_display = ['start', 'end']

class WishKeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword1', 'keyword2', 'keyword3']

admin.site.register(LibraryItem, LibraryItemAdmin)
admin.site.register(Show, ShowAdmin)
admin.site.register(SyncJob, SyncJobAdmin)
admin.site.register(WishKeyword, WishKeywordAdmin)
