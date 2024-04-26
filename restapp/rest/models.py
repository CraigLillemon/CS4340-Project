from django.db import models

# Create your models here.
class Note(models.Model):
    business_id = models.PositiveIntegerField(default=0)
    note_text = models.CharField(max_length=400)
    note_publisher = models.CharField(max_length=20)
    note_pub_date = models.DateTimeField("date posted")