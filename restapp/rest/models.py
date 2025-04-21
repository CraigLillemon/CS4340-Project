from django.db import models
from django.conf import settings

# Create your models here.
class Note(models.Model):
    business_id = models.PositiveIntegerField(default=0)
    note_text = models.CharField(max_length=400)
    note_publisher = models.CharField(max_length=20)
    note_pub_date = models.DateTimeField("date posted")

class Restaurant(models.Model):
    business_id = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    diets = models.JSONField(blank=True, null=True)

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    # Ensures a user can't favorite the same restaurant twice.
    class Meta:
        unique_together = ('user', 'restaurant')

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=1)
    # Ensures a user can't have multiple ratings for the same restaurant.
    class Meta:
        unique_together = ('user', 'restaurant')