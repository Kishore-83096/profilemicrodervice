# Create your views here.
from rest_framework.views import APIView
from .auth_client import AuthClient, AuthClientError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Address, Card
from .serializers import UserProfileSerializer, AddressSerializer, CardSerializer
from .auth_client import AuthClient, AuthClientError

auth_client = AuthClient()


class HealthCheckView(APIView):
    def get(self, request):
        return Response(
            {"status": "Profile_MS is running"},
            status=status.HTTP_200_OK
        )




class TestAuthView(APIView):
    def get(self, request):
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        try:
            user_data = auth_client.get_user(token)
            return Response({
                "message": "Profile_MS successfully connected to AUTH_MS",
                "user": user_data
            })
        except AuthClientError as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Address, Card
from .serializers import UserProfileSerializer, AddressSerializer, CardSerializer
from .auth_client import AuthClient, AuthClientError

auth_client = AuthClient()


def get_authenticated_user(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        return auth_client.get_user(token)
    except AuthClientError:
        return None


class UserProfileView(APIView):
    def get(self, request):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile, _ = UserProfile.objects.get_or_create(
            person_id=user_data["person_id"], defaults={"email": user_data["email"]}
        )
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile, _ = UserProfile.objects.get_or_create(
            person_id=user_data["person_id"], defaults={"email": user_data["email"]}
        )
        data = request.data.copy()
        data.pop("email", None)
        data.pop("person_id", None)

        serializer = UserProfileSerializer(profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(APIView):
    def get(self, request):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        serializer = AddressSerializer(profile.addresses.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
    def get_object(self, pk, profile):
        return profile.addresses.get(pk=pk)

    def get(self, request, pk):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        try:
            address = self.get_object(pk, profile)
        except Address.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def put(self, request, pk):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        try:
            address = self.get_object(pk, profile)
        except Address.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        try:
            address = self.get_object(pk, profile)
        except Address.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CardListCreateView(APIView):
    def get(self, request):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        serializer = CardSerializer(profile.cards.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        if profile.cards.count() >= 4:
            return Response({"error": "Maximum 4 cards allowed"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardDetailView(APIView):
    def get_object(self, pk, profile):
        return profile.cards.get(pk=pk)

    def get(self, request, pk):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        try:
            card = self.get_object(pk, profile)
        except Card.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CardSerializer(card)
        return Response(serializer.data)

    def put(self, request, pk):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        try:
            card = self.get_object(pk, profile)
        except Card.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CardSerializer(card, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_data = get_authenticated_user(request)
        if not user_data:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(person_id=user_data["person_id"])
        try:
            card = self.get_object(pk, profile)
        except Card.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
