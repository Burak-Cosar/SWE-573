from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Community, CommunityMembership
from .forms import CommunityForm

User = get_user_model()

def home(request):
    return render(request, 'home.html', {})

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
    return render(request, 'community.html', {
        'community': community,
        'user_is_member': user_is_member
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

# COMMUNITY MODERATOR ADD/REMOVE

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