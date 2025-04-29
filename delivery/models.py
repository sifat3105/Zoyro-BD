from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User




class DeliverySettings(models.Model):
    maxbuy = models.PositiveIntegerField(default=2000)

    def save(self, *args, **kwargs):
        self.pk = 1  # Force only one instance
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion

    @classmethod
    def get(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj



class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, verbose_name="DeliveryUser", on_delete=models.CASCADE, related_name="address")
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]

    # Contact Information
    full_name = models.CharField(max_length=100, verbose_name="Full Name")
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+8801XXXXXXXXX'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name="Phone Number"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="Email")

    # Address Type
    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES,
        default='home',
        verbose_name="Address Type"
    )

    # Location Information
    division = models.CharField(max_length=50, verbose_name="Division")
    district = models.CharField(max_length=50, verbose_name="District")
    upazila = models.CharField(max_length=50, verbose_name="Upazila/Thana")
    postal_code = models.CharField(max_length=10, verbose_name="Postal Code")

    # Address Details
    delivery_area = models.CharField(max_length=100, verbose_name="Delivery Area")

    # Additional Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False, verbose_name="Default Address")

    class Meta:
        verbose_name = "Delivery Address"
        verbose_name_plural = "Delivery Addresses"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.get_address_type_display()} - {self.district}"

    def get_full_address(self):
        return (
            f" {self.delivery_area}, {self.upazila} "
            f" {self.district}, {self.division} - {self.postal_code} "
        )
    def save(self, *args, **kwargs):
        
        if self.is_default and self.user:
            DeliveryAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)