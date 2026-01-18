from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, ValidationError

from .auth_client import AuthClient, AuthClientError
from .models import UserProfile, Address, Card
from .serializers import (
    UserProfileSerializer,
    AddressSerializer,
    CardSerializer
)

auth_client = AuthClient()


# ------------------------------------------------------------------
# Success Response Helper (MANDATORY FORMAT)
# ------------------------------------------------------------------
def success_response(data, status_code=status.HTTP_200_OK):
    return Response(
        {
            "success": True,
            "data": data
        },
        status=status_code
    )


# ------------------------------------------------------------------
# Authentication Helper
# ------------------------------------------------------------------
def get_authenticated_user(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise NotAuthenticated("Authorization token missing.")

    token = auth_header.split(" ")[1]

    try:
        return auth_client.get_user(token)
    except AuthClientError:
        raise NotAuthenticated("Invalid or expired token.")


# ------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------
class HealthCheckView(APIView):

    def get(self, request):
        return success_response(
            {"status": "Profile_MS is running"}
        )


# ------------------------------------------------------------------
# AUTH_MS Connectivity Test
# ------------------------------------------------------------------
class TestAuthView(APIView):

    def get(self, request):
        user_data = get_authenticated_user(request)

        return success_response({
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "person_id": user_data.get("person_id"),
        })


# ------------------------------------------------------------------
# User Profile
# ------------------------------------------------------------------
class UserProfileView(APIView):

    def get(self, request):
        user_data = get_authenticated_user(request)

        person_id = user_data.get("person_id") or user_data.get("id")
        email = user_data.get("email")

        if not person_id:
            raise ValidationError("person_id missing from Auth MS response.")

        profile, _ = UserProfile.objects.get_or_create(
            person_id=person_id,
            defaults={"email": email}
        )

        return success_response(
            UserProfileSerializer(profile).data
        )

    def put(self, request):
        user_data = get_authenticated_user(request)

        person_id = user_data.get("person_id") or user_data.get("id")
        email = user_data.get("email")

        if not person_id:
            raise ValidationError("person_id missing from Auth MS response.")

        profile, _ = UserProfile.objects.get_or_create(
            person_id=person_id,
            defaults={"email": email}
        )

        data = request.data.copy()
        data.pop("email", None)
        data.pop("person_id", None)

        serializer = UserProfileSerializer(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(serializer.data)


# ------------------------------------------------------------------
# Address Management
# ------------------------------------------------------------------
class AddressListCreateView(APIView):

    def get(self, request):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        serializer = AddressSerializer(profile.addresses.all(), many=True)

        return success_response(serializer.data)

    def post(self, request):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=profile)

        return success_response(
            serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class AddressDetailView(APIView):

    def get_object(self, pk, profile):
        try:
            return profile.addresses.get(pk=pk)
        except Address.DoesNotExist:
            raise ValidationError("Address not found.")

    def get(self, request, pk):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        address = self.get_object(pk, profile)

        return success_response(
            AddressSerializer(address).data
        )

    def put(self, request, pk):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        address = self.get_object(pk, profile)

        serializer = AddressSerializer(address, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(serializer.data)

    def delete(self, request, pk):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        address = self.get_object(pk, profile)
        address.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------------
# Card Management
# ------------------------------------------------------------------
class CardListCreateView(APIView):

    def get(self, request):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        serializer = CardSerializer(profile.cards.all(), many=True)

        return success_response(serializer.data)

    def post(self, request):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])

        if profile.cards.count() >= 4:
            raise ValidationError("Maximum 4 cards allowed.")

        serializer = CardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=profile)

        return success_response(
            serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class CardDetailView(APIView):

    def get_object(self, pk, profile):
        try:
            return profile.cards.get(pk=pk)
        except Card.DoesNotExist:
            raise ValidationError("Card not found.")

    def get(self, request, pk):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        card = self.get_object(pk, profile)

        return success_response(
            CardSerializer(card).data
        )

    def put(self, request, pk):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        card = self.get_object(pk, profile)

        serializer = CardSerializer(card, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(serializer.data)

    def delete(self, request, pk):
        user_data = get_authenticated_user(request)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        card = self.get_object(pk, profile)
        card.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
