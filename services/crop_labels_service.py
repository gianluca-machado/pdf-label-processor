from pypdf import PdfWriter, PdfReader
from pypdf.generic import RectangleObject
import os

class PDFCropper:
    def __init__(self, input_pdf_path, output_folder_path):
        """
        Initialize the PDFCropper with input PDF, output folder, and crop box coordinates.

        Args:
            input_pdf_path (str): Path to the input PDF file.
            output_folder_path (str): Path to the folder where cropped PDFs will be saved.
        """
        self.input_pdf_path = input_pdf_path
        self.output_folder_path = output_folder_path
        self.reader = PdfReader(input_pdf_path)
        self.total_pages = len(self.reader.pages)

    def _ensure_output_folder_exists(self):
        """Ensure the output folder exists, and create it if it doesn't."""
        if not os.path.exists(self.output_folder_path):
            os.makedirs(self.output_folder_path)
            print(f"[INFO] Output folder '{self.output_folder_path}' created.")
        else:
            print(f"[INFO] Output folder '{self.output_folder_path}' already exists.")

    def _clear_output_folder(self):
        """Delete all files in the output folder to avoid conflicts with old files."""
        print("[INFO] Clearing old files in the output folder...")
        for file_name in os.listdir(self.output_folder_path):
            file_path = os.path.join(self.output_folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"[INFO] Deleted old file: {file_name}")

    def _crop_and_save_page(self, page_index, output_file_path, crop_box_coordinates):
        """
        Crop a single page and save it as a new PDF.

        Args:
            page_index (int): Index of the page to crop.
            output_file_path (str): Path to save the cropped PDF.
            crop_box_coordinates (list): Coordinates for the crop box [x1, y1, x2, y2].
        """
        print(f"[INFO] Cropping page {page_index + 1} (index {page_index})...")
        writer = PdfWriter()
        page = self.reader.pages[page_index]
        crop_box = RectangleObject(crop_box_coordinates)
        page.cropbox = crop_box
        writer.add_page(page)

        with open(output_file_path, "wb") as output_file:
            writer.write(output_file)

        print(f"[INFO] Cropped PDF saved as '{output_file_path}'.")

    def crop_labels(self):
        """
        Crop all even-numbered pages (0, 2, 4, ...) and save them as individual PDFs.
        Each page is divided into three labels with predefined crop box coordinates.
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
        for page_index in range(0, self.total_pages, 2):  # Process only even-numbered pages
            for crop_box_coordinates in crop_box_templates:
                output_file_path = os.path.join(self.output_folder_path, f"label_{label_counter}.pdf")
                self._crop_and_save_page(page_index, output_file_path, crop_box_coordinates)
                label_counter += 1

        print("[INFO] Cropping process completed successfully.")