import os
from pathlib import Path

from pypdf import PageObject, PdfReader, PdfWriter, Transformation

from config import LABELS_PER_PAGE, RESULT_COORDINATES, SCALE_FACTOR, CUSTOM_LABEL_POSITIONS
from services.create_page_service import PDFPageCreator


class PDFLabelMerger:
    """
    Classe responsável por mesclar etiquetas em um PDF, organizando-as em páginas A4.
    """

    def __init__(self, labels_folder_path: str, output_pdf_path: str):
        """
        Inicializa o PDFLabelMerger.

        Args:
            labels_folder_path (str): Caminho para a pasta contendo os PDFs das etiquetas.
            output_pdf_path (str): Caminho para o arquivo PDF de saída.
        """
        self.labels_folder_path = labels_folder_path
        self.output_pdf_path = output_pdf_path
        self.scale_factor = SCALE_FACTOR  # Fator de escala para ajustar as etiquetas
        # Coordenadas (tx, ty) para posicionar cada etiqueta na página A4
        self.coordinates = RESULT_COORDINATES
        self.custom_label_positions = CUSTOM_LABEL_POSITIONS

        # Cria a primeira página em branco para o PDF de saída (página A4)
        print("[INFO] Criando a primeira página em branco para o PDF de saída.")
        PDFPageCreator().create_blank_page_a4(self.output_pdf_path)

        # Conta o número total de etiquetas encontradas na pasta
        self.num_of_labels = sum(1 for item in Path(labels_folder_path).iterdir() if item.is_file())
        print(f"[INFO] Número total de etiquetas encontradas: {self.num_of_labels}")

    def process_labels(self):
        """
        Processa e mescla as etiquetas no PDF de saída, organizando até 4 etiquetas por página.
        """
        print("[INFO] Iniciando o processo de mesclagem das etiquetas.")
        label_counter = 0
        page_index = 0  # Índice da página de destino atual
        coord_index = 0  # Índice das coordenadas para posicionamento da etiqueta
        custom_position_index = 0  # Índice para percorrer as posições personalizadas

        # Itera pelos arquivos de etiqueta (ordenados para garantir a sequência)
        for label_file in sorted(Path(self.labels_folder_path).iterdir()):
            # Somar o contador de etiquetas
            label_counter += 1

            # Verifica se existe uma posição personalizada para a página atual
            custom_position, custom_position_len = self.get_custom_position(page_index)
            
            # Define coordenadas
            coordinates = self.coordinates[coord_index] if not custom_position else self.coordinates[custom_position[custom_position_index]]

            # Mescla a etiqueta na página de destino
            print(f"[INFO] Mesclando etiqueta: {label_file.name}")
            self.merge_content(
                label_pdf_path=str(label_file),
                target_page_index=page_index,
                coordinates=coordinates,
            )

            # Atualiza os índices de controle
            coord_index = coord_index + 1 if not custom_position else custom_position[custom_position_index] + 1
            custom_position_index += 1 if custom_position else 0

            # Quando o numero máximo de etiquetas já foram inseridas na página corrente, acrescenta uma nova página em branco
            # Reseta o contador de etiquas e o índice de coordenadas
            if coord_index == LABELS_PER_PAGE or (custom_position and custom_position_index == custom_position_len):
                coord_index = 0
                page_index += 1
                custom_position_index = 0
                custom_position = None
                if label_counter < self.num_of_labels:
                    self.add_blank_page()

        print("[INFO] Processo de mesclagem concluído com sucesso.")

    def add_blank_page(self):
        """
        Adiciona uma página em branco ao PDF de saída.
        """
        print("[INFO] Adicionando uma página em branco ao PDF de saída.")
        temp_pdf_path = "temp.pdf"

        # Cria uma página A4 em branco e salva temporariamente
        PDFPageCreator().create_blank_page_a4(temp_pdf_path)

        writer = PdfWriter()
        try:
            reader = PdfReader(self.output_pdf_path)
            for page in reader.pages:
                writer.add_page(page)
        except FileNotFoundError:
            print(f"[WARNING] Arquivo '{self.output_pdf_path}' não encontrado. Será criado um novo arquivo.")

        # Insere a página em branco criada temporariamente
        temp_reader = PdfReader(temp_pdf_path)
        blank_page = temp_reader.pages[0]
        writer.add_page(blank_page)

        # Salva o PDF atualizado
        with open(self.output_pdf_path, "wb") as output_file:
            writer.write(output_file)
        print(f"[INFO] Página em branco adicionada ao arquivo '{self.output_pdf_path}'.")

        # Remove o arquivo temporário
        try:
            os.remove(temp_pdf_path)
            print("[INFO] Arquivo temporário 'temp.pdf' excluído com sucesso.")
        except FileNotFoundError:
            print("[WARNING] Arquivo temporário 'temp.pdf' não encontrado para exclusão.")
        except Exception as e:
            print(f"[ERROR] Erro ao tentar excluir 'temp.pdf': {e}")

    def merge_content(self, label_pdf_path: str, target_page_index: int, coordinates: dict):
        """
        Mescla uma etiqueta em uma página específica do PDF de saída, aplicando normalização,
        transformação de escala e translação para posicionamento correto na página A4.

        Args:
            label_pdf_path (str): Caminho para o PDF da etiqueta.
            target_page_index (int): Índice da página de destino onde a etiqueta será mesclada.
            coordinates (dict): Dicionário contendo 'tx' e 'ty' para posicionamento.
        """
        print(f"[INFO] Mesclando etiqueta '{label_pdf_path}' na página {target_page_index + 1}.")

        # Lê o PDF de saída e seleciona a página de destino
        output_reader = PdfReader(self.output_pdf_path)
        try:
            output_page = output_reader.pages[target_page_index]
        except IndexError:
            print(f"[ERROR] Página de destino {target_page_index + 1} não encontrada em '{self.output_pdf_path}'.")
            return

        # Lê o PDF da etiqueta (deve conter a cropBox já aplicada)
        label_reader = PdfReader(label_pdf_path)
        label_page = label_reader.pages[0]

        # Normaliza a etiqueta com base na cropBox para redefinir o sistema de coordenadas
        crop_box = label_page.cropbox  # Supõe que o corte já foi realizado
        llx, lly = float(crop_box.lower_left[0]), float(crop_box.lower_left[1])
        urx, ury = float(crop_box.upper_right[0]), float(crop_box.upper_right[1])
        normalized_width = urx - llx
        normalized_height = ury - lly

        print(f"[INFO] Normalizando etiqueta com cropBox: ({llx}, {lly}, {urx}, {ury})")

        # Cria um novo objeto de página com as dimensões do cropBox e reposiciona o conteúdo
        normalized_label_page = PageObject.create_blank_page(width=normalized_width, height=normalized_height)
        normalized_label_page.merge_transformed_page(
            label_page,
            Transformation().translate(-llx, -lly)
        )

        # Prepara a página de destino (formato A4) para a mesclagem
        page_width = output_page.mediabox.width
        page_height = output_page.mediabox.height
        merged_page = PageObject.create_blank_page(width=page_width, height=page_height)

        # Aplica transformação: escala e translação para posicionar a etiqueta na página A4
        tx = coordinates.get("tx", 0)
        ty = coordinates.get("ty", 0)
        merged_page.merge_transformed_page(
            normalized_label_page,
            Transformation().scale(self.scale_factor).translate(tx, ty)
        )
        print(f"[INFO] Etiqueta posicionada em (tx: {tx}, ty: {ty}).")

        # Mescla o conteúdo da página de destino original com a nova composição
        merged_page.merge_page(output_page)

        # Atualiza o PDF de saída preservando todas as páginas
        writer = PdfWriter()
        reader = PdfReader(self.output_pdf_path)
        total_pages = len(reader.pages)

        # Adiciona as páginas anteriores (caso existam)
        for i in range(target_page_index):
            writer.add_page(reader.pages[i])
        # Insere a página atual mesclada
        writer.add_page(merged_page)
        # Adiciona as páginas subsequentes (se houver)
        for i in range(target_page_index + 1, total_pages):
            writer.add_page(reader.pages[i])

        # Salva o PDF de saída atualizado
        with open(self.output_pdf_path, "wb") as output_file:
            writer.write(output_file)
        print(f"[INFO] Conteúdo mesclado salvo no arquivo '{self.output_pdf_path}'.")

        # Fecha os leitores (se necessário, dependendo da versão do PyPDF)
        writer.close()
        output_reader.close()
        label_reader.close()

    def get_custom_position(self, page_index: int):
        try:
            return self.custom_label_positions[page_index], self.custom_label_positions[page_index].__len__()
        except Exception as e:
            return None, 0