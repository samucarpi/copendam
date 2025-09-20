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
from django.urls import path
from .views.views import dashboard
from .views.test_views import (
    admin_dashboard, test_view, add_category, delete_category,
    add_restaurant, delete_restaurant, add_user, delete_user,
    delete_review, clear_all_polls, get_statistics
)

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('test/', test_view, name='test_view'),
    
    # Admin Dashboard URLs
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('admin/category/add/', add_category, name='add_category'),
    path('admin/category/<int:category_id>/delete/', delete_category, name='delete_category'),
    path('admin/restaurant/add/', add_restaurant, name='add_restaurant'),
    path('admin/restaurant/<int:restaurant_id>/delete/', delete_restaurant, name='delete_restaurant'),
    path('admin/user/add/', add_user, name='add_user'),
    path('admin/user/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('admin/review/<int:review_id>/delete/', delete_review, name='delete_review'),
    path('admin/polls/clear/', clear_all_polls, name='clear_all_polls'),
    path('admin/stats/', get_statistics, name='get_statistics'),
]
