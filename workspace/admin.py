from csv import list_dialects
from django.contrib import admin

from workspace.models import Category, DayName, Post, SchedulePost

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("user", "name")
    empty_value_display = '-empty-'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name")


@admin.register(SchedulePost)
class SchedulePostAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "day",
        "category",
        "time",
    )

# admin.site.register(DayName)
