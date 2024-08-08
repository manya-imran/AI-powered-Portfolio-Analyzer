from django.db import models

# Create your models(db) here in Django

# new model Review
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    site_url = models.CharField(max_length=10000)
    # url for the image hosting site - cloudinary
    # it return the url of screenshot
    site_image_url = models.CharField(max_length=10000)
    feedback = models.CharField(max_length=100000, default=None, null=True) # response from openai

    # tuple of choices
    GREAT_POOR_CHOICES = (
        ('great', 'Great'),
        ('poor', 'Poor'),
    )
    user_rating = models.CharField(
        max_length=5,
        choices = GREAT_POOR_CHOICES,
        default = None, # for testing you dont have to add a value
        null = True,
        blank = True
    )



