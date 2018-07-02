from django.contrib import admin

# Register your models here.

from . import models

class FileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'note')

admin.site.register(models.file,FileAdmin)