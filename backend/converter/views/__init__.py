from .pdf_converter import convert_pdf_to_word, convert_pdf_to_image, convert_pdf_to_txt
from .image_to_pdf import convert_image_to_pdf
from .image_converter import (
    convert_image_to_png,
    convert_image_to_jpeg,
    convert_image_to_webp,
)

# Dispatch map: (file_type_from, file_type_to) -> converter function
CONVERTER_MAP = {
    # pdf converters
    ('pdf', 'docx'): convert_pdf_to_word,
    ('pdf', 'png'): convert_pdf_to_image,
    ('pdf', 'txt'): convert_pdf_to_txt,

    # jpeg converters
    ('jpeg', 'pdf'): convert_image_to_pdf,
    ('jpeg', 'png'): convert_image_to_png,
    ('jpeg', 'webp'): convert_image_to_webp,
    ('jpeg', 'jpg'): convert_image_to_jpeg,

    # jpg converters
    ('jpg', 'png'): convert_image_to_png,
    ('jpg', 'pdf'): convert_image_to_pdf,
    ('jpg', 'webp'): convert_image_to_webp,
    ('jpg', 'jpeg'): convert_image_to_jpeg,

    # png converters
    ('png', 'pdf'): convert_image_to_pdf,
    ('png', 'jpeg'): convert_image_to_jpeg,
    ('png', 'jpg'): convert_image_to_jpeg,
    ('png', 'webp'): convert_image_to_webp,

    # webp converters
    ('webp', 'pdf'): convert_image_to_pdf,
    ('webp', 'jpeg'): convert_image_to_jpeg,
    ('webp', 'jpg'): convert_image_to_jpeg,
    ('webp', 'png'): convert_image_to_png,

    # bmp converters
    ('bmp', 'pdf'): convert_image_to_pdf,
    ('bmp', 'jpeg'): convert_image_to_jpeg,
    ('bmp', 'jpg'): convert_image_to_jpeg,
    ('bmp', 'png'): convert_image_to_png,
    ('bmp', 'webp'): convert_image_to_webp,

    # tiff converters
    ('tiff', 'pdf'): convert_image_to_pdf,
    ('tiff', 'jpeg'): convert_image_to_jpeg,
    ('tiff', 'jpg'): convert_image_to_jpeg,
    ('tiff', 'png'): convert_image_to_png,
    ('tiff', 'webp'): convert_image_to_webp,

    # gif converters
    ('gif', 'pdf'): convert_image_to_pdf,
    ('gif', 'jpeg'): convert_image_to_jpeg,
    ('gif', 'jpg'): convert_image_to_jpeg,
    ('gif', 'png'): convert_image_to_png,
    ('gif', 'webp'): convert_image_to_webp,
}

AVAILABLE_FORMATS = {
    # pdf
    "pdf": ["docx", "png", "txt"],
    
    # images
    "jpeg": ["pdf", "png", "webp", "jpg"],
    "jpg": ["pdf", "png", "webp", "jpeg"],
    "png": ["pdf", "jpeg", "jpg", "webp"],
    "webp": ["pdf", "jpeg", "jpg", "png"],
    "bmp": ["pdf", "jpeg", "jpg", "png", "webp"],
    "tiff": ["pdf", "jpeg", "jpg", "png", "webp"],
    "gif": ["pdf", "jpeg", "jpg", "png", "webp"],
}

__all__ = [
    'CONVERTER_MAP',
    'AVAILABLE_FORMATS',
    'convert_pdf_to_word',
    'convert_pdf_to_image',
    'convert_pdf_to_txt',
    'convert_image_to_pdf',
    'convert_image_to_png',
    'convert_image_to_jpeg',
    'convert_image_to_webp',
]
