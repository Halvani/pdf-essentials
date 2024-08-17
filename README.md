<div align="center">
  <p>
    <a href="#"><img src="https://github.com/Halvani/pdf-essentials/blob/main/images/redaction.jpg" alt="PDF-Essentials logo"/></a>
  </p>
</div>

# PDF-Essentials
An easy-to-use Python library for annotating, manipulating and processing PDF files.


## Description
PDF-Essentials was born out of the idea to bundle both common and advanced PDF manipulation and processing functions into a single library. It builds on [pikepdf](https://github.com/pikepdf/pikepdf), [fitz](https://github.com/pymupdf/PyMuPDF), [PyPDF2/pypdf](https://github.com/py-pdf/pypdf) and [reportlab](https://pypi.org/project/reportlab/) and allows you to perform a variety of PDF editing tasks, including redacting, annotating, extracting, cropping, deleting, splitting and others, without having to deal with the details required when using low-level PDF libraries.


## Installation
The easiest way to install PDF-Essentials is to use pip, where you can choose between PyPI and this repository: 

- ```pip install pdf-essentials```
- ```pip install git+https://github.com/Halvani/pdf-essentials.git```

The latter will pull and install the latest commit from this repository as well as the required Python dependencies. Note that the repo is updated regulary, while PyPi-packages are less frequently released (primarily after mayor bugfixing, refactoring, etc.).


## Features
PDF-Essentials offers both standard and advanced functions for processing PDF files. The following functions are currently covered:

- **Numbering**: Insert page numbers at three possible positions at the bottom: left, center or right

- **Extraction**: Extract specified pages from a PDF and save the result to a new PDF file

- **Range splitting**: Split a PDF file into several parts using a list of page ranges and save the parts in the specified output folder

- **Merging**: merge a list of PDF files into a single PDF file in the specified order

- **Deletion**: delete specified pages from a PDF file

- **Rotation**: rotate pages in a PDF file based on global or page-wise rotation setting(s)

- **Reordering**: arrange the pages in a PDF file in a specific order

- **Metadata removal**: strip all metadata from a PDF file and save the modified content in a new PDF file

- **Cropping**: crop pages of a PDF based on the given (individual/global) margins and saves the result to a new PDF file

- **Redaction**: anonymize and rasterize words/substrings in a PDF file by redacting them with an overlay color ([RGB](https://en.wikipedia.org/wiki/RGB_color_model), [HTML color codes](https://htmlcolorcodes.com/), [Web colors](https://en.wikipedia.org/wiki/Web_colors))

- **Copy enabling**: remove restrictions in a PDF file that prevent text from being copied

- **Form field protection**: take a PDF with filled form fields and make it read-only

- **PDF/A Conversion/Validation**: convert PDF to PDF/A format (requires [ghostscript](https://ghostscript.com/releases/gsdnld.html)) or validate if a given PDF complies with PDF/A

- **Highlighting**: highlights occurrences of substrings, whole words or regex patterns in a PDF file and adds comments to the highlighted text along with a background color


## Limitations / Design Considerations:
PDF-Essentials comes with several limitations:

- *Form field protection* does not currently work for all tested PDFs and is still being investigated. Therefore, you do not need to open an issue in this regard.

- Currently, all input/output operations are based on the file system. In the future, it is planned to integrate an additional in-memory mechanism so that the functions can operate directly on byte streams, which in turn will enable reasonable pipelining. However, this mechanism is a little tricky and requires a well thought-out design, which again demands time. So please be patient 🙏


## Disclaimer
Although this project has been carried out with great care, no liability is accepted for the completeness and accuracy of all the underlying data. The use of PDF-Essentials for integration into production systems is at your own risk!

Furthermore, please note that this project is still in its initial phase. The code structure may therefore change over time.


## License
The PDF-Essentials package is released under the Apache-2.0 license. See <a href="https://github.com/Halvani/pdf-essentials/blob/main/LICENSE">LICENSE</a> for further details.


## Last Remarks
As is usual with open source projects, we developers do not earn any money with what we do, but are primarily interested in giving something back to the community with fun, passion and joy. Nevertheless, we would be very happy if you rewarded all the time that has gone into the project with just a small star 🤗