from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from dashboard.models import RealEstateInfoScrape
from django.core.cache import cache
import os
from datetime import datetime, timedelta
import re
from .forms import ContactForm
from django.conf import settings

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
            user_email = form.cleaned_data["user_email"]
            message = user_email+'<br>'+form.cleaned_data['message']
            try:
                send_mail(subject, message,app_email,[app_email])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return redirect("success")
    return render(request, 'dashboard/contact.html', {"form": form})

# /success
def success(request):
    context = {}
    return render(request, 'dashboard/success.html', context)

# /
def leaflet_map(request):
    context = cache.get('map')
    if context is None:

        # Get the current date and calculate the date six weeks ago
        now = datetime.now()
        six_weeks_ago = now - timedelta(weeks=6)

        # Perform the ORM query
        queryset = RealEstateInfoScrape.objects.filter(
            sale_date__gt=six_weeks_ago,
            property_use='SINGLE FAMILY'
        ).exclude(sale_price='$0')

        # Access the query results
        group_dict = {}
        for result in queryset:
            neighborhood = result.neighborhoods.id

            if str(neighborhood) not in group_dict:
                neighborhood_name = result.neighborhoods.description
                neighborhood_clean = re.sub('[^A-Za-z0-9 /]+', '', neighborhood_name)

                avg_latitude = result.neighborhoods.latitude
                avg_longitude = result.neighborhoods.longitude
                mod_neighborhood = int(neighborhood) % 7
                neighborhood_dict = {'lat': avg_latitude
                                     ,'long': avg_longitude
                                     ,'icon_num': mod_neighborhood
                                     ,'name': neighborhood_clean
                                     ,'house_list': []
                }
                group_dict[str(neighborhood)] = neighborhood_dict

            if result.tn_davidson_addresses is not None:
                house_json = {'reis_id': result.id
                              ,'lat': result.tn_davidson_addresses.latitude
                              ,'long': result.tn_davidson_addresses.longitude
                              ,'address': result.location
                              ,'sale_date': result.sale_date
                              ,'sale_price': result.sale_price
                              ,'square_footage': result.square_footage}
                group_dict[str(neighborhood)]['house_list'].append(house_json)
            if 'total_sale_count' in group_dict[str(neighborhood)]:
                group_dict[str(neighborhood)]['total_sale_count'] = group_dict[str(neighborhood)]['total_sale_count'] + 1
            else:
                group_dict[str(neighborhood)]['total_sale_count'] = 1


        print(len(group_dict))
        NASHVILLE_LATITUDE = 36.164577
        NASHVILLE_LONGITUDE = -86.776949

        sorted_by_name = sorted(group_dict.items(), key=lambda x:x[1]['name'])
        sorted_dict = dict(sorted_by_name)
        context = {
            'nash_lat': NASHVILLE_LATITUDE
            ,'nash_long': NASHVILLE_LONGITUDE
            ,'groups': sorted_dict
        }
        cache.set('map',context)
    else:
        print("got cached content")
    return render(request, 'dashboard/map_leaflet.html', context)
