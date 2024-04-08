from django import forms
from django.forms import ModelForm
from .models import Venue, Event

#Create a venue form
class VenueForm(ModelForm):
    class Meta:
        model = Venue
        fields = ('name','address','zip_code','phone', 'web','email_address')

        labels = {
            'name': '',
            'address': '',
            'zip_code': '',
            'phone': '',
            'web': '',
            'email_address': '',
        } 

        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Venue Name'}),
            'address': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter Address'}),
            'zip_code': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Zipcode'}),
            'phone': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Phone Number'}),
            'web': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Website'}),
            'email_address': forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email Address'}),
        }

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ('name','event_date','venue','manager','description','attendees')

        labels = {
            'name':'',
            'event_date':'YYYY-MM-DD HH:MM:SS',
            'venue':'',
            'manager':'',
            'description':'',
            'attendees':'',
        }

        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name'}),
            'event_date': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Event Date'}),
            'venue': forms.Select(attrs={'class':'form-control', 'placeholder':'Venue'}),
            'manager': forms.Select(attrs={'class':'form-control', 'placeholder':'Manager'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Description'}),
            'attendees': forms.SelectMultiple(attrs={'class':'form-control', 'placeholder':'Attendees'}),
        }