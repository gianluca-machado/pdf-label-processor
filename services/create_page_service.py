from pypdf import PageObject, PdfWriter


class PDFPageCreator:
    def __init__(self):
        """
        Inicializa o PDFPageCreator com um objeto PdfWriter.
        """
        self.writer = PdfWriter()
        print("[INFO] PDFPageCreator inicializado com um PdfWriter.")

    def create_blank_page_a4(self, output_file_path):
        """
        Cria uma página em branco no formato A4 e salva em um arquivo PDF.

        Args:
            output_file_path (str): Caminho para salvar o arquivo PDF gerado.
        """
        print("[INFO] Iniciando o processo de criação de uma página em branco no formato A4.")

        # Dimensões de uma página A4 em pontos (595 x 842, orientação retrato)
        a4_width_points = 595
        a4_height_points = 842
        print(f"[INFO] Dimensões da página A4 definidas: {a4_width_points} x {a4_height_points} pontos.")

        # Cria uma página em branco no formato A4
        blank_a4_page = PageObject.create_blank_page(width=a4_width_points, height=a4_height_points)
        print("[INFO] Página em branco no formato A4 criada com sucesso.")

        # Adiciona a página em branco ao escritor de PDF
        self.writer.add_page(blank_a4_page)

        # Salva o PDF com a página em branco no caminho especificado
        try:
            with open(output_file_path, "wb") as output_file:
                self.writer.write(output_file)
            print(f"[INFO] PDF com a página em branco salvo com sucesso em: {output_file_path}")
        except Exception as e:
            print(f"[ERROR] Ocorreu um erro ao salvar o PDF: {e}")
