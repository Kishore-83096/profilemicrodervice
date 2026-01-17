from django.urls import path
from .views import (
    HealthCheckView,
    TestAuthView,
    UserProfileView,
    AddressListCreateView,
    AddressDetailView,
    CardListCreateView,
    CardDetailView
)

urlpatterns = [
    # ----------------------
    # Health & Test
    # ----------------------
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("test-auth/", TestAuthView.as_view(), name="test-auth"),

    # ----------------------
    # UserProfile
    # ----------------------
    path("profile/", UserProfileView.as_view(), name="user-profile"),

    # ----------------------
    # Address CRUD
    # ----------------------
    path("addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),

    # ----------------------
    # Card CRUD
    # ----------------------
    path("cards/", CardListCreateView.as_view(), name="card-list-create"),
    path("cards/<int:pk>/", CardDetailView.as_view(), name="card-detail"),
]
