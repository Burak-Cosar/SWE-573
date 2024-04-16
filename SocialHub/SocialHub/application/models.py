from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    admin = models.ManyToManyField(User, related_name='administered_communities')
    moderator = models.ManyToManyField(User, related_name='moderated_communities')
    members = models.ManyToManyField(User, through='CommunityMembership', related_name='application_communities')

    def is_member(self, user):
        return self.members.filter(id=user.id).exists()

    def __str__(self):
        return self.name

class CommunityMembership(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='application_community_memberships')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.community.name}"
