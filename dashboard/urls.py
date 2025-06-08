from django.urls import path
from .views import DashboardView, fetch_github_data

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('fetch-data/', fetch_github_data, name='fetch_github_data'),
]