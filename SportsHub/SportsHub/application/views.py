from django.shortcuts import render

def home(request):
    return render(request, 'home.html', {})

def search(request):
    if request.method == "POST":
        searched = request.POST['searched'] 
        items = all.objects.filter(name__contains = searched)
        
        return render(request, 'search.html', {'searched': searched, 'items':items})
    else:
        return render(request, 'search.html', {})