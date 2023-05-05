from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_rendered, name='map_rendered'),
    path('data', views.pivot_data, name='pivot_data'),
    path('map', views.interactive_map, name='interactive_map'),
]