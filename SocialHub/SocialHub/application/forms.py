from django import forms
from django.forms import ModelForm
from .models import Community

class CommunityForm(ModelForm):
    class Meta:
        model = Community
        fields = ('name', 'description')

        labels = {
            'name': 'Community Name',
            'description': 'Community Description',
            }
        
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Community Name'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Describe Your Community'}),
        }