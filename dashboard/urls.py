from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_with_pivot, name='dashboard_with_pivot'),
    path('data', views.pivot_data, name='pivot_data'),
    path('map', views.interactive_map, name='interactive_map'),
    path('mapiframe', views.map_rendered, name='map_rendered'),
]