from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from django.db import IntegrityError
from ..models import Categories, Restaurants, Reviews, FoodPoll


def admin_dashboard(request):
    """Main admin dashboard view"""
    # Get all data for display
    categories = Categories.objects.all().order_by('name')
    restaurants = Restaurants.objects.all().order_by('name')
    users = User.objects.all()
    reviews = Reviews.objects.all()[:10]
    
    context = {
        'categories': categories,
        'restaurants': restaurants,
        'users': users,
        'reviews': reviews,
        'total_categories': categories.count(),
        'total_restaurants': restaurants.count(),
        'total_users': users.count(),
        'total_reviews': Reviews.objects.count(),
    }
    return render(request, 'test/test.html', context)


# Category Management Views
def add_category(request):
    """Add a new category"""
    if request.method == 'POST':
        name = request.POST.get('category_name')
        if name:
            try:
                Categories.objects.create(name=name)
                messages.success(request, f'Category "{name}" added successfully!')
            except IntegrityError:
                messages.error(request, 'Category already exists!')
        else:
            messages.error(request, 'Category name is required!')
    return redirect('admin_dashboard')


def delete_category(request, category_id):
    """Delete a category"""
    if request.method == 'POST':
        category = get_object_or_404(Categories, id=category_id)
        category_name = category.name
        
        # Check if category has associated restaurants
        restaurant_count = category.restaurants_set.count()
        if restaurant_count > 0:
            messages.warning(request, f'Cannot delete category "{category_name}" because it has {restaurant_count} associated restaurants.')
        else:
            category.delete()
            messages.success(request, f'Category "{category_name}" deleted successfully!')
    return redirect('admin_dashboard')


# Restaurant Management Views
def add_restaurant(request):
    """Add a new restaurant"""
    if request.method == 'POST':
        name = request.POST.get('restaurant_name')
        category_id = request.POST.get('restaurant_category')
        
        if name and category_id:
            try:
                category = get_object_or_404(Categories, id=category_id)
                Restaurants.objects.create(name=name, category=category)
                messages.success(request, f'Restaurant "{name}" added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding restaurant: {str(e)}')
        else:
            messages.error(request, 'Restaurant name and category are required!')
    return redirect('admin_dashboard')


def delete_restaurant(request, restaurant_id):
    """Delete a restaurant"""
    if request.method == 'POST':
        restaurant = get_object_or_404(Restaurants, id=restaurant_id)
        restaurant_name = restaurant.name
        
        # Check if restaurant has reviews
        review_count = restaurant.reviews_set.count()
        if review_count > 0:
            messages.warning(request, f'Cannot delete restaurant "{restaurant_name}" because it has {review_count} reviews. Delete reviews first.')
        else:
            restaurant.delete()
            messages.success(request, f'Restaurant "{restaurant_name}" deleted successfully!')
    return redirect('admin_dashboard')


# User Management Views
def add_user(request):
    """Add a new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if username and password:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                messages.success(request, f'User "{username}" created successfully!')
            except IntegrityError:
                messages.error(request, f'Username "{username}" already exists!')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            messages.error(request, 'Username and password are required!')
    return redirect('admin_dashboard')


def delete_user(request, user_id):
    """Delete a user"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        username = user.username
        
        # Don't allow deletion of superuser or current user
        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser!')
        elif user == request.user:
            messages.error(request, 'Cannot delete your own account!')
        else:
            # Check if user has reviews or polls
            review_count = user.reviews_set.count()
            poll_count = user.foodpoll_set.count()
            
            if review_count > 0 or poll_count > 0:
                messages.warning(request, f'User "{username}" has {review_count} reviews and {poll_count} polls. These will also be deleted.')
            
            user.delete()
            messages.success(request, f'User "{username}" deleted successfully!')
    return redirect('admin_dashboard')


# Review Management Views
def delete_review(request, review_id):
    """Delete a review"""
    if request.method == 'POST':
        review = get_object_or_404(Reviews, id=review_id)
        restaurant_name = review.restaurant.name
        user_name = review.user.username
        
        review.delete()
        messages.success(request, f'Review by "{user_name}" for "{restaurant_name}" deleted successfully!')
    return redirect('admin_dashboard')


# Bulk operations
def clear_all_polls(request):
    """Clear all food polls"""
    if request.method == 'POST':
        poll_count = FoodPoll.objects.count()
        FoodPoll.objects.all().delete()
        messages.success(request, f'Cleared {poll_count} polls successfully!')
    return redirect('admin_dashboard')


def get_statistics(request):
    """Get dashboard statistics"""
    stats = {
        'categories': Categories.objects.count(),
        'restaurants': Restaurants.objects.count(),
        'users': User.objects.count(),
        'reviews': Reviews.objects.count(),
        'polls': FoodPoll.objects.count(),
    }
    return render(request, 'test/statistics.html', {'stats': stats})


def test_view(request):
    """Legacy test view - redirects to admin dashboard"""
    return redirect('admin_dashboard')
