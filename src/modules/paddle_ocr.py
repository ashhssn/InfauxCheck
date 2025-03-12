import cv2
from paddleocr import PaddleOCR

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using PaddleOCR.
    """
    ocr = PaddleOCR(use_angle_cls=True, lang='en')  # 'en' for English; adjust as needed
    
    # Load the image
    image = cv2.imread(image_path)

    # Check if image loaded successfully
    if image is None:
        raise ValueError(f"Failed to load image at {image_path}")

    # Perform OCR
    result = ocr.ocr(image, cls=True)

    # Extract the text
    text = " ".join([line[1][0] for line in result[0]])

    return text

if __name__ == "__main__":
    image_path = 'data/images/2024-02-25_3310289540023402853.jpg'  # Replace with your image path
    data = extract_text_from_image(image_path)
    print(f"Extracted text: {data}")