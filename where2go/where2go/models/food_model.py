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
class FoodPoll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)


'''
    Contains presence votes of users.
    Each user can vote whether they will be present or absent.
    Choices: 'present' or 'absent'
'''
class PresencePoll(models.Model):
    PRESENCE_CHOICES = [
        ('present', 'Presente'),
        ('absent', 'Assente'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    presence = models.CharField(max_length=10, choices=PRESENCE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.get_presence_display()}"


'''
    Reviews model representing user reviews for restaurants.
'''
class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)