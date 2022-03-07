from django.contrib import admin

from .models import Post

# Register your models here.

# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     list_display = ("user", "title", "category_name")
#     empty_value_display = '-empty-'

#     def category_name(self, ins):
#         return ins.category.name