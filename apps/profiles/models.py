from django.db import models
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    # Auth info from AUTH_MS
    person_id = models.IntegerField(unique=True)
    email = models.EmailField(unique=True)

    # Alternate contacts
    alternate_email = models.EmailField(blank=True, null=True)

    phone_regex = RegexValidator(
        regex=r'^\d{10}$', message="Phone number must be 10 digits."
    )
    primary_phone = models.CharField(validators=[phone_regex], max_length=10, blank=True, null=True)
    alternate_phone = models.CharField(validators=[phone_regex], max_length=10, blank=True, null=True)

    # Country code
    COUNTRY_CODE_CHOICES = [
        ("+91", "India"), ("+1", "USA"), ("+44", "UK"), ("+61", "Australia"),
        ("+81", "Japan"), ("+49", "Germany"), ("+86", "China"), ("+33", "France"),
        ("+7", "Russia"), ("+971", "UAE")
    ]
    primary_country_code = models.CharField(max_length=5, choices=COUNTRY_CODE_CHOICES, default="+91")
    alternate_country_code = models.CharField(max_length=5, choices=COUNTRY_CODE_CHOICES, default="+91")

    # Personal info
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Other")]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [("home", "Home"), ("work", "Work"), ("friend", "Friend"), ("other", "Other")]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)

    COUNTRY_CHOICES = [("IN", "India"), ("US", "USA"), ("UK", "UK"), ("AU", "Australia"), ("JP", "Japan")]
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default="IN")

    STATE_CHOICES = [("MH", "Maharashtra"), ("DL", "Delhi"), ("KA", "Karnataka"), ("CA", "California")]
    state = models.CharField(max_length=3, choices=STATE_CHOICES, default="MH")

    CITY_CHOICES = [("MUM", "Mumbai"), ("BLR", "Bangalore"), ("DEL", "Delhi"), ("LA", "Los Angeles")]
    city = models.CharField(max_length=4, choices=CITY_CHOICES, default="MUM")

    zip_code = models.CharField(max_length=20, blank=True)

    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Phone number must be 10 digits.")
    phone_number = models.CharField(validators=[phone_regex], max_length=10, blank=True, null=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "address_type")

    def __str__(self):
        return f"{self.user.email} - {self.address_type}"


class Card(models.Model):
    CARD_TYPE_CHOICES = [("credit", "Credit"), ("debit", "Debit")]

    CREDIT_CARD_BRANDS = [("visa", "Visa"), ("mastercard", "MasterCard"), ("amex", "American Express"), ("discover", "Discover")]
    DEBIT_CARD_BRANDS = [("visa_debit", "Visa Debit"), ("master_debit", "MasterCard Debit"), ("maestro", "Maestro"), ("rupay", "Rupay")]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="cards")
    card_type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES)
    card_brand = models.CharField(max_length=20)
    card_number = models.CharField(max_length=16)
    card_holder_name = models.CharField(max_length=150)
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.user.cards.count() >= 4:
            raise ValueError("Maximum 4 cards allowed per user.")
        if self.card_type == "credit" and self.card_brand not in dict(self.CREDIT_CARD_BRANDS):
            raise ValueError("Invalid credit card brand.")
        if self.card_type == "debit" and self.card_brand not in dict(self.DEBIT_CARD_BRANDS):
            raise ValueError("Invalid debit card brand.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.card_type.title()} - {self.card_brand.title()} ({self.card_holder_name})"
