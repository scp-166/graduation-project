from django.contrib import admin
from .models import *


@admin.register(TerminalCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name')


@admin.register(TerminalInfo)
class TerminalInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'terminal_category', 'terminal_id', 'terminal_name', 'status')


@admin.register(TerminalData)
class TerminalDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'terminal', 'data', 'create_time')

