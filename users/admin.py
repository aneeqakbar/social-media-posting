from django.contrib import admin
from .models import Profile, SocialAccount, SocialLongLivedToken

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    empty_value_display = '-empty-'

@admin.register(SocialLongLivedToken)
class SocialLongLivedTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "backend", "get_token", "created_at")
    empty_value_display = '-empty-'

    def get_token(self, ins):
        return f"{ins.token[:50]}..."
    get_token.short_description = "Token"

    def get_backend(self, ins):
        return ins.get_backend_display

@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "backend", "name", "created_at")
    empty_value_display = '-empty-'

    def get_backend(self, ins):
        return ins.get_backend_display