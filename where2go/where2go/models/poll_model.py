from django.db import models
from django.contrib.auth.models import User


class Restaurants(models.Model):
    name = models.CharField(max_length=200)


class Votes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)

