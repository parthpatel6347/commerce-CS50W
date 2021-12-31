from django.contrib import admin

from .models import User, Category, Listing, Watchlist, Comments, Bids


class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "image",
        "startingBid",
        "user",
        "category",
    )


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Watchlist)
admin.site.register(Comments)
admin.site.register(Bids)
