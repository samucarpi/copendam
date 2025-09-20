from django.db import models
from django.contrib.auth.models import User


'''
    Categories model representing different categories of restaurants.
'''
class Categories(models.Model):
    name = models.CharField(max_length=100)


'''
    Restaurant model representing a restaurant in the database.
    TBA:
    - Location
    - Price range
    - Cuisine type
    - Reviews
'''
class Restaurants(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)


'''
    Contains the votes of users for different categories.
    Each vote links a user to a category.
    After each poll, votes are cleared.

'''
class Votes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)

