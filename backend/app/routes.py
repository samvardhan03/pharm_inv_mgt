from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
import os
import ml_model
from .models import Product
from .schemas import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD API for pharmacy inventory management.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

@api_view(["POST"])
def upload_inventory_image(request):
    """
    Uploads an inventory image, runs YOLO detection, and filters medicines
    based on expiry dates and storage conditions.
    """
    try:
        file = request.FILES.get("file")
        storage_temp = request.data.get("storage_temp", None)
        storage_humidity = request.data.get("storage_humidity", None)

        if not file:
            return Response({"error": "No file provided"}, status=400)

        file_path = default_storage.save(f"inventory_images/{file.name}", file)
        detections = ml_model.detect_objects(
            os.path.join("media", file_path),
            storage_temp=float(storage_temp) if storage_temp else None,
            storage_humidity=float(storage_humidity) if storage_humidity else None
        )

        return Response({"detections": detections})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
