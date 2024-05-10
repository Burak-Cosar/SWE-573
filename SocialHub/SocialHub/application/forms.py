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

# DEFAULT TEMPLATE FORM
class PostForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['title', 'description']

        labels = {
            'title': 'Post Title',
            'description': 'What Would You Like to Say?',
            }

        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Post Title'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'What Would You Like to Say?'}),
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
                ('number', 'Number'),
                ('date', 'Date'),
            ])

class DynamicPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description']  # DEFAULT FOR ALL

    def __init__(self, *args, **kwargs):
        template_fields = kwargs.pop('template_fields', [])  # Extract template_fields from kwargs
        super().__init__(*args, **kwargs)

        # DYNAMIC FIELDZ
        for field in template_fields:
            field_name = field['field_name']
            field_type = field['field_type']
            if field_type == 'text':
                self.fields[field_name] = forms.CharField(max_length=255)
            elif field_type == 'number':
                self.fields[field_name] = forms.IntegerField()
            elif field_type == 'date':
                self.fields[field_name] = forms.DateField()

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
        labels = {'invited': 'Invite Users'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invited'].queryset = User.objects.all()