from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField


User = get_user_model()

class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    admin = models.ManyToManyField(User, related_name='administered_communities')
    moderator = models.ManyToManyField(User, related_name='moderated_communities')
    members = models.ManyToManyField(User, through='CommunityMembership', related_name='members')

    def is_member(self, user):
        return self.members.filter(id=user.id).exists()

    def __str__(self):
        return self.name

class CommunityMembership(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_memberships')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.community.name}"

class Template(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='templates', null=True)

    def __str__(self):
        return self.title

class TemplateField(models.Model):
    community = models.ForeignKey(Community, related_name='community_template_fields', on_delete=models.CASCADE, null=True)
    template = models.ForeignKey(Template, related_name='fields', on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.field_name} ({self.field_type})"

class Post(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    title = models.CharField(max_length=255)
    description = models.TextField()
    data = models.JSONField(default=dict)  # JSON to store dynamic field stuff
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    

