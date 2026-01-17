from rest_framework import serializers
from .models import UserProfile, Address, Card

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "person_id", "email", "alternate_email",
            "primary_phone", "alternate_phone",
            "primary_country_code", "alternate_country_code",
            "first_name", "last_name", "date_of_birth", "gender"
        ]
        read_only_fields = ["person_id", "email"]

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_card_brand(self, value):
        card_type = self.initial_data.get("card_type")
        if card_type == "credit" and value not in dict(Card.CREDIT_CARD_BRANDS):
            raise serializers.ValidationError("Invalid credit card brand.")
        if card_type == "debit" and value not in dict(Card.DEBIT_CARD_BRANDS):
            raise serializers.ValidationError("Invalid debit card brand.")
        return value
