from pypdf import PdfWriter, PdfReader, PageObject, Transformation
from pypdf.generic import RectangleObject

def crop_pdf(input_pdf, output_pdf, crop_box_coordinates):
    # Create a PdfReader object to read the input PDF
    reader = PdfReader(input_pdf)

    # Create a PdfWriter object to write the cropped PDF
    writer = PdfWriter()

    # Get the first page
    first_page = reader.pages[0]

    # Set the crop box to the specified coordinates
    crop_box = RectangleObject(crop_box_coordinates)
    first_page.cropbox = crop_box

    # Add the cropped page to the writer
    writer.add_page(first_page)

    # Write the cropped page to the output PDF
    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

    print(f"Cropped PDF saved as '{output_pdf}'.")

def create_blank_page_a4(output_pdf_with_blank):
    # A4 dimensions in points: 595 x 842 (portrait orientation)
    a4_width = 595
    a4_height = 842

    # Create a new PdfWriter for the final output
    final_writer = PdfWriter()

    # Create a blank A4 page
    blank_page = PageObject.create_blank_page(width=a4_width, height=a4_height)

    # Add the new page to the final writer
    final_writer.add_page(blank_page)

    # Write the final PDF to a new file
    with open(output_pdf_with_blank, "wb") as final_output_file:
        final_writer.write(final_output_file)

    print(f"Final PDF with cropped content centered on a blank A4 page saved as '{output_pdf_with_blank}'.")

def merge_content_left_top_scaled(pdf1_path, pdf2_path, output_path):
    # Lê os dois PDFs
    reader1 = PdfReader(pdf1_path)
    reader2 = PdfReader(pdf2_path)

    # Obtém a primeira página de cada PDF
    page1 = reader1.pages[0]
    page2 = reader2.pages[0]

    # Usa as dimensões da página de out2.pdf (page2)
    width = page2.mediabox.width
    height = page2.mediabox.height

    # Cria uma nova página com as dimensões de out2.pdf
    merged_page = PageObject.create_blank_page(width=width, height=height)

    # Adiciona o conteúdo da primeira página do PDF1 (out.pdf) à página mesclada
    # Aumenta a escala do conteúdo de out.pdf em 20% e posiciona no canto superior esquerdo
    scale_factor = 0.95  # Aumenta a escala em 20%
    scaled_width = page1.mediabox.width * scale_factor
    scaled_height = page1.mediabox.height * scale_factor

    # Garante que o conteúdo redimensionado não ultrapasse os limites da página de out2.pdf
    if scaled_width > width or scaled_height > height:
        print("Aviso: O conteúdo escalado de 'out.pdf' excede as dimensões de 'out2.pdf'.")

    # Posiciona o conteúdo no canto superior esquerdo
    tx = -13  # Alinhado à esquerda
    ty = height - scaled_height + 17  # Alinhado ao topo
    merged_page.merge_transformed_page(page1, Transformation().scale(scale_factor).translate(tx, ty))

    # Adiciona o conteúdo da primeira página do PDF2 (out2.pdf) à página mesclada
    merged_page.merge_page(page2)

    # Cria um PdfWriter para salvar o resultado
    writer = PdfWriter()
    writer.add_page(merged_page)

    # Salva o PDF combinado no arquivo de saída
    with open(output_path, "wb") as output_file:
        writer.write(output_file)

    print(f"Conteúdo dos PDFs '{pdf1_path}' e '{pdf2_path}' foi combinado em '{output_path}' com o conteúdo de '{pdf1_path}' no canto superior esquerdo e escalado em 20%.")

# paths and coordinates
input_pdf = "in.pdf"
output_pdf = "out.pdf"
output_pdf_with_blank = "out2.pdf"
output_pdf = "final.pdf"
crop_box_coordinates = [27, 143, 290, 570]

# Crop the PDF
crop_pdf(input_pdf, output_pdf, crop_box_coordinates)

# Center the cropped content on a blank A4 page
create_blank_page_a4(output_pdf_with_blank)

# Realiza o merge de conteúdo
merge_content_left_top_scaled(output_pdf, output_pdf_with_blank, output_pdf)