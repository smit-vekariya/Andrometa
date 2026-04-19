import io
import os
import tempfile
from pdf2docx import Converter as Pdf2DocxConverter
import fitz  # PyMuPDF
from PIL import Image
import zipfile


def convert_pdf_to_word(file):
    """
    Convert a PDF file to DOCX format using pdf2docx.
    Returns a tuple of (file_bytes, output_filename).
    """
    original_name = os.path.splitext(file.name)[0]
    output_filename = f"{original_name}.docx"

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        for chunk in file.chunks():
            temp_pdf.write(chunk)
        temp_pdf_path = temp_pdf.name

    temp_docx_path = temp_pdf_path.replace('.pdf', '.docx')

    try:
        converter = Pdf2DocxConverter(temp_pdf_path)
        converter.convert(temp_docx_path)
        converter.close()

        with open(temp_docx_path, 'rb') as docx_file:
            file_bytes = docx_file.read()

        return io.BytesIO(file_bytes), output_filename, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    finally:
        if os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)
        if os.path.exists(temp_docx_path):
            os.unlink(temp_docx_path)


def convert_pdf_to_image(file):
    """
    Convert a PDF file to PNG images using PyMuPDF (fitz).
    If single page, returns a PNG. If multi-page, returns a ZIP of PNGs.
    Returns a tuple of (file_bytes, output_filename, content_type).
    """
    original_name = os.path.splitext(file.name)[0]
    pdf_bytes = file.read()

    doc = fitz.open("pdf", pdf_bytes)

    if len(doc) == 1:
        page = doc.load_page(0)
        pix = page.get_pixmap()
        output_buffer = io.BytesIO(pix.tobytes("png"))
        output_filename = f"{original_name}.png"
        return output_buffer, output_filename, 'image/png'
    else:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for index in range(len(doc)):
                page = doc.load_page(index)
                pix = page.get_pixmap(dpi=150) # use a decent dpi
                zip_file.writestr(f"{original_name}_page_{index + 1}.png", pix.tobytes("png"))

        zip_buffer.seek(0)
        output_filename = f"{original_name}_images.zip"
        return zip_buffer, output_filename, 'application/zip'


def convert_pdf_to_jpeg(file):
    """
    Convert a PDF file to JPEG images using PyMuPDF (fitz).
    If single page, returns a JPEG. If multi-page, returns a ZIP of JPEGs.
    Returns a tuple of (file_bytes, output_filename, content_type).
    """
    original_name = os.path.splitext(file.name)[0]
    pdf_bytes = file.read()

    doc = fitz.open("pdf", pdf_bytes)

    if len(doc) == 1:
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        output_buffer = io.BytesIO(pix.tobytes("jpeg"))
        output_filename = f"{original_name}.jpg"
        return output_buffer, output_filename, 'image/jpeg'
    else:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for index in range(len(doc)):
                page = doc.load_page(index)
                pix = page.get_pixmap(dpi=150) # use a decent dpi
                zip_file.writestr(f"{original_name}_page_{index + 1}.jpg", pix.tobytes("jpeg"))

        zip_buffer.seek(0)
        output_filename = f"{original_name}_images.zip"
        return zip_buffer, output_filename, 'application/zip'


def convert_pdf_to_txt(file):
    """
    Extract text content from a PDF file using PyMuPDF (fitz).
    Returns a tuple of (file_bytes, output_filename, content_type).
    """
    original_name = os.path.splitext(file.name)[0]
    output_filename = f"{original_name}.txt"

    pdf_bytes = file.read()
    doc = fitz.open("pdf", pdf_bytes)

    full_text = ""
    for page in doc:
        full_text += page.get_text()

    doc.close()

    output_buffer = io.BytesIO(full_text.encode('utf-8'))
    output_buffer.seek(0)

    return output_buffer, output_filename, 'text/plain'
