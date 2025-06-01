from django.urls import path
from .views import home, protected_view, set_location

app_name = 'base'

urlpatterns = [
    path('', home, name='home'),
    path('protected/', protected_view, name='protected_view'),
    path('set-location/', set_location, name='set_location'),
]