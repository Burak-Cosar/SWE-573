from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Event, Venue
from .forms import VenueForm, EventForm
from django.http import HttpResponseRedirect
from django.http import HttpResponse, FileResponse
import csv, io

#Import PDF Stuff
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

#Import pagination stuff
from django.core.paginator import Paginator

def add_event(request):
    submitted = False
    if request.method == "POST": 
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_event?submitted=True')
    else:
        form = EventForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'add_event.html', {'form': form, 'submitted': submitted})

def home(request, year=2024, month='April'):
    name = "Cos"
    month = month.capitalize()
    #Convert month from name to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)
    now = datetime.now()
    current_year = now.year

    #current time
    time = now.strftime('%I:%M &p')

    #create a calendar
    cal = HTMLCalendar().formatmonth(year, month_number)

    return render(request,
        'home.html', {
        "name": name,
        "year": year,
        "month": month,
        "month_number": month_number,
        "cal": cal,
        "current_year": current_year,
        })

def all_events(request):
    event_list = Event.objects.all().order_by('event_date')
    return render(request, 'event_list.html', {'event_list': event_list})

def add_venue(request):
    submitted = False
    if request.method == "POST": 
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'add_venue.html', {'form': form, 'submitted': submitted})

def list_venues(request):
    venue_list = Venue.objects.all()

    #Set up Pagination
    p = Paginator(Venue.objects.all(), 1)
    page = request.GET.get('page')
    venues = p.get_page(page)
    nums = "1" * venues.paginator.num_pages

    return render(request, 'venues.html', {'venue_list': venue_list, 'venues': venues, 'nums': nums})

def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    return render(request, 'show_venue.html', {'venue': venue})

def search_venues(request):
    if request.method == "POST":
        searched = request.POST['searched'] 
        venues = Venue.objects.filter(name__contains = searched)
        
        return render(request, 'search_venues.html', {'searched': searched, 'venues':venues})
    else:
        return render(request, 'search_venues.html', {})
    
def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, instance =venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')
    return render(request, 'update_venue.html', {'venue': venue, 'form': form})

def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    form = EventForm(request.POST or None, instance = event)
    if form.is_valid():
        form.save()
        return redirect('list-events')
    return render(request, 'update_events.html', {'event': event, 'form': form})

def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    event.delete()
    return redirect('list-events')

def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')

def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=venues.txt'
    #Designate the model
    venues = Venue.objects.all()
    lines = []

    for venue in venues:
        lines.append(f'{venue.name}\n{venue.address}\n{venue.phone}\n{venue.zip_code}\n{venue.phone}\n{venue.web}\n{venue.email_address}\n\n')
    
    response.writelines(lines)
    return response

def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=venues.csv'

    #Create a csv writer
    writer = csv.writer(response)

    #Designate the model
    venues = Venue.objects.all()
    
    writer.writerow(['Name', 'Address', 'Phone', 'Zip Code', 'Phone', 'Web', 'Email Address'])

    for venue in venues:
        writer.writerow([venue.name, venue.address, venue.phone, venue.zip_code, venue.phone, venue.web, venue.email_address])

    return response

def venue_pdf(request):
    #Create Bytestream buffer
    buf = io.BytesIO()
    #Canvas
    c = canvas.Canvas (buf, pagesize=letter, bottomup=0)
    #TextObject
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    #Designate the model
    venues = Venue.objects.all()

    #Add some lines of text
    lines =[]

    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(" ")

    for line in lines:
        textob.textLine(line)

    # Finish up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    #Return stuff
    return FileResponse(buf, as_attachment=True, filename='Venues.pdf')