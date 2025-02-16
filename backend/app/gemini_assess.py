import os
import base64
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel
import PIL.Image

# Load environment variables from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Gemini API Key is missing! Please set it in the .env file.")

#  Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

class Date(BaseModel):
    """Schema for extracted expiry date."""
    day: int | None
    month: int | None
    year: int | None

class ProductAssessment(BaseModel):
    """Schema for product assessment."""
    expiry_date: Date | str  # 'NA' if not detected
    damaged: bool
    opened: bool

def encode_image(image_path):
    """Convert an image to base64 for API compatibility."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def assess_product(image_path: str):
    """
    Sends an image to Gemini API and extracts expiry date, damage status, and opened status.
    """
    image_base64 = encode_image(image_path)

    response = model.generate_content([
        "Extract the expiry date, check if the product is damaged, and if it is opened. If Expiry Date is not present, return 'NA'.",
        {"type": "image", "data": image_base64}
    ])

    return response.text
