"""
File upload validators.

Applied at the model level so they fire on both the
admin dashboard and any API endpoint that accepts file uploads.
"""
import os
from django.core.exceptions import ValidationError
from PIL import Image


# Maximum file sizes
MAX_IMAGE_SIZE_MB = 5
MAX_FILE_SIZE_MB  = 10


def validate_image_file(file):
    """
    Validates uploaded image files.

    Checks:
    1. File extension is in the allowed list
    2. File size does not exceed the limit
    3. File is actually a valid image (PIL can open it)
       — this prevents files disguised as images
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    ext = os.path.splitext(file.name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file type '{ext}'. "
            f"Allowed types: {', '.join(allowed_extensions)}"
        )

    max_size = MAX_IMAGE_SIZE_MB * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(
            f"Image file too large. "
            f"Maximum size is {MAX_IMAGE_SIZE_MB}MB."
        )

    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        raise ValidationError(
            "Invalid image file. "
            "The file could not be opened as an image."
        )
    finally:
        # Reset file pointer after PIL reads it
        file.seek(0)


def validate_pdf_file(file):
    """
    Validates uploaded PDF files.

    Checks:
    1. File extension is .pdf
    2. File size does not exceed the limit
    3. File starts with the PDF magic bytes (%PDF-)
       — this prevents non-PDF files being renamed to .pdf
    """
    ext = os.path.splitext(file.name)[1].lower()

    if ext != '.pdf':
        raise ValidationError(
            "Only PDF files are allowed for resume upload."
        )

    max_size = MAX_FILE_SIZE_MB * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(
            f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB."
        )

    # Read first 5 bytes and check for PDF magic number
    header = file.read(5)
    file.seek(0)

    if header != b'%PDF-':
        raise ValidationError(
            "File does not appear to be a valid PDF."
        )