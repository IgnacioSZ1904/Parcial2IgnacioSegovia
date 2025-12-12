import cloudinary.uploader
import os

def upload_image(file):
    result = cloudinary.uploader.upload(file.file)
    return result["secure_url"]
