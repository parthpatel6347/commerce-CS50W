from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)


class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    startingBid = models.IntegerField()
    image = models.TextField()
    category = models.ForeignKey(Category, on_delete=CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE)


class Bids(models.Model):
    Listing = models.ForeignKey(Listing, on_delete=CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE)
    amount = models.IntegerField()


class Comments(models.Model):
    Listing = models.ForeignKey(Listing, on_delete=CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE)
    comment = models.TextField()


class Watchlist(models.Model):
    Listing = models.ForeignKey(Listing, on_delete=CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE)
