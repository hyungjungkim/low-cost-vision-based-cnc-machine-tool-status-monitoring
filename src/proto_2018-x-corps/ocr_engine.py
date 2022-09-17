import tesserocr
from tesserocr import PyTessBaseAPI
from PIL import Image
import cv2


class OCREngine:
    api = None

    def __init__(self, lang='cnc-2018', path='C:\\Program Files\\Tesseract-OCR\\tessdata'):
        self.api = PyTessBaseAPI(lang=lang, path=path)

    def ocr_process(self, image):
        self.api.SetImage(image)

        ocr_res = self.api.GetUTF8Text()
        ocr_res = ocr_res.replace('\n', '')

        return ocr_res


if __name__ == '__main__':
    print('standalone test')

    sample_image = cv2.imread('test_image/roi_image_sample-2.jpg')

    ocr_engine = OCREngine()

    image = Image.fromarray(sample_image)
    ocr_res = ocr_engine.ocr_process(image)

    print(ocr_res)
