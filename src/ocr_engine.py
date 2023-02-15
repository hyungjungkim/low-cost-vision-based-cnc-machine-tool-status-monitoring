import pytesseract
import platform
from PIL import Image

class OCREngine():
    tessdata_config = None

    def __init__(self, tesseract_exe_loc):
        if(platform.system() == 'Windows') :
            pytesseract.pytesseract.tesseract_cmd = r'' + tesseract_exe_loc

    def execute_ocr(self, image, data_path):
        tessdata_config  = r'--tessdata-dir "'+ data_path + '" --psm 6'
        ocr_res = pytesseract.image_to_string(image, lang = 'cnc-2018', config = tessdata_config)
        ocr_res = ocr_res.replace('\n','')
        ocr_res = ocr_res[:-1]

        # Post-processing for improvement
        ocr_res = ocr_res.replace(' ', '')
        ocr_res = ocr_res.replace('D', '0')
        ocr_res = ocr_res.replace('I', '1')
        ocr_res = ocr_res.replace('G', '1')
        ocr_res = ocr_res.replace('B', '8')

        return ocr_res

if __name__ == '__main__':
    ocr_engine = OCREngine('C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
    
    image = Image.open('sample_image/roi_image_sample-1.jpg')
    ocr_res = ocr_engine.execute_ocr(image, "C:\\Program Files\\Tesseract-OCR\\tessdata")
    print(ocr_res)

    image = Image.open('sample_image/roi_image_sample-2.jpg')
    ocr_res = ocr_engine.execute_ocr(image, "C:\\Program Files\\Tesseract-OCR\\tessdata")
    print(ocr_res)

    image = Image.open('sample_image/roi_image_sample-3.jpg')
    ocr_res = ocr_engine.execute_ocr(image, "C:\\Program Files\\Tesseract-OCR\\tessdata")
    print(ocr_res)