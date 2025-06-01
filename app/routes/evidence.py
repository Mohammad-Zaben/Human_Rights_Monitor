from fastapi import HTTPException
from app.services.cloudinary_config import CloudinaryClient
from app.models.evidence import EvidenceCreate
from app.database import get_collection
import os
from PIL import Image, ExifTags

async def create_evidence(image):
    """
    Process evidence by uploading the image to Cloudinary, storing the URL, and saving evidence data.

    Args:
        image_path (str): Path to the image file.
        evidence_data (dict): Dictionary containing evidence details.

    Returns:
        str: ID of the saved evidence in MongoDB.
    """
    try:
        # Initialize Cloudinary client
        cloudinary_client = CloudinaryClient()

        # Extract date captured from image metadata (if available)
        date_captured = None
        try:
            img = Image.open(image)
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    decoded_tag = ExifTags.TAGS.get(tag, tag)
                    if decoded_tag == "DateTimeOriginal":
                        date_captured = value
                        break
        except Exception as metadata_error:
            print(f"Failed to extract metadata: {metadata_error}")

        # Upload image to Cloudinary
        uploaded_url, public_id = cloudinary_client.upload_image(image)

        if not uploaded_url:
            raise HTTPException(status_code=500, detail="Failed to upload image to Cloudinary")

        # Prepare evidence data
        evidence_data = {
            "url": uploaded_url,
            "type": "image",
            "public_id": public_id,
            "date_captured": date_captured,  # Add date captured if available
        } 

        

        # Save evidence to MongoDB
        evidence_collection = await get_collection("evidence")
        result = await evidence_collection.insert_one(evidence_data)

        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to save evidence to database")

        return str(result.inserted_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))