from django.http import JsonResponse
from django.shortcuts import render
from dashboard.models import RealEstateInfoScrape
from django.core import serializers
from django.db.models import Count
import json
from django.core.serializers.json import DjangoJSONEncoder
from pathlib import Path
import os
from django.db.models import F
from datetime import datetime, timedelta
import re

module_dir = os.path.dirname(__file__)

# /map
def interactive_map(request):
    return render(request, 'dashboard/base-map.html', {})

# /
def map_rendered(request):
    file_path = module_dir + '/static/dashboard/json/total_sales.json'  # '/templates/dashboard/base-map.html'
    data_file = open(file_path, 'rb')  # I used 'rb' here since I got an 'gbk' decode error
    data = data_file.read().decode()
    # map_html = Path('/dashboard/templates/dashboard/base-map.html').read_text()
    print(data)
    context = {}
    context["sales_data"] = json.loads(data)
    print(context)
    return render(request, 'dashboard/map_rendered.html', context)

# /data
def pivot_data(request):
    # Get the current date and calculate the date six weeks ago
    now = datetime.now()
    six_weeks_ago = now - timedelta(weeks=10)

    # Perform the ORM query
    queryset = RealEstateInfoScrape.objects.filter(
        sale_date__gt=six_weeks_ago,
        property_use='SINGLE FAMILY'
    )

    # Access the query results
    group_dict = {}
    for result in queryset:
        neighborhood = result.neighborhoods.id

        if str(neighborhood) in group_dict:
            blank = group_dict[str(neighborhood)]
        else:
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

        print(result.id)
        if result.tn_davidson_addresses is not None:
            house_json = {'reis_id': result.id
                          ,'lat': result.tn_davidson_addresses.latitude
                          ,'long': result.tn_davidson_addresses.longitude
                          ,'address': result.location
                          ,'sale_date': result.sale_date}
            group_dict[str(neighborhood)]['house_list'].append(house_json)


    print(len(group_dict))
    NASHVILLE_LATITUDE = 36.164577
    NASHVILLE_LONGITUDE = -86.776949
    context = {
        'nash_lat': NASHVILLE_LATITUDE
        ,'nash_long': NASHVILLE_LONGITUDE
        ,'groups': group_dict
    }

    return render(request, 'dashboard/base.html', context)
