from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Category, Listing, Watchlist, Comments, Bids


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":

        user = request.user
        title = request.POST["title"]
        description = request.POST["description"]
        image = request.POST["image"]
        startingBid = int(request.POST["startingBid"])
        category = Category.objects.get(id=request.POST["category"])

        newListing = Listing(
            title=title,
            description=description,
            image=image,
            startingBid=startingBid,
            category=category,
            user=user,
        )
        newListing.save()

        return HttpResponse("TRYING TO ADD LISTING")
    else:
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {"categories": categories})


def listing(request, id):
    if request.method == "POST":
        return HttpResponse("POST REQUEST TO /listing")
    else:
        listing = Listing.objects.get(id=id)
        return render(request, "auctions/listing.html", {"listing": listing})


@login_required
def watchlist(request):

    # Get logged in user
    user = request.user

    if request.method == "POST":

        # If post request has a key of "remove"
        if request.POST.get("remove", ""):

            # Get listing id of the item to be removed from the watchlist
            listing = int(request.POST["remove"])

            # delete item from watchlist database
            Watchlist.objects.filter(user=user, Listing_id=listing).delete()

            # redirect to watchlist page
            return HttpResponseRedirect("watchlist")

        else:

            # get listing id of the item to be added in the watchlist
            listing = int(request.POST["listing"])

            # try to see the item already exists in the watchlist database
            w = Watchlist.objects.filter(user=user, Listing_id=listing)

            # If item doesn't exist in the database, add it
            if not w:
                watchlistItem = Watchlist(user=user, Listing_id=listing)
                watchlistItem.save()

                # redirect to watchlist page
                return HttpResponseRedirect("watchlist")

            else:
                return HttpResponse("Item already in watchlist")

    else:
        # get listing ids from watchlist database for current user
        ids = Watchlist.objects.values_list("Listing_id", flat=True).filter(user=user)

        # get listing data corresponding to the listing ids
        userWatchlist = Listing.objects.filter(id__in=ids)

        return render(
            request, "auctions/watchlist.html", {"userWatchlist": userWatchlist}
        )
