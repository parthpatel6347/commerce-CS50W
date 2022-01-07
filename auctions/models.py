from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import BooleanField


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    startingBid = models.IntegerField()
    image = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = BooleanField(default=True)
    winner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="winner", null=True, blank=True
    )

    def __str__(self):
        return f"Title: {self.title}, description:{self.description}, starting bid:{self.startingBid}, image: {self.image}, user:{self.user}, category:{self.category}, active:{self.active}, winner:{self.winner}"


class Bids(models.Model):
    Listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()


class Comments(models.Model):
    Listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()


class Watchlist(models.Model):
    Listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="listing"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
