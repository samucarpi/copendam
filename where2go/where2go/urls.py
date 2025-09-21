"""
URL configuration for where2go project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views.views import dashboard, food_poll_vote_ajax, food_poll_data_ajax, presence_poll_vote_ajax, presence_poll_data_ajax
from .views.auth_views import auth_view, logout_view
from .views.weather_views import get_weather_data
from .views.test_views import (
    admin_dashboard, test_view, add_category, delete_category,
    add_restaurant, delete_restaurant, add_user, delete_user,
    delete_review, clear_all_polls, get_statistics
)

urlpatterns = [
    # Authenticated user URLs
    path('', auth_view, name='auth'),
    path('logout/', logout_view, name='logout'),

    # Main application URLs
    path('dashboard/', dashboard, name='dashboard'),
    path('food-poll/vote/', food_poll_vote_ajax, name='food_poll_vote'),
    path('food-poll/data/', food_poll_data_ajax, name='food_poll_data'),
    path('presence-poll/vote/', presence_poll_vote_ajax, name='presence_poll_vote'),
    path('presence-poll/data/', presence_poll_data_ajax, name='presence_poll_data'),
    path('weather/data/', get_weather_data, name='weather_data'),


    # Test and admin URLs
    path('test/', test_view, name='test_view'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('add-category/', add_category, name='add_category'),
    path('delete-category/<int:category_id>/', delete_category, name='delete_category'),
    path('add-restaurant/', add_restaurant, name='add_restaurant'),
    path('delete-restaurant/<int:restaurant_id>/', delete_restaurant, name='delete_restaurant'),
    path('add-user/', add_user, name='add_user'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
    path('delete-review/<int:review_id>/', delete_review, name='delete_review'),
    path('clear-all-polls/', clear_all_polls, name='clear_all_polls'),
    path('get-statistics/', get_statistics, name='get_statistics'),
    path('admin/', admin.site.urls),
]
