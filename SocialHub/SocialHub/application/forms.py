from django import forms
from django.forms import ModelForm, formset_factory
from .models import Community, Template, Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class CommunityForm(ModelForm):
    class Meta:
        model = Community
        fields = ('name', 'description', 'isPrivate')

        labels = {
            'name': 'Community Name',
            'description': 'Community Description',
            'isPrivate': "Private",
            }
        
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Community Name'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Describe Your Community'}),
            'isPrivate': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

class TemplateForm(forms.Form):
    post_title = forms.CharField(max_length=255, label="Post Title")
    post_description = forms.CharField(widget=forms.Textarea, label="Post Description")

    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop('extra', 0)
        super(TemplateForm, self).__init__(*args, **kwargs)

        for i in range(int(extra_fields)):
            self.fields[f'custom_field_{i}'] = forms.CharField()
            self.fields[f'custom_type_{i}'] = forms.ChoiceField(choices=[
                ('text', 'Text'),
                ('textArea', 'Text Area'),
                ('number', 'Number'),
                ('float', 'Float'),
                ('date', 'Date'),
                ('time', 'Time'),
                ('image', 'Image'),
                ('color', 'Color Picker'),  
                ('url', 'URL'),  
                ('email', 'Email'),  
                ('phone', 'Phone Number'),  
                ('geolocation', 'Geolocation')
            ])

class DynamicPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title']  # Default field included in all posts
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
        }

    def __init__(self, *args, **kwargs):
        template_fields = kwargs.pop('template_fields', [])  # Extract template_fields from kwargs
        super().__init__(*args, **kwargs)

        # Adding dynamic fields based on the template_fields
        for field in template_fields:
            field_name = field['field_name']
            field_type = field['field_type']
            if field_type == 'text':
                self.fields[field_name] = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter text'}))
            elif field_type == 'textArea':
                self.fields[field_name] = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write here'}))
            elif field_type == 'number':
                self.fields[field_name] = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter number'}))
            elif field_type == 'float':
                self.fields[field_name] = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter number'}))
            elif field_type == 'date':
                self.fields[field_name] = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
            elif field_type == 'time':
                self.fields[field_name] = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
            elif field_type == 'image':
                self.fields[field_name] = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file', 'type': 'file'}))
            elif field_type == 'color':
                self.fields[field_name] = forms.CharField(widget=forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}))
            elif field_type == 'url':
                self.fields[field_name] = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter URL'}))
            elif field_type == 'email':
                self.fields[field_name] = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}))
            elif field_type == 'phone':
                self.fields[field_name] = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}))
            elif field_type == 'geolocation':
                self.fields[field_name + '_latitude'] = forms.DecimalField(
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude'}), 
                    max_digits=9, 
                    decimal_places=6
                )
                self.fields[field_name + '_longitude'] = forms.DecimalField(
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude'}), 
                    max_digits=9, 
                    decimal_places=6
                )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

        labels = {
            'content': 'New Comment',
            }

        widgets = {
            'content': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Write a comment'}),
        }

class InviteForm(forms.ModelForm):
    invited = forms.ModelMultipleChoiceField(queryset=None, widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    class Meta:
        model = Community
        fields = ['invited']
        labels = {'invited': ''}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invited'].queryset = User.objects.all()
        self.fields['invited'].label = 'Select the users to invite to this private community' 