from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django import forms
from .models import Community, CommunityMembership, Template, TemplateField, Post
from .forms import CommunityForm, TemplateForm, DynamicPostForm
from django.http import HttpResponse


User = get_user_model()

def home(request):
    return render(request, 'home.html', {})

# PLACEHOLDING FOR NOW
def search(request):
    if request.method == "POST":
        searched = request.POST['searched'] 
        items = all.objects.filter(name__contains = searched)
        
        return render(request, 'search.html', {'searched': searched, 'items':items})
    else:
        return render(request, 'search.html', {})

# COMMUNITY VIEWS BELOW    
@login_required
def create_community(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.save()
            community.admin.add(request.user)
            # Automatically adding the creator as a member and an admin
            CommunityMembership.objects.create(community=community, user=request.user)
            community.moderator.add(request.user)  # Adding as admin
            return redirect('community_content', community_id=community.id)
    else:
        form = CommunityForm()
    return render(request, 'create_community.html', {'form': form})

@login_required
def community_content(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    user_is_member = community.is_member(request.user)
    user_is_admin = community.admin.filter(id=request.user.id).exists()

    # Fetch templates related to the community directly
    templates = community.templates.all()
    # Fetch posts related to the community directly
    posts = community.posts.all()

    return render(request, 'community.html', {
        'community': community,
        'user_is_member': user_is_member,
        'user_is_admin': user_is_admin,
        'templates': templates,
        'posts': posts
    })

@login_required
def join_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    CommunityMembership.objects.get_or_create(community=community, user=request.user)
    return redirect('community_content', community_id=community_id)

@login_required
def leave_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    CommunityMembership.objects.filter(community=community, user=request.user).delete()
    return redirect('community_content', community_id=community_id)

@login_required
def list_communities(request):
    communities = Community.objects.all()
    communities_data = []
    for community in communities:
        is_member = request.user.is_member(community.id)
        communities_data.append({
            'community': community,
            'is_member': is_member
        })
    return render(request, 'list_communities.html', {'communities': communities_data})

# COMMUNITY MODERATOR ADD/REMOVE PLACEHOLDING FOR NOW
@login_required
def add_moderator(request, community_id, user_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user == community.admin:  # Ensure only the admin can add moderators
        user_to_add = get_object_or_404(User, id=user_id)
        community.moderator.add(user_to_add)
        return redirect('community_settings', community_id=community.id)
    else:
        return redirect('community_content', community_id=community.id)

@login_required
def remove_moderator(request, community_id, user_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user == community.admin:  # Ensure only the admin can add moderators
        user_to_remove = get_object_or_404(User, id=user_id)
        community.moderator.remove(user_to_remove)
        return redirect('community_settings', community_id=community.id)
    else:
        return redirect('community_content', community_id=community.id)
    
# TEMPLATE VIEWS
def manage_templates(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    return render (request, 'manage_templates.html', {'community': community})

def create_template(request, community_id):
    community = get_object_or_404(Community, pk=community_id)  # Fetch the community instance

    if request.method == 'POST':
        form = TemplateForm(request.POST, extra=request.POST.get('field_count'))
        if form.is_valid():
            # Create the template with the community link
            template = Template(
                title=form.cleaned_data['post_title'],
                description=form.cleaned_data['post_description'],
                community=community
            )
            template.save()

            # CUSTOM FIELDS
            field_count = int(request.POST.get('field_count', 0))
            for i in range(field_count):
                field_name = form.cleaned_data.get(f'custom_field_{i}', '')
                field_type = form.cleaned_data.get(f'custom_type_{i}', '')
                if field_name and field_type: 
                    TemplateField.objects.create(
                        template=template,
                        field_name=field_name,
                        field_type=field_type
                    )

            return redirect('community_content', community_id=community_id)

    else:
        form = TemplateForm(extra=0)

    return render(request, 'create_template.html', {'form': form, 'community_id': community_id})


def get_dynamic_form(template_id):
    template = Template.objects.get(pk=template_id)
    class DynamicForm(forms.Form):
        # Standard fields from Template model
        title = forms.CharField(max_length=255, initial=template.title)
        description = forms.CharField(widget=forms.Textarea, initial=template.description)

        # Dynamic fields based on the template
        for field in template.fields.all():
            if field.field_type == 'text':
                field_instance = forms.CharField(label=field.field_name, required=False)
            elif field.field_type == 'number':
                field_instance = forms.IntegerField(label=field.field_name, required=False)
            elif field.field_type == 'date':
                field_instance = forms.DateField(label=field.field_name, required=False)
            # MORE TYPES WILL BE ADDED
            setattr(DynamicPostForm, field.field_name, field_instance)
    return DynamicForm

def create_post(request, community_id, template_id):
    community = get_object_or_404(Community, pk=community_id)
    template = get_object_or_404(Template, pk=template_id)
    template_fields = list(template.fields.all().values('field_name', 'field_type'))

    if request.method == 'POST':
        form = DynamicPostForm(request.POST, template_fields=template_fields)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.community = community
            new_post.template = template
            new_post.created_by = request.user

            # JSON field
            data = {}
            for field in template_fields:
                field_name = field['field_name']
                if field_name in form.cleaned_data:
                    data[field_name] = form.cleaned_data[field_name]
            new_post.data = data  # SAVE 

            new_post.save()
            return redirect('community_content', community_id=community_id)
    else:
        form = DynamicPostForm(template_fields=template_fields)

    return render(request, 'create_post.html', {
        'form': form,
        'community_id': community_id,
        'template_id': template_id
    })

def view_post(request, community_id, post_id):
    community= get_object_or_404(Community, pk=community_id)
    post= get_object_or_404(Post, pk=post_id)

    return render(request, 'view_post.html', {
        'community': community,
        'post': post
    })


