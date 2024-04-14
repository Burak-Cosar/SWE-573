from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SportsHubUser

class SportsHubUserAdmin(UserAdmin):
    model = SportsHubUser
    fieldsets = UserAdmin.fieldsets
    list_display = ['username', 'email']
    search_fields = ['username', 'email']

admin.site.register(SportsHubUser, SportsHubUserAdmin)