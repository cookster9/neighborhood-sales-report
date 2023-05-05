from django.http import JsonResponse
from django.shortcuts import render
from dashboard.models import RealEstateInfoScrape
from django.core import serializers
from django.db.models import Count
import json
from django.core.serializers.json import DjangoJSONEncoder
from pathlib import Path
import os

module_dir = os.path.dirname(__file__)

def interactive_map(request):
    return render(request, 'dashboard/base-map.html', {})

def map_rendered(request):
    context = {}
    return render(request, 'dashboard/map_rendered.html', context)

def pivot_data(request):
    dataset = list(RealEstateInfoScrape.objects.values("neighborhood").annotate(count=Count(id)))
    # data = serializers.serialize('json', dataset)
    # data = json.dumps(list(dataset), cls=DjangoJSONEncoder)
    return JsonResponse(list(dataset), safe=False)
