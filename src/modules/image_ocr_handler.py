import easyocr
import cv2

def extract_text_from_image(image_path):
    """
    Extracts text from an image using EasyOCR.
    To be used to extract text from images for user inputs.

    """
    try:
        # Initialize the EasyOCR reader
        reader = easyocr.Reader(['en'])  # 'en' for English

        # Read the image using OpenCV
        img = cv2.imread(image_path)

        # Check if the image was loaded successfully
        if img is None:
            return f"Error: Could not load image from {image_path}"

        # Perform OCR on the image
        results = reader.readtext(img)

        # Extract and concatenate the text from the results
        extracted_text = " ".join([result[1] for result in results])

        return extracted_text
    except Exception as e:
        return f"Error during text extraction: {str(e)}"

if __name__ == "__main__":
    image_path = "data/images/2024-02-25_3310289540023402853.jpg"
    extracted_text = extract_text_from_image(image_path)
    print(f"Extracted text: {extracted_text}")
