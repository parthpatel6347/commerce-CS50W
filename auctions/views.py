from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Category, Listing, Watchlist, Comments, Bids


def index(request):

    # Get all active listings from database
    listings = Listing.objects.filter(active=True)

    # Get all bids from database
    bids = Bids.objects.all()

    return render(request, "auctions/index.html", {"listings": listings, "bids": bids})


def all(request):

    # Get all listings from database
    listings = Listing.objects.all()

    # Get all bids from database
    bids = Bids.objects.all()

    return render(request, "auctions/all.html", {"listings": listings, "bids": bids})


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

        # Get title value or return error
        if not request.POST.get("title"):
            # return error
            return render(
                request,
                "auctions/error.html",
                {"error": "Unable to get Title value."},
            )
        else:
            title = request.POST["title"]

        # Get description value or return error
        if not request.POST.get("description"):
            # return error
            return render(
                request,
                "auctions/error.html",
                {"error": "Unable to get Description value."},
            )
        else:
            description = request.POST["description"]

        # Get startingBid value or return error
        if not request.POST.get("startingBid"):
            # return error
            return render(
                request,
                "auctions/error.html",
                {"error": "Unable to get starting bid value."},
            )
        else:
            startingBid = int(request.POST["startingBid"])

        # Set category to default if none specified.
        if not request.POST.get("category"):
            category = Category.objects.get(name="Other")
        else:
            category = Category.objects.get(id=request.POST["category"])

        # Set a default image if none provided.
        if not request.POST.get("image"):
            image = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"
        else:
            image = request.POST["image"]

        # Create new database listing object
        newListing = Listing(
            title=title,
            description=description,
            image=image,
            startingBid=startingBid,
            category=category,
            user=user,
        )

        # Save new listing
        newListing.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {"categories": categories})


def listing(request, id):

    # Get listing with requested id
    listing = Listing.objects.get(id=id)

    # Check if logged in user is the winner of the listing
    winner = False
    if request.user and request.user == listing.winner:
        winner = True

    # Check if logged in user is the creator of the listing
    creator = False
    if request.user and request.user == listing.user:
        creator = True

    # Get all comments for the listing
    comments = Comments.objects.filter(Listing_id=listing)

    # Check if there is a bid on the listing
    if Bids.objects.filter(Listing_id=listing).exists():
        # get the bid object for listing
        b = Bids.objects.get(Listing_id=listing)
        bid = b.amount
    else:
        bid = None

    inWatchlist = False
    if (
        request.user
        and Watchlist.objects.filter(Listing_id=listing, user=request.user).exists()
    ):
        inWatchlist = True

    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "creator": creator,
            "winner": winner,
            "comments": comments,
            "bid": bid,
            "inWatchlist": inWatchlist,
        },
    )


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
            # Get listing data or return error
            if not request.POST.get("listing"):
                return render(
                    request,
                    "auctions/error.html",
                    {"error": "Unable to fetch listing data."},
                )
            else:
                listing = int(request.POST["listing"])

            # try to see the item already exists in the watchlist database
            w = Watchlist.objects.filter(user=user, Listing_id=listing)

            # If item doesn't exist in the database, add it
            if not w:
                watchlistItem = Watchlist(user=user, Listing_id=listing)
                watchlistItem.save()

                # redirect to watchlist page
                return HttpResponseRedirect("watchlist")

            # return error if item is already in watchlist.
            else:
                return render(
                    request,
                    "auctions/error.html",
                    {"error": "Item is already in your Watchlist."},
                )

    else:
        # get listing ids from watchlist database for current user
        ids = Watchlist.objects.values_list("Listing_id", flat=True).filter(user=user)

        # get listing data corresponding to the listing ids
        userWatchlist = Listing.objects.filter(id__in=ids)

        bids = Bids.objects.all()
        return render(
            request,
            "auctions/watchlist.html",
            {"userWatchlist": userWatchlist, "bids": bids},
        )


@login_required
def bid(request):
    user = request.user

    # Get bid amount or return error
    if not request.POST.get("bid"):
        return render(
            request,
            "auctions/error.html",
            {"error": "Unable to fetch bid value."},
        )
    else:
        bid = int(request.POST["bid"])

    # Get listing data or return error
    if not request.POST.get("listing"):
        return render(
            request,
            "auctions/error.html",
            {"error": "Unable to fetch listing data."},
        )
    else:
        listing = int(request.POST["listing"])

    # get starting bid for listing
    startingBid = Listing.objects.values_list("startingBid", flat=True).get(id=listing)

    # return error if bid amount is less than starting bid
    if bid < startingBid:
        return render(
            request,
            "auctions/error.html",
            {"error": "Bid cannot be less than starting bid."},
        )

    # check if a bid on the listing already exists
    if Bids.objects.filter(Listing_id=listing).exists():

        # get the bid object for listing
        b = Bids.objects.get(Listing_id=listing)

        # Update bid for listing if bid is greater than current bid
        if bid > b.amount:
            b.user = user
            b.amount = bid
            b.save()
            return HttpResponseRedirect(reverse("listing", args=(listing,)))

        else:
            return render(
                request,
                "auctions/error.html",
                {"error": "Bid cannot be less than maximum bid."},
            )

    else:

        # Submit bid to database
        newBid = Bids(user=user, Listing_id=listing, amount=bid)
        newBid.save()

        return HttpResponseRedirect(reverse("listing", args=(listing,)))


@login_required
def close(request):

    # Get listing data or return error
    if not request.POST.get("listing"):
        return render(
            request,
            "auctions/error.html",
            {"error": "Unable to fetch listing data."},
        )
    else:
        listing = int(request.POST["listing"])

    # Get listing database object and set active to False
    l = Listing.objects.get(id=listing)
    l.active = False

    # If there was a bid on the listing, set listing winner to the user who bid.
    if Bids.objects.filter(Listing_id=listing).exists():

        b = Bids.objects.get(Listing_id=listing)

        l.winner = b.user

    # Save modified listing object
    l.save()

    return HttpResponseRedirect(reverse("listing", args=(listing,)))


@login_required
def comment(request):

    # get logged in user
    user = request.user

    # Get comment data or return error
    if not request.POST.get("comment"):
        return render(
            request,
            "auctions/error.html",
            {"error": "Unable to fetch Comment."},
        )
    else:
        comment = request.POST["comment"]

    # Get listing data or return error
    if not request.POST.get("listing"):
        return render(
            request,
            "auctions/error.html",
            {"error": "Unable to fetch listing data."},
        )
    else:
        listing = int(request.POST["listing"])

    # Create and save new comment database object
    newComment = Comments(user=user, Listing_id=listing, comment=comment)
    newComment.save()

    return HttpResponseRedirect(reverse("listing", args=(listing,)))


def categories(request):

    # Get all categories from database
    categories = Category.objects.all()

    return render(request, "auctions/categories.html", {"categories": categories})


def category(request, name):

    # Get category object with name in url
    category = Category.objects.get(name=name)

    # Get all listings that have the requested category
    listings = Listing.objects.filter(category=category, active=True)
    bids = Bids.objects.all()

    return render(
        request,
        "auctions/category.html",
        {"listings": listings, "category": category, "bids": bids},
    )
