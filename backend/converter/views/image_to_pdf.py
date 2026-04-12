import io
import os
from PIL import Image
import img2pdf

def convert_image_to_pdf(files):
    """
    Convert image files (JPEG/PNG/WEBP) to PDF using img2pdf.
    img2pdf wraps the raw image directly into a PDF without re-encoding,
    producing smaller files and faster conversion.
    WEBP and non-supported formats are dynamically converted to JPEG in memory.
    Returns a tuple of (file_bytes, output_filename, content_type).
    """
    if not isinstance(files, list):
        files = [files]

    original_name = os.path.splitext(files[0].name)[0]
    output_filename = f"{original_name}.pdf"

    image_bytes_list = []
    
    for file in files:
        file.seek(0)
        img_bytes = file.read()
        
        try:
            # Check if image needs conversion for img2pdf (e.g. WEBP)
            img = Image.open(io.BytesIO(img_bytes))
            if img.format not in ['JPEG', 'PNG']:
                # Convert to JPEG for img2pdf compatibility
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                else:
                    img = img.convert('RGB')
                    
                temp_buffer = io.BytesIO()
                img.save(temp_buffer, format='JPEG', quality=95)
                img_bytes = temp_buffer.getvalue()
        except:
            pass # fallback to original bytes if pillow fails, img2pdf will try its best
            
        image_bytes_list.append(img_bytes)

    pdf_bytes = img2pdf.convert(image_bytes_list)

    output_buffer = io.BytesIO(pdf_bytes)
    output_buffer.seek(0)

    return output_buffer, output_filename, 'application/pdf'
