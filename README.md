# 비전 기반 레거시 HMI 상태 모니터링 Vision-based Status Monitoring for Legacy HMI

## 요약 Summary
이 저장소는 적정 상태 모니터링 도구로써 KEM(Keep an Eye on your Machine)을 소개합니다. 이 도구는 제조업의 중소기업이나 개발도상국에서 웹캠과 같은 저가의 비전 센서와 OpenCV와 Tesseract OCR를 포함하는 오픈소스 기술들을 이용해서 사용될 수 있습니다.
이 아이디어는 저렴하고 사용하기 쉬운 요소들을 사용하여 일종의 스마트 개조와 같이 관심 HMI나 장비의 운영 상태 데이터를 수집하고 처리하는 것에 중점을 두고 있습니다.

This repository presents an appropriate status monitoring tool, KEM (Keep an Eye on your Machine). This tool can be used for such as Small and Medium-sized Enterprises (SMEs) in the manufacturing sector or developing countries using a low-cost vision sensor, such as a webcam, and open-source technologies, including OpenCV and Tesseract OCR. Mainly, this idea focuses on collecting and processing operational status data of target HMI or machine using cheaper and easy-to-use components, like smart retrofitting.

### 상태 모니터링 개념도 Conceptual diagram of status monitoring  
![Proposed monitoring idea](figure-3.png 'Proposed monitoring idea')

### 일반적인 OCR 처리 과정 Typical workflow of OCR process  
![Workflow of OCR process](figure-1.png 'Workflow of OCR process')

### 사례 #1. 디지털 표시기 Case #1. Digital indicator
이 데모는 일반적인 디지털 표시기의 수치를 모니터링 하도록 구성되었습니다.
This demo is designed to monitor typical digital indicators/gauges. <br/>


### 사례 #2. CNC 공작기계 HMI Case #2. HMI of CNC machine tool  
이 데모는 일반적인 CNC 공작기계를 모니터링 하도록 구성되었습니다.
This demo is designed to monitor typical computer numerical control (CNC) machine tools.<br/>

![Example configuration of demo](figure-8.png 'Example configuration of demo')

## 필수 라이브러리 Dependencies
- cv2, numpy, pillow, pytesseract: any version after 2019
- tesserocr: v2.5.2 (tesseract 4.1.1) [[Download Link](https://github.com/simonflueckiger/tesserocr-windows_build/releases/tag/tesserocr-v2.5.2-tesseract-4.1.1)] (You should install an appropriate wheel for your installed python version.)
- tesseract-ocr engine: Latest release of v4 [[Download Link](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v4.1.0.20190314.exe)] ([UB-Mannheim's tesseract](https://github.com/UB-Mannheim/tesseract/wiki))

## 사용 방법 How to use
- Proto_2018-x-corps [(한글)](docs/how_to_use_proto_2018-x-corps_kr.md), [(English)](docs/how_to_use_proto_2018-x-corps_en.md)
- Webcam selector [(한글)](), [(English)]()
- Proto_2022-CDE_DX_Award [(한글)](), [(English)]()

## 관련 논문 Related publication
- Kim, H., Jung, W. K., Choi, I. G., & Ahn, S. H. (2019). A low-cost vision-based monitoring of computer numerical control (CNC) machine tools for small and medium-sized enterprises (SMEs). Sensors, 19(20), 4506. [[Link](https://doi.org/10.3390/s19204506)]
 - Kim. H. (2022). Open-source software for developing appropriate smart manufacturing technology for small and medium-sized enterprises (SMEs), Journal of Appropriate Technology - Accepted. [[Link]()], [[GitHub](https://github.com/hyungjungkim/enabling-oss-for-appropriate-smart-manufacturing-in-smes)]
