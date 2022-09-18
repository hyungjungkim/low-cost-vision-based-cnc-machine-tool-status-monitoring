# Low-cost vision-based CNC machine tool status monitoring

## Summary
This repository presents an appropriate monitoring approach, KEM (Keep an Eye on your Machine), for Small and Medium-sized Enterprises (SMEs) in the manufacturing sector using a low-cost vision, such as a webcam, and open-source technologies, including OpenCV and Tesseract OCR. Mainly, this idea focuses on collecting and processing operational data using cheaper and easy-to-use components, like smart retrofitting.

**Workflow of OCR process**  
![Workflow of OCR process](figure-1.png 'Workflow of OCR process')

**Proposed monitoring idea**  
![Proposed monitoring idea](figure-3.png 'Proposed monitoring idea')

**Example configuration of demo**  
![Example configuration of demo](figure-8.png 'Example configuration of demo')

The first demo is designed for the typical computer numerical control (CNC) machine tool.

## Dependencies
- cv2, numpy, pillow, pytesseract: any version after 2019
- tesserocr: v2.5.2 (tesseract 4.1.1)
- tesseract-ocr engine: Latest release of v4 ([UB-Mannheim's tesseract](https://github.com/UB-Mannheim/tesseract/wiki))

## How to use
- [Proto_2018-x-corps (Korean)](docs/how_to_use_proto_2018-x-corps_kr.md), [Proto_2018-x-corps (English)](docs/how_to_use_proto_2018-x-corps_en.md)

## Related publication
- Kim, H., Jung, W. K., Choi, I. G., & Ahn, S. H. (2019). A low-cost vision-based monitoring of computer numerical control (CNC) machine tools for small and medium-sized enterprises (SMEs). Sensors, 19(20), 4506. [[Link](https://doi.org/10.3390/s19204506)]
