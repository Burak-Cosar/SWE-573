from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SocialHubUser

class SocialHubUserAdmin(UserAdmin):
    model = SocialHubUser
    fieldsets = UserAdmin.fieldsets
    list_display = ['username', 'email']
    search_fields = ['username', 'email']

admin.site.register(SocialHubUser, SocialHubUserAdmin)