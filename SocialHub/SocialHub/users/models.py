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
