from django.contrib import admin
from .models import Community, CommunityMembership, Template, TemplateField
from django.contrib.auth.admin import UserAdmin

class CommunityMembershipInline(admin.TabularInline):
    model = CommunityMembership
    extra = 1
    autocomplete_fields = ['user']

class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'list_admins', 'list_moderators']
    inlines = [CommunityMembershipInline]

    def list_admins(self, obj):
        return ", ".join([user.username for user in obj.admin.all()])
    list_admins.short_description = 'Admins'

    def list_moderators(self, obj):
        return ", ".join([user.username for user in obj.moderator.all()])
    list_moderators.short_description = 'Moderators'

admin.site.register(Community, CommunityAdmin)

class TemplateFieldInline(admin.TabularInline):
    model = TemplateField
    extra = 1

class TemplateAdmin(admin.ModelAdmin):
    inlines = [TemplateFieldInline]

admin.site.register(Template, TemplateAdmin)