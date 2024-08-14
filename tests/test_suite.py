import os
import sys
import inspect
import unittest
import pytest

# Import the module from the parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import pdf_essentials

class TestCore(unittest.TestCase):

    def test_delete_pdf_pages(self):
        input_pdf = r"tests/doc_with_4_pages.pdf"
        output_pdf = r"tests/test_deletion_now_only_page_2_page_4_doc_with_4_pages.pdf"
        page_numbers = [1, 3]
        success = pdf_essentials.delete_pdf_pages(input_pdf, output_pdf, page_numbers)
        assert success

    def test_extract_pdf_pages(self):
        input_pdf = r"tests/doc_with_4_pages.pdf"
        output_pdf = r"tests/test_extraction_now_only_page_1_and_page_2.pdf"
        page_indices = [1, 2]
        success = pdf_essentials.extract_pdf_pages(input_pdf, output_pdf, page_indices)
        assert success

    def test_redaction(self):
        input_pdf = r"tests/doc_about_python.pdf"
        output_pdf = r"tests/test_redaction_doc_about_python.pdf"
        strings_to_anonymize = ["Python", "programming", "release"]
        overlay_color = (0, 0, 0)
        success = pdf_essentials.redact_strings(input_pdf, output_pdf, strings_to_anonymize, overlay_color, match_whole_word=False)
        text = pdf_essentials.get_text(output_pdf)
        assert (success and "Python" not in text and "programming" not in text and "release" not in text)

