import os
import io
from pathlib import Path
from enum import Enum, auto
from typing import Union, Optional, List, Dict, Tuple

import fitz  # PyMuPDF
import pikepdf
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from PyPDF2.generic import NameObject, NumberObject
from PyPDF2.errors import PdfReadError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .utils import convert_to_rgb

class PageNumberPosition(Enum):
    """
    Enum representing the position where the page number will be placed on each page.

    Attributes:
        Left: The page number is placed on the left side of the page.
        Right: The page number is placed on the right side of the page.
        Center: The page number is placed in the center of the page.
    """
    Left = auto()
    Right = auto()
    Center = auto()

def get_text(input_pdf: str) -> str:
    text = ''
    with fitz.open(input_pdf) as doc:
        for page in doc:
            text+= page.get_text()
    return text

def add_page_numbers(input_pdf_path: str,
                     output_pdf_path: str,
                     margin_x: int = 50,
                     margin_y: int = 30,
                     page_number_position: PageNumberPosition = PageNumberPosition.Center,
                     verbose: bool = True) -> bool:
    """
    Adds page numbers to each page of a PDF file at the specified position.

    This function reads a PDF file, adds page numbers to each page at the specified
    position, and saves the modified PDF to a new file. The position of the page number
    can be set to the left, right, or center of the page.

    Args:
        input_pdf_path (str): The path to the input PDF file that will have page numbers added.
        output_pdf_path (str): The path where the new PDF file with page numbers will be saved.
        margin_x (int): The horizontal margin (in points) from the edge of the page for the page number. Defaults to 50.
        margin_y (int): The vertical margin (in points) from the bottom of the page for the page number. Defaults to 30.
        page_number_position (PageNumberPosition): The position where the page number will be placed (Left, Right, Center). Defaults to Center.
        verbose (bool): If True, print the success or failure of the operation. Defaults to True.

    Returns:
        bool: True if the PDF was saved successfully with page numbers, False otherwise.

    Example:
        success = add_page_numbers('input.pdf', 'output.pdf', margin_x=50, margin_y=30, page_number_position=PageNumberPosition.Right, verbose=True)
        if success:
            print("Page numbers added successfully.")
        else:
            print("Failed to add page numbers.")
    """

    try:
        # Open original PDF
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()

        # Loop over all pages
        for i, page in enumerate(reader.pages, start=1):
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            page_width, _ = letter

            # Determine x position for the page number based on the specified alignment
            if page_number_position == PageNumberPosition.Left:
                x = margin_x
            elif page_number_position == PageNumberPosition.Center:
                x = page_width / 2
            elif page_number_position == PageNumberPosition.Right:
                x = page_width - margin_x

            y = margin_y  # Position from the bottom
            can.drawString(x, y, str(i))
            can.save()

            # Move to the beginning of the BytesIO buffer
            packet.seek(0)

            # Create new PDF from the ReportLab canvas content
            new_pdf = PdfReader(packet)

            # Merge the new PDF (with the page number) onto the original page
            page.merge_page(new_pdf.pages[0])

            # Add the modified page to the output PDF
            writer.add_page(page)

        # Save the resulting PDF to a file
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)

        if verbose:
            print(f"Page numbers added and saved to '{output_pdf_path}'.")
        return True

    except Exception as e:
        if verbose:
            print(f"Failed to add page numbers: {e}")
        return False

def extract_pdf_pages(input_pdf: str, output_pdf_path: str, page_indices: list[int], verbose:bool = True) -> bool:
    """
    Extracts specified pages from a PDF file and saves them to a new file.

    Args:
        input_pdf (str): Path to the input PDF file.
        output_pdf_path (str): Path to the output PDF file.
        page_indices (list[int]): A list of page indices to extract (starting from 1).
        verbose (bool): If True, prints a success message if the operation is successful.

    Returns:
        True if the output PDF was successfully written, False otherwise.
    """

    try:
        with open(input_pdf, 'rb') as in_file:
            reader = PdfReader(in_file)
            writer = PdfWriter()

            # Convert page indices to 0-based indices
            page_indices = [index - 1 for index in page_indices]

            for index in page_indices:
                if 0 <= index < len(reader.pages):
                    writer.add_page(reader.pages[index])
                else:
                    print(f"Warning: Page index {index + 1} is out of range.")

            with open(output_pdf_path, 'wb') as out_file:
                writer.write(out_file)
                if verbose:
                    print(f"Extracted PDF pages saved to '{output_pdf_path}'.")            
                return True
    except PdfReadError as e:
        if verbose:
            print(f"Error processing PDF: {e}")
        return False
    
    except FileNotFoundError:
        if verbose:
            print(f"Input file not found: {input_pdf}")
        return False
    
    except Exception as e:
        if verbose:
            print(f"Unexpected error occurred: {e}")
        return False

def split_pdf_by_page_ranges(pdf_path: str, page_ranges: List[Tuple[int, int]], output_folder: str, verbose: bool = True) -> bool:
    """
    Splits a PDF file into multiple parts based on the provided list of page ranges and saves the parts to the specified output folder.

    Args:
        pdf_path (str): The file path to the input PDF.
        page_ranges (List[Tuple[int, int]]): A list of tuples, where each tuple specifies the start and end page (inclusive) of the range. 
                                             Page offsets start at 1.
        output_folder (str): The path to the folder where the output PDFs will be saved.
        verbose (bool): If True, prints success or failure messages. Defaults to True.

    Returns:
        bool: True if all parts are successfully saved, False otherwise.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If any page range is invalid or out of bounds.
    """
    
    try:
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        # Load the PDF file
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"The PDF file does not exist: {pdf_path}")
        
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        
        for i, (start, end) in enumerate(page_ranges):
            # Validate page range
            if start < 1 or end > num_pages or start > end:
                raise ValueError(f"Invalid page range: ({start}, {end})")
            
            writer = PdfWriter()
            
            # Add specified pages to the writer
            for page_num in range(start - 1, end):
                writer.add_page(reader.pages[page_num])
            
            # Save the split PDF part with a filename indicating the page range
            filename = Path(pdf_path).stem
            output_path = os.path.join(output_folder, f"{filename}_part_{i + 1}_pages_{start}-{end}.pdf")
            with open(output_path, "wb") as output_pdf:
                writer.write(output_pdf)
            
            # Check if the file was saved correctly
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                if verbose:
                    print(f"Failed to save the file: {output_path}")
                return False
        
        if verbose:
            print("All PDF parts saved successfully.")
        return True
    
    except (FileNotFoundError, ValueError, IOError) as e:
        if verbose:
            print(f"An error occurred: {e}")
        return False

def merge_pdfs(pdf_list: List[str], output_path: str, verbose: bool = True) -> bool:
    """
    Merges a list of PDF files into a single PDF file in the specified order.

    Args:
        pdf_list (List[str]): A list of file paths to the PDF files to be merged.
        output_path (str): The file path where the merged PDF will be saved.
        verbose (bool): If True, prints a success or failure message. Defaults to True.

    Returns:
        bool: True if the PDF was successfully merged and saved, False otherwise.
    """
    
    try:
        merger = PdfMerger()
        
        for pdf in pdf_list:
            merger.append(pdf)
        
        # Write merged PDF to the output path
        merger.write(output_path)
        merger.close()

        if verbose:
            print(f"PDFs merged successfully into '{output_path}'.")
        return True

    except Exception as e:
        if verbose:
            print(f"An error occurred while merging the PDFs: {e}")
        return False

def delete_pdf_pages(input_pdf: str, output_pdf: str, page_numbers: List[int], verbose: bool = True) -> bool:
    """
    Deletes specified pages from a PDF file.

    Args:
        input_pdf: Path to the input PDF file.
        output_pdf: Path to the output PDF file.
        page_numbers: A list of page numbers to delete (starting from 1).
        verbose: If True, prints a success message if the operation is successful.

    Returns:
        True if the output PDF was successfully written, False otherwise.
    """

    try:
        with open(input_pdf, 'rb') as in_file:
            reader = PdfReader(in_file)
            writer = PdfWriter()

            # Convert page numbers to 0-based indices
            page_numbers = [num - 1 for num in page_numbers]
            page_numbers.sort(reverse=True)

            for page_num, page in enumerate(reader.pages):
                if page_num not in page_numbers:
                    writer.add_page(page)

            with open(output_pdf, 'wb') as out_file:
                writer.write(out_file)
                if verbose:
                    print("PDF pages deleted successfully.")
            return True
    except PdfReadError as e:
        if verbose:
            print(f"Error processing PDF: {e}")
        return False
    
    except FileNotFoundError:
        if verbose:
            print(f"Input file not found: {input_pdf}")
        return False
    
    except Exception as e:
        if verbose:
            print(f"Unexpected error occurred: {e}")
        return False

def rotate_pages(input_pdf_path: str,
                 output_pdf_path: str,
                 global_rotation: Optional[int] = None,
                 page_rotation_dict: Optional[dict[int, int]] = None,
                 verbose: bool = True) -> bool:
    """
    Rotates pages in a PDF file based on global or page-wise rotation setting(s).

    This function reads a PDF file, rotates all pages according to a global rotation angle or rotates specific pages
    according to individual rotation angles, and saves the modified PDF to a new file.

    Args:
        input_pdf_path (str): The path to the input PDF file that will have its pages rotated.
        output_pdf_path (str): The path where the rotated PDF file will be saved.
        global_rotation (Optional[int]): A global rotation angle to apply to all pages (in degrees). Valid angles are
                                         90, 180, 270, -90, -180, and -270 degrees. If None, no global rotation is applied.
        page_rotation_dict (Optional[Dict[int, int]]): A dictionary mapping page numbers (1-based index) to rotation angles.
                                                       Individual page rotations override the global rotation. Valid angles
                                                       are 90, 180, 270, -90, -180, and -270 degrees.
        verbose (bool): If True, prints the success or failure of the operation. Defaults to True.

    Returns:
        bool: True if the PDF was saved successfully with the rotated pages, False otherwise.

    Raises:
        ValueError: If an invalid rotation angle or a zero-based page index is provided.

    Example:
        success = rotate_pages(
            'input.pdf',
            'output.pdf',
            global_rotation=90,
            page_rotation_dict={1: 180, 3: -90},
            verbose=True
        )
        # Rotates all pages by 90 degrees clockwise unless overridden, where page 1 is rotated by 180 degrees
        # and page 3 is rotated by 90 degrees counterclockwise, and saves the output to 'output.pdf'.
    """

    try:
        # Validate rotation angles
        valid_rotations = {90, 180, 270, -90, -180, -270}
        if global_rotation and global_rotation not in valid_rotations:
            allowed_values = ", ".join([str(x) for x in valid_rotations])
            raise ValueError(f"Invalid global rotation angle: {global_rotation}. Allowed values are: {allowed_values}.")

        if page_rotation_dict:
            for page_num, rotation in page_rotation_dict.items():
                if page_num <= 0:
                    raise ValueError("Page numbers should be natural numbers (starting from 1). A zero index was provided.")
                if rotation not in valid_rotations:
                    allowed_values = ", ".join([str(x) for x in valid_rotations])
                    raise ValueError(f"Invalid rotation angle for page {page_num}: {rotation}. Allowed values are: {allowed_values}.")

        # Read the input PDF
        pdf_reader = PdfReader(input_pdf_path)
        pdf_writer = PdfWriter()

        # Iterate through each page and apply the appropriate rotation
        for i, page in enumerate(pdf_reader.pages, start=1):
            rotation = page_rotation_dict.get(i, global_rotation)
            if rotation is not None:
                page.rotate(rotation)
            pdf_writer.add_page(page)

        # Write the rotated PDF to the output file
        with open(output_pdf_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)

        if verbose:
            print(f"Rotated PDF saved successfully to '{output_pdf_path}'.")
        return True

    except Exception as e:
        if verbose:
            print(f"Failed to save the rotated PDF: {e}")
        return False

def rearrange_pdf(input_pdf_path: str, output_pdf_path: str, page_order: List[int], verbose: bool = True) -> bool:
    """
    Rearranges pages in a PDF file according to a specified order.

    Args:
        input_pdf_path: Path to the input PDF file.
        output_pdf_path: Path to save the output PDF file with rearranged pages.
        page_order: A list of integers representing the new order of pages (1-indexed).
        verbose (bool): If True, prints a success message if the operation is successful.

    Returns:
        True if the PDF was rearranged and saved successfully, False otherwise.
    """

    try:
        with open(input_pdf_path, 'rb') as input_file:
            reader = PdfReader(input_file)
            writer = PdfWriter()

            # Convert page order to 0-based indices
            page_order = [index - 1 for index in page_order]

            # Ensure page order covers all pages
            if len(page_order) != len(reader.pages):
                raise ValueError("Page order list must have the same length as the number of pages in the PDF.")

            # Rearrange pages according to the provided order
            for i in page_order:
                if 0 <= i < len(reader.pages):
                    writer.add_page(reader.pages[i])
                else:
                    raise ValueError(f"Invalid page index: {i + 1}")

            with open(output_pdf_path, 'wb') as output_file:                
                writer.write(output_file)
                if verbose:
                    print(f"Rearranged PDF saved to '{output_pdf_path}'.")
                return True

    except PdfReadError as e:
        if verbose:
            print(f"Error processing PDF: {e}")
        return False
    
    except FileNotFoundError:
        if verbose:
            print(f"Input file not found: {input_pdf_path}")
        return False
    
    except ValueError as e:
        if verbose:
            print(f"Error: {e}")
        return False
    
    except Exception as e:
        if verbose:
            print(f"Unexpected error occurred: {e}")
        return False

def remove_pdf_metadata(input_pdf_path: str, output_pdf_path: str, verbose: bool = True) -> bool:
    """
    Remove all metadata from a PDF file and save the modified content to a new PDF.

    This function reads the content of an existing PDF file, removes any metadata
    associated with it, and writes the content to a new PDF file. Metadata includes
    information like the author, title, subject, and other document properties.

    Args:
        input_pdf_path (str): The path to the input PDF file from which metadata should be removed.
        output_pdf_path (str): The path where the new PDF file without metadata will be saved.
        verbose (bool): If True, print the success or failure of the operation. Defaults to True.

    Returns:
        bool: True if the PDF was saved successfully without metadata, False otherwise.

    Example:
        success = remove_pdf_metadata('input.pdf', 'output.pdf', verbose=True)
        if success:
            print("Metadata removed successfully.")
        else:
            print("Failed to remove metadata.")
    """
    
    try:
        with open(input_pdf_path, 'rb') as input_pdf_file:
            pdf_reader = PdfReader(input_pdf_file)
            pdf_writer = PdfWriter()

            # Copy all pages to the writer object
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

            # Remove metadata
            pdf_writer.add_metadata({})

            # Write the modified content to a new PDF
            with open(output_pdf_path, 'wb') as output_pdf_file:
                pdf_writer.write(output_pdf_file)

        if verbose:
            print(f"Metadata removed and saved to '{output_pdf_path}'.")
        return True

    except Exception as e:
        if verbose:
            print(f"Failed to remove metadata: {e}")
        return False

def crop_pdf(input_pdf: str,
             output_pdf: str,
             global_margins: Optional[dict[str, float]] = None,
             page_margins: Optional[dict[int, Dict[str, float]]] = None,
             verbose: bool = True) -> bool:
    """
    Crops the pages of a PDF based on the given (individual/global) margins and saves the result to a new PDF file.

    Args:
        input_pdf (str): The file path of the PDF to be cropped.
        output_pdf (str): The file path where the cropped PDF should be saved.
        global_margins (Optional[Dict[str, float]]): A dictionary containing 'left', 'right', 'top', and 'bottom' margins in points
                                                     to be applied globally to all pages if no individual margins are specified.
        page_margins (Optional[Dict[int, Dict[str, float]]]): A dictionary where keys are page indices (starting from 1) and values are
                                                             dictionaries specifying 'left', 'right', 'top', and 'bottom' margins in points
                                                             for individual pages. These margins will override global margins for specified pages.
        verbose (bool): If True, prints success or failure messages. Defaults to True.

    Returns:
        bool: True if the PDF is successfully saved, False otherwise.
    """
    
    try:
        pdf_reader = PdfReader(input_pdf)
        pdf_writer = PdfWriter()

        # Initialize global and page margins as empty dictionaries if not provided
        global_margins = global_margins or {}
        page_margins = page_margins or {}

        num_pages = len(pdf_reader.pages)

        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]

            # Default crop box is the media box
            crop_box = page.mediabox

            # Determine margins to apply
            # Start with global margins and override with page-specific margins if provided
            margins = page_margins.get(page_num + 1, global_margins)

            if margins:
                left = margins.get('left', 0)
                right = margins.get('right', 0)
                top = margins.get('top', 0)
                bottom = margins.get('bottom', 0)

                # Adjust the crop box based on the margins
                new_lower_left = (crop_box.lower_left[0] + left, crop_box.lower_left[1] + bottom)
                new_upper_right = (crop_box.upper_right[0] - right, crop_box.upper_right[1] - top)

                # Ensure the new coordinates are valid
                if new_upper_right[0] > new_lower_left[0] and new_upper_right[1] > new_lower_left[1]:
                    page.cropbox.lower_left = new_lower_left
                    page.cropbox.upper_right = new_upper_right
                else:
                    raise ValueError(f"Invalid crop box dimensions on page {page_num + 1}. Please check the margins.")

            # Add the modified page to the writer
            pdf_writer.add_page(page)

        # Write the cropped PDF to the output file
        with open(output_pdf, 'wb') as out_file:
            pdf_writer.write(out_file)

        if verbose:
            print(f"PDF cropped and saved successfully to '{output_pdf}'.")
        return True

    except Exception as e:
        if verbose:
            print(f"An error occurred while cropping the PDF: {e}")
        return False

def redact_strings(input_pdf_path: str,
                   output_pdf_path: str,
                   strings_to_anonymize: List[str],
                   overlay_color: Union[str, Tuple[int, int, int]] = (0, 0, 0),
                   match_whole_word: bool = True,
                   verbose: bool = True) -> bool:
    """
    Anonymize and rasterize specified strings (words/substrings) in a PDF by redacting them with a specified overlay color.

    Args:
        input_pdf_path (str): The path to the input PDF file where words will be anonymized.
        output_pdf_path (str): The path where the output PDF file with redactions will be saved.
        strings_to_anonymize (List[str]): A list of words or phrases to be anonymized in the PDF.
        overlay_color (Union[str, Tuple[int, int, int]]): The color to use for redaction, in RGB, hex, or human-readable color name format.
        match_whole_word (bool): If True, only exact word matches will be anonymized. Defaults to True.
        verbose (bool): If True, prints a success message if the operation is successful.

    Returns:
        bool: True if the PDF was saved successfully with the redactions, False otherwise.
    """

    try:
        # Convert overlay color to normalized RGB tuple (0 to 1 range)
        rgb_color = convert_to_rgb(overlay_color)

        # Open the PDF document
        pdf_document = fitz.open(input_pdf_path)

        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)

            for word in strings_to_anonymize:
                # Search for the string (word/substring)
                text_instances = page.search_for(word)
                final_instances = []

                if match_whole_word:
                    for inst in text_instances:
                        # Extract text around the instance to check for whole word match
                        rect = fitz.Rect(inst)
                        extracted_text = page.get_text("text", clip=rect)

                        # Check if the found text is exactly the word
                        if extracted_text.strip() == word:
                            final_instances.append(inst)
                else:
                    final_instances = text_instances

                # Redact the text instances
                for inst in final_instances:
                    rect = fitz.Rect(inst)
                    # Add the redaction annotation with the RGB color (normalized float tuple)
                    page.add_redact_annot(rect, fill=rgb_color)

            # Apply all redactions
            page.apply_redactions()

        # Save the modified PDF
        pdf_document.save(output_pdf_path)
        pdf_document.close()

        if verbose:
            print(f"Redacted PDF saved to '{output_pdf_path}'.")
        return True

    except Exception as e:
        if verbose:
            print(f"An error occurred: {e}")
        return False

def enable_text_copy(input_pdf_path: str, output_pdf_path: str, verbose: bool = True) -> bool:
    """
    Removes restrictions on a PDF that prevent text from being copied.

    This function uses the pikepdf library to open a PDF file, remove any restrictions 
    that prevent text from being copied, and then save the unrestricted PDF to a new file.

    Args:
        input_pdf_path (str): The file path to the input PDF.
        output_pdf_path (str): The file path where the unrestricted PDF should be saved.
        verbose (bool): If True, prints a success message if the operation is successful.

    Returns:
        bool: True if the PDF was saved successfully with text copying enabled, False otherwise.
    """
    try:
        # Open the PDF with pikepdf, automatically removing restrictions
        with pikepdf.open(input_pdf_path) as pdf:
            # Save the unrestricted PDF to the specified output path
            pdf.save(output_pdf_path)

        if verbose:
            print(f"Text copy enabled PDF saved to '{output_pdf_path}'.")
        return True

    except pikepdf._qpdf.PasswordError:
        if verbose:
            print("Failed to open PDF: Incorrect password.")
        return False

    except pikepdf._qpdf.PdfError as e:
        if verbose:
            print(f"Failed to process PDF: {e}")
        return False

    except Exception as e:
        if verbose:
            print(f"An unexpected error occurred: {e}")
        return False

def make_pdf_read_only(input_pdf_path: str, output_pdf_path: str, verbose: bool = True) -> bool:
    """
    Takes a PDF with filled form fields and makes it read-only by fully flattening the form fields.
    The output PDF will be saved to the specified path without setting a password. 
    Note, this approach doesn't work on all tested pdfs.

    Args:
        input_pdf_path (str): The file path to the input PDF with form fields.
        output_pdf_path (str): The file path where the read-only PDF should be saved.
        verbose (bool): If True, prints a success message if the operation is successful.

    Returns:
        bool: True if the PDF was saved successfully, False otherwise.
    """
    
    try:
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()
        
        # Flatten form fields by copying each page to the writer
        for page in reader.pages:
            
            # If page contains form fields, merge them with the content
            if '/Annots' in page:
                page_annotations = page['/Annots']
                for annotation in page_annotations:
                    annotation_obj = annotation.get_object()
                    if annotation_obj.get('/FT'):  # Field Type
                        # Update annotation with PdfObject instances
                        annotation_obj.update({
                            NameObject('/Ff'): NumberObject(annotation_obj.get('/Ff', 0) | 1),  # Set Read-Only flag
                            NameObject('/F'): NumberObject(annotation_obj.get('/F', 0) | 4),    # Flatten the field (remove appearance)
                            })            
            writer.add_page(page)
        
        # Write the output PDF to the specified path
        with open(output_pdf_path, "wb") as output_pdf:
            writer.write(output_pdf)
        
        if verbose:
            print(f"Read-only PDF saved to '{output_pdf_path}'.")
        return True

    except Exception as e:
        if verbose:
            print(f"An error occurred: {e}")
        return False

def remove_images_and_add_placeholder(input_pdf: str,
                                      output_pdf: str,
                                      pages_with_images: Optional[List[int]] = None,
                                      placeholder: str = "Image removed",
                                      verbose: bool = True) -> bool:
    """
    Removes images from a PDF and replaces them with a given placeholder. Saves the result to a new PDF.

    Args:
        input_pdf (str): The path to the input PDF file.
        output_pdf (str): The path to the output PDF file.
        pages_with_images (List[int], optional): A list of page indices (1-based) where images should be removed.
                                                 If not provided, images will be removed from all pages.
        placeholder (str): The placeholder that should be inserted where the respective image has been deleted.                               
        verbose (bool): If True, prints success/failure messages. Defaults to True.

    Returns:
        bool: True if the PDF was successfully written, False otherwise.
    """
    
    try:
        # Open the input PDF
        pdf_document = fitz.open(input_pdf)

        # Determine pages to process
        if pages_with_images is None:
            pages_to_process = range(len(pdf_document))  # All pages
        else:
            pages_to_process = [page - 1 for page in pages_with_images]  # Convert to 0-based index

        # Process each specified page
        for page_num in pages_to_process:
            page = pdf_document.load_page(page_num)
            image_list = page.get_images(full=True)

            # Remove each image and replace it with a placeholder
            for image in image_list:
                xref = image[0]  # Image reference number
                rect = page.get_image_rects(xref)[0]  # Get image position and size

                # Remove the image from the document
                pdf_document._deleteObject(xref)

                # Draw a placeholder (a rectangle and some text)
                page.draw_rect(rect, color=(1, 0, 0), width=2)  # Red rectangle placeholder
                page.insert_text((rect.x0, rect.y1), placeholder, fontsize=20, color=(1, 0, 0))

            if verbose:
                if image_list:
                    print(f"Images removed from page {page_num + 1}.")
                else:
                    print(f"No images found on page {page_num + 1}.")

        # Save the modified PDF to the output file
        pdf_document.save(output_pdf)

        # Close the document
        pdf_document.close()

        if verbose:
            print(f"Images successfully removed and placeholders added. Saved to '{output_pdf}'.")

        return True

    except Exception as e:
        if verbose:
            print(f"Failed to remove images from '{input_pdf}': {e}")
        return False

def check_pdfa_compliance(input_pdf: str) -> bool:
    """
    Check if a PDF is PDF/A compliant by inspecting its XMP metadata and PDF structure.

    Args:
        input_pdf (str): Path to the input PDF file.

    Returns:
        bool: True if the PDF is PDF/A compliant, False otherwise.
    """
    
    try:
        with pikepdf.open(input_pdf) as pdf:
            # Check document's XMP metadata for PDF/A compliance
            try:
                xmp_metadata = pdf.open_metadata()
                if xmp_metadata is not None:
                    pdfa_part = xmp_metadata.get("pdfaid:part", None)
                    pdfa_conformance = xmp_metadata.get("pdfaid:conformance", None)
                    
                    # If both keys are present, the PDF is likely PDF/A compliant
                    if pdfa_part and pdfa_conformance:
                        return True
            except KeyError:
                # If there's an issue reading XMP metadata, continue with other checks
                pass

            # PDF/A typically embeds an OutputIntent entry in the document's structure
            # We check for /OutputIntent dictionaries, which are required in PDF/A files
            if "/OutputIntent" in pdf.root:
                output_intent = pdf.root["/OutputIntent"]
                if isinstance(output_intent, pikepdf.Dictionary):
                    return True
                elif isinstance(output_intent, pikepdf.Array):
                    if any("/GTS_PDFA1" in intent.get("/S", "") for intent in output_intent):
                        return True

        return False  # Return False if none of the checks confirm PDF/A compliance

    except Exception as e:
        print(f"An error occurred while checking PDF/A compliance: {e}")
        return False
    
def convert_to_pdfa(input_pdf: str, output_pdf: str, verbose: bool = True) -> bool:
    """
    Converts a PDF to a PDF/A compliant format using Ghostscript.

    Args:
        input_pdf (str): Path to the input PDF file.
        output_pdf (str): Path to the output PDF/A file.
        verbose (bool): If True, prints success or failure messages. Defaults to True.

    Returns:
        bool: True if the PDF is successfully processed, False otherwise.
    """
    
    import ghostscript
    
    try:
        # Ghostscript command to convert PDF to PDF/A
        args = [
            "gs",  # Ghostscript command
            "-dPDFA",  # Enable PDF/A mode
            "-dBATCH",  # Exit after processing
            "-dNOPAUSE",  # Do not prompt and pause after each page
            "-dUseCIEColor",  # Ensure color accuracy
            "-sDEVICE=pdfwrite",  # Set the output device
            f"-sOutputFile={output_pdf}",  # Output PDF/A file path
            "-dPDFACompatibilityPolicy=1",  # Ensure strict PDF/A compliance
            input_pdf  # Input PDF file path
        ]

        # Run Ghostscript with the specified arguments
        ghostscript.Ghostscript(*args)

        if verbose:
            print(f"PDF successfully converted to PDF/A and saved to '{output_pdf}'.")

        return True

    except Exception as e:
        if verbose:
            print(f"An error occurred while converting to PDF/A: {e}")
        return False
