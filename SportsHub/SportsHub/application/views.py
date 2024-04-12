from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Community, CommunityMembership
from .forms import CommunityForm

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
            community.owner = request.user
            community.save()
            # Automatically add the creator as a member and an admin
            CommunityMembership.objects.create(community=community, user=request.user)
            community.admins.add(request.user)  # Adding as admin
            return redirect('community_detail', community_id=community.id)
    else:
        form = CommunityForm()
    return render(request, 'create_community.html', {'form': form})

@login_required
def community_content(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    return render(request, 'community.html', {'community': community})

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
    return render(request, 'list_communities.html', {'communities': communities})

# COMMUNITY ADMIN ADD/REMOVE

@login_required
def add_admin(request, community_id, user_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user == community.owner:  # Ensure only the owner can add admins
        user_to_add = get_object_or_404(User, id=user_id)
        community.admins.add(user_to_add)
        return redirect('community_settings', community_id=community.id)
    else:
        return redirect('community_content', community_id=community.id)

@login_required
def remove_admin(request, community_id, user_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user == community.owner:  # Ensure only the owner can remove admins
        user_to_remove = get_object_or_404(User, id=user_id)
        community.admins.remove(user_to_remove)
        return redirect('community_settings', community_id=community.id)
    else:
        return redirect('community_content', community_id=community.id)
