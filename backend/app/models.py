from djongo import models
import uuid
from django.utils.timezone import now

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
    total_units = models.PositiveIntegerField(default=0)
    damaged = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to="inventory_images/", null=True, blank=True)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        """Checks if the medicine is expired."""
        return self.expiry_date and self.expiry_date < now().date()

    def __str__(self):
        return f"{self.name} ({self.category}) - {'Expired' if self.is_expired() else 'Valid'}"

    class Meta:
        ordering = ["-updated_at"]  # Sort by most recently updated
