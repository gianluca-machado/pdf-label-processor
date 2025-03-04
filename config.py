# Name of the input PDF file
INPUT_PDF_PATH = "in.pdf"

# Folder to save the cropped labels
CROPPED_LABELS_FOLDER = "labels/"

# Name of the final output PDF file
FINAL_OUTPUT_PDF_PATH = "final.pdf"

# Width of the label to be cropped
LABEL_WIDTH = 265

# Coordinates for the crop box templates [x0, y0, x1, y1]
CROP_BOX_TEMPLATES = [
    [27, 143, 290, 570],  # First label
    [27 + LABEL_WIDTH, 143, 290 + LABEL_WIDTH, 570],  # Second label
    [27 + (LABEL_WIDTH * 2), 143, 290 + (LABEL_WIDTH * 2), 570],  # Third label
]

# Expected width and height for the label to be processed
LABEL_WIDTH_PROCCESS = 841.8898
LABEL_HEIGHT_PROCCESS = 595.2756

# Expected texts to be present in the cropped label
EXPECTED_TEXTS_LABEL = ["NF:", "NFe:", "JADLEVE"]

# Scale factor to be applied to the label
SCALE_FACTOR = 0.91

# Coordinates (tx, ty) to position each label on the A4 page
RESULT_COORDINATES = [
    {"tx": 10,  "ty": 445},  # 1ª etiqueta
    {"tx": 345, "ty": 445},  # 2ª etiqueta
    {"tx": 10,  "ty": 10},   # 3ª etiqueta
    {"tx": 345, "ty": 10},   # 4ª etiqueta
]

# Number of labels per page
LABELS_PER_PAGE = 4

# Custom label positions
# | 0 | 1 |
# | 2 | 3 |
CUSTOM_LABEL_POSITIONS = []