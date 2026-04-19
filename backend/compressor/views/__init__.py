from .image_compressor import compress_image

COMPRESSOR_FORMATS = {
    "image": ["jpeg", "jpg", "png", "webp", "bmp", "tiff", "gif", "heic"]
}

__all__ = ['compress_image', 'COMPRESSOR_FORMATS']

