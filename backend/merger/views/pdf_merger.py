import io
import os
from pypdf import PdfWriter

def merge_pdfs(files):
    """
    Merges multiple PDF files into one.
    
    Args:
        files: List of file-like objects (e.g. UploadedFile)
        
    Returns:
        tuple: (output_buffer, output_filename, content_type)
    """
    writer = PdfWriter()
    
    for file in files:
        file.seek(0)
        writer.append(file)
    
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    
    # Generate filename based on the first file name + postfix
    first_file_name = files[0].name
    base_name, _ = os.path.splitext(first_file_name)
    output_filename = f"{base_name}_merged.pdf"
    
    content_type = 'application/pdf'
    
    return output_buffer, output_filename, content_type
