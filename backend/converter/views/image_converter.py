import io
import os
from PIL import Image
import img2pdf


def convert_image_to_png(file):
    """
    Convert any image to PNG format using Pillow.
    Returns a tuple of (file_bytes, output_filename, content_type).
    """
    original_name = os.path.splitext(file.name)[0]
    output_filename = f"{original_name}.png"

    image = Image.open(file)
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='PNG')
    output_buffer.seek(0)

    return output_buffer, output_filename, 'image/png'


def convert_image_to_jpeg(file):
    """
    Convert any image to JPEG format using Pillow.
    Handles transparency by compositing onto a white background.
    Returns a tuple of (file_bytes, output_filename, content_type).
    """
    original_name = os.path.splitext(file.name)[0]
    output_filename = f"{original_name}.jpg"

    image = Image.open(file)

    # JPEG doesn't support transparency, composite onto white background
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background

    output_buffer = io.BytesIO()
    image.save(output_buffer, format='JPEG', quality=95)
    output_buffer.seek(0)

    return output_buffer, output_filename, 'image/jpeg'


def convert_image_to_webp(file):
    """
    Convert any image to WEBP format using Pillow.
    Returns a tuple of (file_bytes, output_filename, content_type).
    """
    original_name = os.path.splitext(file.name)[0]
    output_filename = f"{original_name}.webp"

    image = Image.open(file)
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='WEBP', quality=90)
    output_buffer.seek(0)

    return output_buffer, output_filename, 'image/webp'


