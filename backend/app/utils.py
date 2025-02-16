import base64

def encode_image(image_path):
    """Converts an image to base64 for Gemini API."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
