from django.db import models
from django.contrib.auth.models import AbstractUser
from django.apps import apps

# It's best to get the User model using this method to avoid circular imports,
# especially when extending the User model or using it across different applications.

def get_community_membership_model():
    """Retrieve the CommunityMembership model dynamically to avoid circular imports."""
    return apps.get_model('application', 'CommunityMembership')

# Create your models here.
class SportsHubUser(AbstractUser):
    def is_member(self, community_id):
        """
        Check if the user is a member of a given community by dynamically fetching the 
        CommunityMembership model and querying it.
        """
        CommunityMembership = get_community_membership_model()
        return CommunityMembership.objects.filter(community_id=community_id, user=self).exists()
