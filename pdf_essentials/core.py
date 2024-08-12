import io
import re
from enum import Enum, auto
from typing import Union, Tuple

import pikepdf
import fitz
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, NumberObject
from PyPDF2.errors import PdfReadError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import utils


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

def rotate_pages(input_pdf_path: str,
                 output_pdf_path: str,
                 rotation_dict: dict[int, int],
                 verbose: bool = True) -> bool:
    """
    Rotates specific pages in a PDF file based on a dictionary of page numbers and rotation angles.

    This function reads a PDF file, rotates specific pages according to the given rotation angles,
    and saves the modified PDF to a new file. The dictionary `rotation_dict` should map page numbers 
    (starting from 1) to rotation angles (in degrees). Valid rotation angles are 90, 180, 270, -90, 
    -180, and -270 degrees.

    Args:
        input_pdf_path (str): The path to the input PDF file that will have its pages rotated.
        output_pdf_path (str): The path where the rotated PDF file will be saved.
        rotation_dict (dict[int, int]): A dictionary mapping page numbers (1-based index) to rotation angles.
        verbose (bool): If True, print the success or failure of the operation. Defaults to True.

    Returns:
        bool: True if the PDF was saved successfully with the rotated pages, False otherwise.

    Raises:
        ValueError: If an invalid rotation angle or a zero-based page index is provided in `rotation_dict`.

    Example:
        success = rotate_pages('input.pdf', 'output.pdf', {1: 90, 3: -90}, verbose=True)
        # Rotates the first page by 90 degrees clockwise and the third page by 90 degrees counterclockwise,
        # and saves the output to 'output.pdf'.
    """

    try:
        # Validate rotation angles
        valid_rotations = {90, 180, 270, -90, -180, -270}
        for page_num, rotation in rotation_dict.items():
            if page_num <= 0:
                raise ValueError("Page numbers should be natural numbers (starting from 1). A zero index was provided.")

            if rotation not in valid_rotations:
                allowed_values = ", ".join([str(x) for x in valid_rotations])
                raise ValueError(f"Invalid rotation angle: {rotation}. Allowed values are: {allowed_values}.")

        # Read the input PDF
        pdf_reader = PdfReader(input_pdf_path)
        pdf_writer = PdfWriter()

        # Iterate through each page and rotate if necessary
        for i, page in enumerate(pdf_reader.pages, start=1):
            if i in rotation_dict:
                page.rotate(rotation_dict[i])
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

def anonymize_and_rasterize_strings(
    input_pdf_path: str,
    output_pdf_path: str,
    strings_to_anonymize: list[str],
    overlay_color: Union[str, Tuple[int, int, int]] = (0, 0, 0),
    match_whole_word: bool = True,
    verbose: bool = True) -> bool:
    """
    Anonymize and rasterize specified strings (words/substrings) in a PDF by redacting them with a specified overlay color.

    This function searches for specific words or phrases in a PDF file and redacts (obscures)
    them with a solid color overlay. The overlay color can be specified in various formats,
    and the function supports exact word matching.

    Args:
        input_pdf_path (str): The path to the input PDF file where words will be anonymized.
        output_pdf_path (str): The path where the output PDF file with redactions will be saved.
        strings_to_anonymize (list[str]): A list of words or phrases to be anonymized in the PDF.
        overlay_color (Union[str, Tuple[int, int, int]]): The color to use for redaction, in RGB, hex, CMYK, HSL, or human-readable color name format.
        match_whole_word (bool): If True, only exact word matches will be anonymized. Defaults to True.
        verbose (bool): If True, prints a success message if the operation is successful.

    Returns:
        bool: True if the PDF was saved successfully with the redactions, False otherwise.

    Example:
        success = anonymize_and_rasterize_strings(
            'input.pdf', 'output.pdf', ['confidential', 'secret'], overlay_color='red'
        )
        if success:
            print("PDF redacted and saved successfully.")
        else:
            print("Failed to save the redacted PDF.")
    """
    try:
        # Convert overlay color to RGB list
        rgb_color = utils.convert_to_rgb(overlay_color)

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
                    # Pass RGB color as a list to avoid immutability issues
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

def delete_pdf_pages(input_pdf: str,
                     output_pdf: str,
                     page_numbers: list[int],
                     verbose: bool = True) -> bool:
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

def extract_pdf_pages(input_pdf: str,
                      output_pdf_path: str,
                      page_indices: list[int],
                      verbose:bool = True) -> bool:
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

def rearrange_pdf(input_pdf_path: str,
                  output_pdf_path: str,
                  page_order: list[int],
                  verbose: bool = True) -> bool:
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
