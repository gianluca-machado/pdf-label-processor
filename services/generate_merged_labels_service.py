import os
from pathlib import Path

from pypdf import PageObject, PdfReader, PdfWriter, Transformation

from services.create_page_service import PDFPageCreator


class PDFLabelMerger:
    """
    Classe responsável por mesclar etiquetas em um PDF, organizando-as em páginas A4.
    """

    def __init__(self, labels_folder_path, output_pdf_path):
        """
        Inicializa o PDFLabelMerger.

        Args:
            labels_folder_path (str): Caminho para a pasta contendo os PDFs das etiquetas.
            output_pdf_path (str): Caminho para o arquivo PDF de saída.
        """
        self.labels_folder_path = labels_folder_path
        self.output_pdf_path = output_pdf_path
        self.scale_factor = 0.95  # Fator de escala para ajustar as etiquetas
        self.coordinates = [
            {"tx": -13,  "ty": 17},      # Coordenadas para a 1ª etiqueta
            {"tx": 50,   "ty": 17},       # Coordenadas para a 2ª etiqueta
            {"tx": -515, "ty": -413},   # Coordenadas para a 3ª etiqueta
            {"tx": 301,  "ty": -413},    # Coordenadas para a 4ª etiqueta
        ]

        # Cria a primeira página em branco no arquivo de saída
        page_creator = PDFPageCreator()
        page_creator.create_blank_page_a4(output_pdf_path)

        # Conta o número de arquivos de etiquetas na pasta
        self.num_of_labels = sum(1 for item in Path(labels_folder_path).iterdir() if item.is_file())
        print(f"[INFO] Número total de etiquetas encontradas: {self.num_of_labels}")

    def process_labels(self):
        """
        Processa as etiquetas, mesclando-as no PDF de saída.
        Cada página A4 pode conter até 4 etiquetas.
        """
        print("[INFO] Iniciando o processo de mesclagem das etiquetas.")
        label_counter = 0
        page_counter = 0
        coordinate_index = 0

        for label_file in Path(self.labels_folder_path).iterdir():
            if label_file.is_file():
                print(f"[INFO] Mesclando etiqueta: {label_file.name}")
                self.merge_content(
                    label_pdf_path=str(label_file),
                    output_pdf_path=self.output_pdf_path,
                    target_page_index=page_counter,
                    coordinates=self.coordinates[coordinate_index]
                )

                label_counter += 1
                coordinate_index += 1

                # Se 4 etiquetas forem adicionadas, cria uma nova página
                if coordinate_index == 4:
                    coordinate_index = 0
                    page_counter += 1
                    if label_counter < self.num_of_labels:
                        self.add_blank_page(self.output_pdf_path)

        print("[INFO] Processo de mesclagem concluído com sucesso.")

    def add_blank_page(self, output_pdf_path):
        """
        Adiciona uma página em branco ao PDF de saída.

        Args:
            output_pdf_path (str): Caminho para o arquivo PDF de saída.
        """
        print("[INFO] Adicionando uma página em branco ao PDF de saída.")
        temp_pdf_path = "temp.pdf"

        # Cria uma página em branco temporária
        page_creator = PDFPageCreator()
        page_creator.create_blank_page_a4(temp_pdf_path)

        # Lê o PDF de saída existente
        writer = PdfWriter()
        try:
            reader = PdfReader(output_pdf_path)
            for page in reader.pages:
                writer.add_page(page)
        except FileNotFoundError:
            print(f"[WARNING] Arquivo '{output_pdf_path}' não encontrado. Criando um novo arquivo.")

        # Adiciona a página em branco ao PDF
        temp_reader = PdfReader(temp_pdf_path)
        blank_page = temp_reader.pages[0]
        writer.add_page(blank_page)

        # Salva o PDF atualizado
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)

        print(f"[INFO] Página em branco adicionada ao arquivo '{output_pdf_path}'.")

        # Remove o arquivo temporário
        try:
            os.remove(temp_pdf_path)
            print("[INFO] Arquivo temporário 'temp.pdf' excluído com sucesso.")
        except FileNotFoundError:
            print("[WARNING] Arquivo temporário 'temp.pdf' não encontrado para exclusão.")
        except Exception as e:
            print(f"[ERROR] Erro ao tentar excluir 'temp.pdf': {e}")

    def merge_content(self, label_pdf_path, output_pdf_path, target_page_index, coordinates):
        """
        Mescla uma etiqueta em uma página específica do PDF de saída.

        Args:
            label_pdf_path (str): Caminho para o PDF da etiqueta.
            output_pdf_path (str): Caminho para o PDF de saída.
            target_page_index (int): Índice da página no PDF de saída onde a etiqueta será mesclada.
            coordinates (dict): Coordenadas de transformação (tx, ty) para posicionar a etiqueta.
        """
        print(f"[INFO] Mesclando conteúdo da etiqueta '{label_pdf_path}' na página {target_page_index + 1}.")

        # Lê a etiqueta e a página de destino
        label_page = PdfReader(label_pdf_path).pages[0]
        output_page = PdfReader(output_pdf_path).pages[target_page_index]

        # Dimensões da página de destino
        page_width = output_page.mediabox.width
        page_height = output_page.mediabox.height

        # Cria uma nova página em branco com as dimensões da página de destino
        merged_page = PageObject.create_blank_page(width=page_width, height=page_height)

        # Calcula a posição escalada da etiqueta
        scaled_height = label_page.mediabox.height * self.scale_factor
        tx = coordinates["tx"]
        ty = page_height - scaled_height + coordinates["ty"]

        # Mescla a etiqueta na nova página
        merged_page.merge_transformed_page(
            label_page,
            Transformation().scale(self.scale_factor).translate(tx, ty)
        )
        print(f"[INFO] Etiqueta posicionada em (tx: {tx}, ty: {ty}).")

        # Mescla a página de destino com a nova página
        merged_page.merge_page(output_page)

        # Atualiza o PDF de saída com a nova página mesclada
        writer = PdfWriter()
        reader = PdfReader(output_pdf_path)

        # Adiciona todas as páginas anteriores ao writer
        for i in range(target_page_index):
            writer.add_page(reader.pages[i])

        # Adiciona a página mesclada
        writer.add_page(merged_page)

        # Salva o PDF atualizado
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)

        print(f"[INFO] Conteúdo mesclado salvo no arquivo '{output_pdf_path}'.")
