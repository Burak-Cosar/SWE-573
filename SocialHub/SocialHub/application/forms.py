from django import forms
from django.forms import ModelForm, formset_factory
from .models import Community, Template, Post

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