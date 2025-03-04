from config import INPUT_PDF_PATH, CROPPED_LABELS_FOLDER, FINAL_OUTPUT_PDF_PATH
from services.crop_labels_service import PDFCropper
from services.generate_merged_labels_service import PDFLabelMerger

def main():
    """
    Função principal para processar um PDF:
    1. Recorta etiquetas de um PDF de entrada e salva em arquivos individuais.
    2. Mescla as etiquetas recortadas em um único PDF organizado em páginas A4.
    """

    # Caminhos de entrada e saída
    input_pdf_path = INPUT_PDF_PATH  # Caminho para o PDF de entrada
    cropped_labels_folder = CROPPED_LABELS_FOLDER  # Pasta para salvar as etiquetas recortadas
    final_output_pdf_path = FINAL_OUTPUT_PDF_PATH  # Caminho para o PDF final mesclado

    print("[INFO] Iniciando o processamento do PDF.")

    # Etapa 1: Recortar etiquetas do PDF de entrada
    print("[INFO] Etapa 1: Recortando etiquetas do PDF de entrada.")
    cropper = PDFCropper(input_pdf_path, cropped_labels_folder)
    cropper.crop_labels()
    print("[INFO] Recorte de etiquetas concluído. Etiquetas salvas na pasta:", cropped_labels_folder)

    # Etapa 2: Mesclar etiquetas recortadas em um único PDF
    print("[INFO] Etapa 2: Mesclando etiquetas recortadas em um único PDF.")
    label_merger = PDFLabelMerger(cropped_labels_folder, final_output_pdf_path)
    label_merger.process_labels()
    print("[INFO] Mesclagem de etiquetas concluída. PDF final salvo em:", final_output_pdf_path)

    print("[INFO] Processamento do PDF concluído com sucesso.")

if __name__ == "__main__":
    main()
