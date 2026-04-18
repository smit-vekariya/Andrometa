from .pdf_converter import convert_pdf_to_word, convert_pdf_to_image
from .image_to_pdf import convert_image_to_pdf
from .image_converter import (
    convert_jpeg_to_png,
    convert_png_to_jpeg,
    convert_image_to_webp,
    convert_webp_to_jpeg,
    convert_webp_to_png,
)

# Dispatch map: (file_type_from, file_type_to) -> converter function
CONVERTER_MAP = {
    # pdf converters
    ('pdf', 'docx'): convert_pdf_to_word,
    ('pdf', 'png'): convert_pdf_to_image,
    # jpeg converters
    ('jpeg', 'pdf'): convert_image_to_pdf,
    ('jpeg', 'png'): convert_jpeg_to_png,
    ('jpeg', 'webp'): convert_image_to_webp,
    # jpg converters
    ('jpg', 'png'): convert_jpeg_to_png,
    ('jpg', 'pdf'): convert_image_to_pdf,
    ('jpg', 'webp'): convert_image_to_webp,
    # png converters
    ('png', 'pdf'): convert_image_to_pdf,
    ('png', 'jpeg'): convert_png_to_jpeg,
    ('png', 'jpg'): convert_png_to_jpeg,
    ('png', 'webp'): convert_image_to_webp,
    # webp converters
    ('webp', 'pdf'): convert_image_to_pdf,
    ('webp', 'jpeg'): convert_webp_to_jpeg,
    ('webp', 'jpg'): convert_webp_to_jpeg,
    ('webp', 'png'): convert_webp_to_png,
}

AVAILABLE_FORMATS = {
    "pdf": ["docx", "png"],
    "jpeg": ["pdf", "png", "webp"],
    "jpg": ["pdf", "png", "webp"],
    "png": ["pdf", "jpeg", "jpg", "webp"],
    "webp": ["pdf", "jpeg", "jpg", "png"]
}

__all__ = [
    'CONVERTER_MAP',
    'AVAILABLE_FORMATS',
    'convert_pdf_to_word',
    'convert_pdf_to_image',
    'convert_image_to_pdf',
    'convert_jpeg_to_png',
    'convert_png_to_jpeg',
    'convert_image_to_webp',
    'convert_webp_to_jpeg',
    'convert_webp_to_png',
]
