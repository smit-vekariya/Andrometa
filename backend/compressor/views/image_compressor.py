import io
import os
import zipfile
from PIL import Image

def compress_single_image(file_bytes, mode, value=None, original_filename="", unit="KB"):
    img = Image.open(io.BytesIO(file_bytes))
    output_format = img.format if img.format in ['JPEG', 'PNG', 'WEBP'] else 'JPEG'

    if output_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background

    temp_buffer = io.BytesIO()

    if mode == 'less':
        img.save(temp_buffer, format=output_format, optimize=True, quality=90)

    elif mode == 'recommended':
        img.save(temp_buffer, format=output_format, optimize=True, quality=75)

    elif mode == 'extreme':
        img.save(temp_buffer, format=output_format, optimize=True, quality=40)

    elif mode == 'quality':
        quality_val = int(value) if value else 89
        if output_format == 'PNG':
            img.save(temp_buffer, format=output_format, optimize=True)
        else:
            img.save(temp_buffer, format=output_format, optimize=True, quality=quality_val)

    elif mode in ['target_size', 'target_percent']:
        original_size = len(file_bytes)

        target_bytes = 0
        if mode == 'target_size':
            multiplier = 1024 if unit == 'KB' else 1024 * 1024
            target_bytes = int(value * multiplier)
        else:
            pct = max(1.0, min(100.0, float(value)))
            target_bytes = int(original_size * (pct / 100.0))

        if output_format == 'PNG':
            img.save(temp_buffer, format='PNG', optimize=True)
        else:
            low_q, high_q = 10, 95
            best_buffer = None

            while low_q <= high_q:
                mid_q = (low_q + high_q) // 2
                test_buffer = io.BytesIO()
                img.save(test_buffer, format=output_format, optimize=True, quality=mid_q)
                size = test_buffer.tell()

                if size <= target_bytes:
                    best_buffer = test_buffer
                    low_q = mid_q + 1
                else:
                    high_q = mid_q - 1

            if best_buffer:
                temp_buffer = best_buffer
            else:
                img.save(temp_buffer, format=output_format, optimize=True, quality=10)

    temp_buffer.seek(0)

    base_name, original_ext = os.path.splitext(original_filename)
    extension = original_ext.lower()
    content_type = f'image/{extension.strip(".")}' if extension else f'image/{output_format.lower()}'

    return temp_buffer, f"{base_name}_compressed{extension}", content_type


def compress_image(files, mode, value=None, unit="KB"):
    if not isinstance(files, list):
        files = [files]

    if len(files) == 1:
        file = files[0]
        file.seek(0)
        file_bytes = file.read()
        return compress_single_image(file_bytes, mode, value, file.name, unit)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for index, file in enumerate(files):
            file.seek(0)
            file_bytes = file.read()
            compressed_buf, out_name, _ = compress_single_image(file_bytes, mode, value, file.name, unit)
            zip_file.writestr(out_name, compressed_buf.read())

    zip_buffer.seek(0)
    return zip_buffer, f"compressed_images.zip", 'application/zip'
