from django.urls import path
from . import views

urlpatterns = [
    path('', views.leaflet_map, name='leaflet_map'),
    path('data', views.leaflet_map, name='leaflet_map'),
    path('map', views.interactive_map, name='interactive_map'),
]