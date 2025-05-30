from django.urls import path
from .views import home, protected_view

app_name = 'base'

urlpatterns = [
    path('', home, name='home'),
    path('protected/', protected_view, name='protected_view'),
]