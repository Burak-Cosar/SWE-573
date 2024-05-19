from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django.core.exceptions import PermissionDenied

User = get_user_model()

class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    admin = models.ManyToManyField(User, related_name='administered_communities')
    moderator = models.ManyToManyField(User, related_name='moderated_communities')
    invited = models.ManyToManyField(User, related_name='invited_communities')
    members = models.ManyToManyField(User, through='CommunityMembership', related_name='members')
    isPrivate = models.BooleanField(blank=True, null=True)

    def is_member(self, user):
        return self.members.filter(id=user.id).exists()
    
    def make_moderator(self, user):
        self.moderator.add(user)

    def remove_moderator(self, user):
        self.moderator.remove(user)

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
    template = models.ForeignKey(Template, related_name='fields', on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.field_name} ({self.field_type})"

class Post(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    data = models.JSONField(default=dict)  # JSON to store dynamic field stuff
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def delete(self, user, *args, **kwargs):
        if self.created_by == user or user == self.community.admin:
            super().delete(*args, **kwargs)
        else:
            raise PermissionDenied("You do not have permission to delete this post.")

    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'
    

