import os
import uuid
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

class CloudinaryClient:
    # بيانات الاتصال ثابتة
    CLOUD_NAME = "djnzgba9h"
    API_KEY = "462835281986351"
    API_SECRET = "1cgqd7yDwo1YwSvm76sSqfkhH-E"  # استبدلها

    def __init__(self):
        cloudinary.config(
            cloud_name=self.CLOUD_NAME,
            api_key=self.API_KEY,
            api_secret=self.API_SECRET,
            secure=True
        )

    def generate_unique_public_id(self, prefix="img"):
        unique_id = uuid.uuid4().hex
        return f"{prefix}_{unique_id}"

    def upload_image(self, image_path_or_url):
        # محاولة استخراج اسم الملف بدون امتداد من الرابط أو المسار

        # base_name = os.path.basename(image_path_or_url)
        # public_id, ext = os.path.splitext(base_name)
        # if not public_id:  # لو الاسم فاضي (مثلاً رابط بدون اسم ملف)
        public_id = self.generate_unique_public_id()
        
        # رفع الصورة مع public_id المستخرج أو المولد
        result = cloudinary.uploader.upload(image_path_or_url, public_id=public_id,resorcese_type="image")
        return result.get("secure_url"), public_id

    # ميثود جلب رابط الصورة كما في السابق
    def get_image_url(self, public_id, width=None, height=None, crop=None, gravity=None, fetch_format="auto", quality="auto"):
        url, _ = cloudinary_url(
            public_id,
            width=width,
            height=height,
            crop=crop,
            gravity=gravity,
            fetch_format=fetch_format,
            quality=quality
        )
        return url
    


if __name__ == "__main__":
    client = CloudinaryClient()

    uploaded_url, public_id = client.upload_image("app/services/IMG_9935.JPG")
    print("Uploaded Image URL:", uploaded_url)
    print("Public ID used:", public_id)