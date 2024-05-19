from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django import forms
from .models import Community, CommunityMembership, Template, TemplateField, Post, Comment 
from .forms import CommunityForm, TemplateForm, DynamicPostForm, CommentForm, InviteForm
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.db.models import Count
import json
from datetime import date
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage



User = get_user_model()

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    for post in posts:
        post.is_followed = post.created_by.is_followed(request.user)
    communities= Community.objects.annotate(num_members=Count('members')).order_by('-num_members')
    followed_communities = [community for community in communities if community.is_member(request.user)]
    return render(request, 'home.html', {'posts': posts, 'communities': communities, 'followed_communities': followed_communities})

@login_required
def search(request):
    if request.method == "POST":
        searched = request.POST.get('searched', '').strip()

        if searched:
            posts = Post.objects.filter(title__icontains=searched)
            communities = Community.objects.filter(name__icontains=searched)
            users = User.objects.filter(username__icontains=searched)
            return render(request, 'search.html', {
                'searched': searched,
                'posts': posts,
                'communities': communities,
                'users': users
            })
        else:
            return render(request, 'search.html', {'error': 'Please enter a search term.'})
    else:
        return render(request, 'search.html')


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

            # Creating a default template for the new community
            default_template = Template.objects.create(
                title="Default Template",
                description="This is a default template with Title and Description fields.",
                community=community
            )

            TemplateField.objects.create(
                template=default_template,
                field_name='Description',
                field_type='textArea'
            )

            return redirect('community_content', community_id=community.id)
    else:
        form = CommunityForm()
    return render(request, 'create_community.html', {'form': form})


@login_required
def community_content(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    user = request.user
    user_is_member = community.is_member(user)
    user_is_admin = community.admin.filter(id=user.id).exists()
    is_private = community.isPrivate
    user_is_invited = community.invited.filter(id=user.id).exists()

    # If the community is private and the user is not a member or invited
    if is_private and not (user_is_member or user_is_invited):
        return render(request, 'error.html')

    # Fetching templates related to the community directly
    templates = community.templates.all()
    # Fetching posts related to the community directly
    posts = community.posts.all().order_by('-created_at')

    return render(request, 'community.html', {
        'community': community,
        'is_private': is_private,
        'user_is_member': user_is_member,
        'user_is_admin': user_is_admin,
        'user_is_invited': user_is_invited,
        'templates': templates,
        'posts': posts,
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
    return redirect('list_communities')

@login_required
def list_communities(request):
    communities = Community.objects.all()
    communities_data = []
    for community in communities:
        is_member = request.user.is_member(community.id)
        is_admin = community.admin.filter(id=request.user.id).exists()
        if request.user in community.invited.all():
            is_invited = True
        else:
            is_invited = False
        communities_data.append({
            'community': community,
            'is_member': is_member,
            'is_invited': is_invited,
            'is_admin': is_admin,
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
    if request.user == community.admin:  # Ensuring only the admin can add moderators
        user_to_remove = get_object_or_404(User, id=user_id)
        community.moderator.remove(user_to_remove)
        return redirect('community_settings', community_id=community.id)
    else:
        return redirect('community_content', community_id=community.id)
    
# TEMPLATE VIEWS
def manage_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    return render (request, 'manage_community.html', {'community': community})

def create_template(request, community_id):
    community = get_object_or_404(Community, pk=community_id)  # Fetching the community instance

    if request.method == 'POST':
        form = TemplateForm(request.POST, extra=request.POST.get('field_count'))
        if form.is_valid():
            # Creating the template with the community link
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

@login_required
def create_post(request, community_id, template_id):
    template = get_object_or_404(Template, pk=template_id)
    template_fields = list(template.fields.all().values('field_name', 'field_type'))

    if request.method == 'POST':
        form = DynamicPostForm(request.POST, request.FILES, template_fields=template_fields)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.community_id = community_id
            new_post.created_by = request.user

            # Handling JSON data
            data = {}
            for field in template_fields:
                field_name = field['field_name']
                field_value = form.cleaned_data.get(field_name)
                # Handling data types one by one
                if field['field_type'] == 'date' and field_value:
                    field_value = field_value.isoformat()
                elif field['field_type'] == 'time' and field_value:
                    field_value = field_value.isoformat()
                elif field['field_type'] == 'image' and field_value:
                    file_path = default_storage.save(f'media/images/{field_value.name}', field_value)
                    field_value = file_path
                    data["image"] = field_value  
                elif field['field_type'] == 'color' and field_value:
                    data["color"] = field_value
                elif field['field_type'] == 'geolocation':
                    latitude = form.cleaned_data.get(field_name + '_latitude')
                    longitude = form.cleaned_data.get(field_name + '_longitude')
                    field_value = {
                        'latitude': float(latitude) if latitude else None,
                        'longitude': float(longitude) if longitude else None
                    }
                data[field_name] = field_value
            
            new_post.data = data
            new_post.save()
            return redirect('community_content', community_id=community_id)
    else:
        form = DynamicPostForm(template_fields=template_fields)

    return render(request, 'create_post.html', {
        'form': form,
        'community_id': community_id,
        'template': template,
        'template_id': template_id,
    })

def view_post(request, community_id, post_id):
    community = get_object_or_404(Community, pk=community_id)
    post = get_object_or_404(Post, pk=post_id)
    user_is_member = community.is_member(request.user)
    comments = post.comments.all()

    if isinstance(post.data, str):
        try:
            post.data = json.loads(post.data)
        except json.JSONDecodeError:
            post.data = {}

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('view_post', community_id=community_id, post_id=post_id)
    else:
        form = CommentForm()

    return render(request, 'view_post.html', {
        'community': community,
        'post': post,
        'comments': comments,
        'form': form,
        'user_is_member': user_is_member,
    })

@login_required
def edit_post(request, community_id, post_id):
    community = get_object_or_404(Community, id=community_id)
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = DynamicPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('view_post', community_id=community_id, post_id=post_id)
    else:
        form = DynamicPostForm(instance=post)
    
    return render(request, 'edit_post.html', {'form': form, 'community': community, 'post': post})

def delete_post(request, community_id, post_id):
    community = get_object_or_404(Community, id=community_id)
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(User, id=request.user.id)
    if request.method == "POST":
        post.delete(request.user)
        return redirect('community_content', community_id=community_id)
    
    return render(request, 'delete_post.html', {'community': community, 'post': post, 'user': user})

@login_required
def invite_users(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            if request.user in community.admin.all():
                selected_users = form.cleaned_data['invited']
                for user in selected_users:
                    community.invited.add(user)
                return redirect('community_content', community_id=community_id)
            else:
                print("User is not the admin")
        else:
            print("Form is invalid:", form.errors)
    else:
        form = InviteForm()
    return render(request, 'invite_users.html', {'form': form, 'community': community})

@login_required
def view_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    communities = user.get_communities()
    following = user.following.all() 
    followed_by = user.get_followers()
    return render(request, 'view_user.html', {'user': user, 'communities': communities, 'following': following, 'followed_by': followed_by})

def conduct(request):
    return render(request, 'conduct.html')

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    request.user.follow(user_to_follow)
    return redirect('view_user', user_id)

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    request.user.unfollow(user_to_unfollow)
    return redirect('view_user', user_id)

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    request.user.delete(user)
    if request.method == "POST":
        user.delete(request.user)
        return redirect('home')

    return render(request, 'delete_user.html', {'user': user})

@login_required
def add_moderator(request, community_id, user_id):
    community = get_object_or_404(Community, pk=community_id)
    user = get_object_or_404(User, pk=user_id)

    if community.admin.filter(id=request.user.id).exists():
        community.make_moderator(user)
        return redirect('community_content', community_id=community_id)
    else:
        raise PermissionDenied("You do not have permission to add a moderator.")

@login_required
def remove_moderator(request, community_id, user_id):
    community = get_object_or_404(Community, pk=community_id)
    user = get_object_or_404(User, pk=user_id)

    if community.admin.filter(id=request.user.id).exists():
        community.remove_moderator(user)
        return redirect('community_content', community_id=community.id)
    else:
        raise PermissionDenied("You do not have permission to remove a moderator.")


