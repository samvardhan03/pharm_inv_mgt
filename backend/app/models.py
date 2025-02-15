from djongo import models
import uuid
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator

class Supplier(models.Model):
    """
    Supplier details for medicines.
    """
    supplier_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField(max_length=255, unique=True)
    contact_phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    MongoDB model for storing pharmacy inventory.
    """
    product_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(
        max_length=50,
        choices=[("Tablet", "Tablet"), ("Liquid", "Liquid"), ("Misc", "Misc")]
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    batch_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    total_units = models.PositiveIntegerField(default=0)
    damaged_units = models.PositiveIntegerField(default=0)
    damages = models.JSONField(default=list)  # Example: ["Expired", "Physical Damage"]
    image = models.ImageField(upload_to="inventory_images/", null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Storage Conditions
    storage_temp = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(-20), MaxValueValidator(50)]
    )  # Allowed range: -20°C to 50°C
    storage_humidity = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # Allowed range: 0% to 100%

    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def damage_percentage(self):
        """Returns the percentage of damaged units."""
        if self.total_units == 0:
            return 0
        return round((self.damaged_units / self.total_units) * 100, 2)

    def is_expired(self):
        """Checks if the medicine is expired."""
        return self.expiry_date and self.expiry_date < now().date()

    def storage_status(self):
        """Returns if the storage temperature and humidity are within range."""
        if self.category not in STORAGE_CONDITIONS:
            return True  # If no conditions defined, assume it's OK
        ideal_conditions = STORAGE_CONDITIONS[self.category]
        temp_ok = (self.storage_temp is None) or (ideal_conditions["temp_range"][0] <= self.storage_temp <= ideal_conditions["temp_range"][1])
        humidity_ok = (self.storage_humidity is None) or (ideal_conditions["humidity_range"][0] <= self.storage_humidity <= ideal_conditions["humidity_range"][1])
        return temp_ok and humidity_ok

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.total_units} units"

    class Meta:
        ordering = ["-updated_at"]  # Sort by most recently updated


# Define ideal storage conditions for each medicine category
STORAGE_CONDITIONS = {
    "Tablet": {"temp_range": (15, 25), "humidity_range": (30, 50)},  # Celsius, Percentage
    "Liquid": {"temp_range": (2, 8), "humidity_range": (20, 40)},   # Refrigerator
    "Misc": {"temp_range": (10, 30), "humidity_range": (20, 60)}
}
