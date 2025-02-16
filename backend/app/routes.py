from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
import os
from app.gemini_assess import assess_product
from app.models import Product
from app.schemas import ProductSerializer

@api_view(["POST"])
def process_medicine_image(request):
    """
    Uploads an image, sends it to Gemini API, and returns expiry & damage info.
    """
    try:
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided"}, status=400)

        # Save uploaded file temporarily
        file_path = default_storage.save(f"uploads/{file.name}", file)

        # Process with Gemini API
        assessment_result = assess_product(os.path.join("media", file_path))

        return Response({"assessment": assessment_result}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
def list_products(request):
    """
    Fetches all medicines stored in the database.
    """
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=200)
