from django.urls import path
from .views import DashboardView, fetch_github_data, fetch_top3_comments

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('fetch-data/', fetch_github_data, name='fetch_github_data'),
    path('fetch-comments/', fetch_top3_comments, name='fetch_top3_comments'),
]