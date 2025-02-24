import os

import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject


class PDFCropper:
    def __init__(self, input_pdf_path, output_folder_path):
        """
        Initialize the PDFCropper with the input PDF path, output folder, and set up the PDF reader.

        Args:
            input_pdf_path (str): Path to the input PDF file.
            output_folder_path (str): Path to the folder where cropped PDFs will be saved.
        """
        self.input_pdf_path = input_pdf_path
        self.output_folder_path = output_folder_path
        self.reader = PdfReader(input_pdf_path)
        self.total_pages = len(self.reader.pages)

    def _ensure_output_folder_exists(self):
        """Ensure the output folder exists, creating it if necessary."""
        if not os.path.exists(self.output_folder_path):
            os.makedirs(self.output_folder_path)
            print(f"[INFO] Output folder '{self.output_folder_path}' created.")
        else:
            print(f"[INFO] Output folder '{self.output_folder_path}' already exists.")

    def _clear_output_folder(self):
        """Delete all files in the output folder to avoid conflicts."""
        print("[INFO] Clearing old files in the output folder...")
        for file_name in os.listdir(self.output_folder_path):
            file_path = os.path.join(self.output_folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"[INFO] Deleted old file: {file_name}")

    def _is_valid_label(self, output_file_path, bbox):
        """
        Check if the area defined by 'bbox' (bounding box) contains any of the expected texts:
        ["NF:", "NFe:"], in a case-insensitive manner.

        Args:
            output_file_path (str): Path to the PDF file.
            bbox (tuple or list): A tuple (or list) in the format (x0, y0, x1, y1) defining the region of interest.
            The coordinates follow the PDF coordinate system (origin at the lower-left corner).

        Returns:
            bool: True if at least one of the expected texts is found in the area, False otherwise.
        """
        complete_text = ""
        
        # Open the cropped PDF using pdfplumber
        with pdfplumber.open(output_file_path) as pdf:
            for page in pdf.pages:
                # Limit extraction to the area defined by bbox
                cropped_area = page.within_bbox(bbox)
                text = cropped_area.extract_text()
                if text:
                    complete_text += text
        
        # Define the expected texts
        expected_texts = ["NF:", "NFe:", "JADLEVE"]
        print(f"[INFO] Checking if the area contains any of the expected texts: {expected_texts}")
        
        # Convert to lowercase for case-insensitive comparison
        complete_text_lower = complete_text.lower()
        
        # Check if any of the expected texts are present in the extracted area
        is_valid = any(expected.lower() in complete_text_lower for expected in expected_texts)
        return is_valid

    def _crop_and_save_page(self, page_index, output_file_path, crop_box_coordinates):
        """
        Crop a single page and save it as a new PDF.

        Args:
            page_index (int): Index of the page to crop.
            output_file_path (str): Path to save the cropped PDF.
            crop_box_coordinates (list): Coordinates for the crop box [x0, y0, x1, y1].
        """
        print(f"[INFO] Cropping page {page_index + 1} (index {page_index})...")
        writer = PdfWriter()
        page = self.reader.pages[page_index]
        crop_box = RectangleObject(crop_box_coordinates)
        page.cropbox = crop_box
        writer.add_page(page)

        with open(output_file_path, "wb") as output_file:
            writer.write(output_file)
        writer.close()

        # Validate if the cropped PDF contains the expected label only within the defined area
        if not self._is_valid_label(output_file_path, crop_box_coordinates):
            os.remove(output_file_path)
            print(f"[INFO] Invalid label in cropped PDF. File deleted: {output_file_path}")
        else:
            print(f"[INFO] Cropped PDF successfully saved as '{output_file_path}'.")

    def crop_labels(self):
        """
        Crop labels from all pages of the input PDF using the defined crop box templates.
        For each page, the width and height are logged. Only pages with dimensions
        width == 841.8898 and height == 595.2756 are processed.
        """
        print(f"[INFO] Starting cropping process for PDF: '{self.input_pdf_path}'")
        print(f"[INFO] Total pages in the input PDF: {self.total_pages}")

        self._ensure_output_folder_exists()
        self._clear_output_folder()

        label_width = 265  # Width of each label
        crop_box_templates = [
            [27, 143, 290, 570],  # First label
            [27 + label_width, 143, 290 + label_width, 570],  # Second label
            [27 + (label_width * 2), 143, 290 + (label_width * 2), 570],  # Third label
        ]

        label_counter = 1
        # Iterate through all pages
        for page_index in range(0, self.total_pages):
            # Get the page and log its width and height
            page = self.reader.pages[page_index]
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            print(f"[INFO] Page {page_index + 1}: Width = {width}, Height = {height}")
            
            # Process only pages with the specified dimensions
            if width == 841.8898 and height == 595.2756:
                for crop_box_coordinates in crop_box_templates:
                    output_file_path = os.path.join(self.output_folder_path, f"label_{label_counter}.pdf")
                    self._crop_and_save_page(page_index, output_file_path, crop_box_coordinates)
                    label_counter += 1

        print("[INFO] Cropping process completed successfully.")