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
    # image to pdf converters
    ('jpeg', 'pdf'): convert_image_to_pdf, #support multiple images
    ('jpg', 'pdf'): convert_image_to_pdf, #support multiple images
    ('png', 'pdf'): convert_image_to_pdf, #support multiple images
    ('webp', 'pdf'): convert_image_to_pdf, #support multiple images
    # image converters
    ('jpeg', 'png'): convert_jpeg_to_png,
    ('jpeg', 'webp'): convert_image_to_webp,
    ('jpg', 'png'): convert_jpeg_to_png,
    ('jpg', 'webp'): convert_image_to_webp,
    ('png', 'jpeg'): convert_png_to_jpeg,
    ('png', 'jpg'): convert_png_to_jpeg,
    ('png', 'webp'): convert_image_to_webp,
    ('webp', 'jpeg'): convert_webp_to_jpeg,
    ('webp', 'jpg'): convert_webp_to_jpeg,
    ('webp', 'png'): convert_webp_to_png,
}

__all__ = [
    'CONVERTER_MAP',
    'convert_pdf_to_word',
    'convert_pdf_to_image',
    'convert_image_to_pdf',
    'convert_jpeg_to_png',
    'convert_png_to_jpeg',
    'convert_image_to_webp',
    'convert_webp_to_jpeg',
    'convert_webp_to_png',
]
