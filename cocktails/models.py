from django.db import models
from django.contrib.auth.models import User

class Cocktail(models.Model):
    category = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, help_text="e.g., Margarita")
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='recipe_images/', blank=True, null=True)
    video = models.URLField( blank=True, null=True)
    recipe_steps = models.JSONField(blank=True, help_text="List of steps", null=True)  # Renamed to recipe_steps
    alcohol_content = models.FloatField(help_text="Alcohol percentage (e.g., 20 for 20%)", blank=True, null=True)
    flavor_profile = models.CharField(max_length=50, blank=True)
    drink_strength = models.CharField(max_length=50, blank=True, help_text="e.g., Light, Medium, Strong")
    glass_type = models.CharField(max_length=50, blank=True)
    rating = models.FloatField(default=0.0, help_text="Average rating out of 5", blank=True, null=True)
    review_count = models.PositiveIntegerField(default=0, help_text="Number of reviews")
    servings = models.PositiveIntegerField(default=1, blank=True, null=True)

    def __str__(self):
        return self.title

class Ingredient(models.Model):
    cocktail = models.ForeignKey(
        Cocktail,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='ingredients'  # Added to match serializer
    )
    name = models.CharField(max_length=400)
    quantity = models.FloatField(blank=True, null=True)  # Changed to FloatField
    unit = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class BookMark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE, blank=True, null=True)  # Renamed to cocktail

    def __str__(self):
        return self.user.email if self.user else "No User"