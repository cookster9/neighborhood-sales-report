from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from dashboard.models import RealEstateSales
from django.core.cache import cache
import os
from datetime import datetime, timedelta
import re
from .forms import ContactForm
from .forms import NeighborhoodUpdateForm
from django.conf import settings
from dashboard.models import Neighborhoods
from django.contrib import messages
from .update_neighborhood import update_neighborhood

module_dir = os.path.dirname(__file__)

# /about
def about_page(request):
    context = {}
    return render(request, 'dashboard/about.html', context)

# /contact
def contact_page(request):
    if request.method == "GET":
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            app_email = settings.DEFAULT_FROM_EMAIL
            your_email = form.cleaned_data["your_email"]
            message = your_email+'<br>'+form.cleaned_data['message']
            try:
                send_mail(subject, message,app_email,[app_email])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            messages.success(request, 'Thank you for your message.')
            return redirect('success')
    return render(request, 'dashboard/contact.html', {"form": form})

# /success
def success(request):
    context = {}
    return render(request, 'dashboard/success.html', context)

# /
def leaflet_map(request):
    context = None
    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding):
        form = NeighborhoodUpdateForm(request.POST)
        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            update_id = form.cleaned_data['id']
            print("Update ID", update_id)
            success_message = update_neighborhood(update_id)

            # redirect to a new URL:
            messages.success(request, success_message)
            return redirect('success')
    else:
        form = NeighborhoodUpdateForm()
    context = cache.get('map')
    if context is None:

        # Get the current date and calculate the date six weeks ago
        now = datetime.now()
        six_weeks_ago = now - timedelta(weeks=6)

        neighborhood_queryset = (Neighborhoods.objects
                                 .filter(latitude__isnull=False, visible=True))
        # Access the query results
        group_dict = {}

        for result in neighborhood_queryset:
            neighborhood = result.id
            neighborhood_name = result.description
            neighborhood_clean = re.sub('[^A-Za-z0-9 /]+', '', neighborhood_name)

            avg_latitude = result.latitude
            avg_longitude = result.longitude
            mod_neighborhood = int(neighborhood) % 7
            neighborhood_dict = {'lat': avg_latitude
                , 'long': avg_longitude
                , 'icon_num': mod_neighborhood
                , 'name': neighborhood_clean
                , 'last_updated': result.last_updated
                , 'house_list': []
                                 }
            group_dict[str(neighborhood)] = neighborhood_dict

        # Perform the ORM query
        queryset = RealEstateSales.objects\
            .select_related('real_estate_properties','real_estate_properties__neighborhoods','real_estate_properties__tn_davidson_addresses')\
            .filter(
            sale_date__gt=six_weeks_ago,
            real_estate_properties__property_use='SINGLE FAMILY'
        ).exclude(sale_price='$0').order_by('-sale_date')

        top_dict = {}
        for result in queryset:

            # property_info = RealEstateProperties.objects.filter(id=result.real_estate_properties_id)
            # print(property_info.query)
            # print(property_info[0].__dict__)
            neighborhood = result.real_estate_properties.neighborhoods_id

            if result.real_estate_properties.tn_davidson_addresses_id is not None:
                house_json = {'reis_id': result.real_estate_properties.id
                              ,'lat': result.real_estate_properties.tn_davidson_addresses.latitude
                              ,'long': result.real_estate_properties.tn_davidson_addresses.longitude
                              ,'address': result.real_estate_properties.location
                              ,'sale_date': result.sale_date
                              ,'sale_price': result.sale_price
                              ,'square_footage': result.real_estate_properties.square_footage}
                group_dict[str(neighborhood)]['house_list'].append(house_json)
                if len(top_dict) < 100:
                    top_dict[len(top_dict)] = house_json
            if 'total_sale_count' in group_dict[str(neighborhood)]:
                group_dict[str(neighborhood)]['total_sale_count'] = group_dict[str(neighborhood)]['total_sale_count'] + 1
            else:
                group_dict[str(neighborhood)]['total_sale_count'] = 1

        NASHVILLE_LATITUDE = 36.164577
        NASHVILLE_LONGITUDE = -86.776949

        sorted_by_name = sorted(group_dict.items(), key=lambda x:x[1]['name'])
        sorted_dict = dict(sorted_by_name)
        context = {
            'nash_lat': NASHVILLE_LATITUDE
            ,'nash_long': NASHVILLE_LONGITUDE
            ,'groups': sorted_dict
            ,'top100': top_dict
            ,'form': form
        }
        # turn off cache for now
        # cache.set('map',context)
    else:
        print("got cached content")
    return render(request, 'dashboard/map_leaflet.html', context)
