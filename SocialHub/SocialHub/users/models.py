from django.db import models
from django.contrib.auth.models import AbstractUser
from django.apps import apps

def get_community_membership_model():
#Retrieve the CommunityMembership model dynamically to avoid circular imports.
    return apps.get_model('application', 'CommunityMembership')

# Create your models here.
class SocialHubUser(AbstractUser):
    def is_member(self, community_id):
        CommunityMembership = get_community_membership_model()
        return CommunityMembership.objects.filter(community_id=community_id, user=self).exists()
    def get_communities(self):
        CommunityMembership = get_community_membership_model()
        return [membership.community for membership in CommunityMembership.objects.filter(user=self)]
    
    # FOLLOW
    following = models.ManyToManyField('self', related_name='followed_by', symmetrical=False, blank=True)

    def follow(self, user):
        if user != self:
            self.following.add(user)

    def unfollow(self, user):
        if user != self:
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(id=user.id).exists()
    
    def is_followed(self, user):
        return self.followed_by.filter(id=user.id).exists()

    def get_followers(self):
        return self.followed_by.all()
    
