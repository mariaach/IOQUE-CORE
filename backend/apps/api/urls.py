from django.urls import path, include

urlpatterns = [
    path("", include("apps.catalog.categories.urls")),
    path("", include("apps.catalog.products.urls")),
    path("", include("apps.contact.urls")),
]
