# For OCR processing
import cv2
from PIL import Image
from threading import Thread
import ocr_engine

# For GUI
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5 import uic, QtGui
KEM_CLIENT_UI_PATH = 'kem_cncmt_client_ui_v2.0.ui'
ROI_EDITOR_UI_PATH = 'roi_editor_ui_v2.0.ui'

# Misc.
import numpy as np
import pickle # For saving roi data in file
import time # For calculating time in processing
from datetime import date # For getting a date
import random # For saving roi image for test purpose

# options
RUN_CONSOLE_ONLY_MODE = True

RUN_WITHOUT_WEBCAM_MODE = True
RUN_UPSIDE_DOWN_MODE = False
RUN_WITHOUT_SCREEN_MODE = False
WEBCAM_INDEX = 0
SAMPLE_IMAGE = 'test_data/hmi_screen_ex-1.jpg'
WEBCAM_FOCUS_AUTO = False
SAVE_ROI_IMAGE = False

TESSERACTOCR_DIR = 'C:\\Program Files\\Tesseract-OCR\\tessdata'

class ROIEditor(QDialog):
    name = ''
    selected_index = 0
    x, y, width, height = -1, -1, -1, -1
    threshold = 0  # cv2 threshold manipulation
    type = 0  # int 0, float 1, string 2

    def __init__(self, parent=None):
        super().__init__()
        self.ui = uic.loadUi(ROI_EDITOR_UI_PATH, self)
        self.ui.show()

        self.cbbParam.currentIndexChanged.connect(self.on_param_select)

    def on_param_select(self):
        self.selected_index = self.cbbParam.currentIndex()

        if self.selected_index == 2 or self.selected_index == 12:
            self.txtType.setText('1')  # String
        else:
            self.txtType.setText('0')  # Numeric

    def accept(self):
        # update data
        self.name = self.cbbParam.currentText()
        self.x = int(self.txtLocX.text())
        self.y = int(self.txtLocY.text())
        self.width = int(self.txtSizeW.text())
        self.height = int(self.txtSizeH.text())
        self.threshold = int(self.txtThreshold.text())
        self.type = int(self.txtType.text())
        self.done(1)

    def reject(self):
        self.done(0)


class ROI:
    name = 'param_id'
    x, y, width, height = -1, -1, -1, -1
    threshold = 0  # cv2 threshold manipulation
    type = 0  # numeric 0, text 1, mixed 2
    data_id = ''
    roi_image = None
    ocr_res = ''

    def set_name(self, name):
        self.name = name

    def set_location(self, x, y):
        self.x, self.y = x, y

    def set_size(self, width, height):
        self.width, self.height = width, height

    def set_threshold(self, threshold):
        self.threshold = threshold

    def set_type(self, type):
        self.type = type

    def set_id(self, index):
        if index < 10:
            index = 'data_00' + str(index)
        else:
            index = 'data_0' + str(index)

        self.data_id = index

    def set_roi_image(self, roi_image):
        self.roi_image = roi_image

    def set_ocr_res(self, ocr_res):
        self.ocr_res = ocr_res
    
    def __getstate__(self):
        return (self.name, self.x, self.y, self.width, self.height, self.threshold,
        self.type, self.data_id, self.roi_image, self.ocr_res)

    def __setstate__(self, state):
        name, x, y, width, height, threshold, type, data_id, roi_image, ocr_res = state
        self.name, self.x, self.y, self.width, self.height, self.threshold = name, x, y, width, height, threshold
        self.type, self.data_id, self.roi_image, self.ocr_res = type, data_id, roi_image, ocr_res


class KEM_CNCMT_Client(QMainWindow):
    sample_image = None

    if RUN_WITHOUT_WEBCAM_MODE:
        sample_image = cv2.imread(SAMPLE_IMAGE)

    image, image_, capture, rectangle, threshold = None, None, False, False, False
    col, row, width, height = -1, -1, -1, -1
    thresholdvalue = 0
    margin_width, margin_height = 100, 30
    roi_list = []

    ocr_engine = ocr_engine.OCREngine()

    run = False

    webcam_focus = 30
    
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(KEM_CLIENT_UI_PATH, self)
        self.ui.show()

        self.actionLoad.triggered.connect(self.load_roi_data)
        self.actionSave.triggered.connect(self.save_roi_data)
        self.actionExit.triggered.connect(self.close)
        self.actionConnect.triggered.connect(self.connect_camera)

        self.btnAdd.clicked.connect(self.add_region)

        self.btnRun.clicked.connect(self.run)
        self.btnFinish.clicked.connect(self.finish)

    def load_roi_data(self):
        with open('roi_data.kem', 'rb') as input:
            self.roi_list = pickle.load(input)

        self.update_region()

        self.lwLog.addItem('ROI data is loaded. %s' % (time.ctime()))

    def save_roi_data(self):
        with open('roi_data.kem', 'wb') as output:  # Overwrites any existing file.
            pickle.dump(self.roi_list, output, pickle.HIGHEST_PROTOCOL)

        self.lwLog.addItem('ROI data is saved. %s' % (time.ctime()))

    def add_region(self):
        self.dialog = ROIEditor(self)

        self.dialog.txtLocX.setText(str(self.col))
        self.dialog.txtLocY.setText(str(self.row))
        self.dialog.txtSizeW.setText(str(self.width))
        self.dialog.txtSizeH.setText(str(self.height))
        self.dialog.txtThreshold.setText(str(self.thresholdvalue))
        self.dialog.txtType.setText('0')

        self.dialog.show()
        if self.dialog.exec_():
            roi = ROI()
            roi.set_name(self.dialog.name)
            roi.set_location(self.dialog.x, self.dialog.y)
            roi.set_size(self.dialog.width, self.dialog.height)
            roi.set_threshold(self.dialog.threshold)
            roi.set_type(self.dialog.type)
            roi.set_id(self.dialog.selected_index)
            self.roi_list.append(roi)

            self.update_region()
            self.lwLog.addItem('1 ROI is added. %s' % (time.ctime()))

    def update_region(self):
        self.lwRegion.clear()

        index = 1
        for roi in self.roi_list:
            roi_info = '%i. %s: W:%s H:%s' % (index, roi.name, roi.width, roi.height)
            self.lwRegion.addItem(roi_info)

            index += 1

    def update_to_client(self):
        self.lwOCRResult.clear()

        index = 1

        for roi in self.roi_list:
            self.lwOCRResult.addItem('%i. %s' % (index, roi.name))
            self.lwOCRResult.addItem(': %s' % str(roi.ocr_res))

            index += 1

    def ocr_execute(self, roi_image, roi_data):
        ocr_res = self.ocr_engine.ocr_process(roi_image)

        print(ocr_res)

        # Post-process for improvement
        ocr_res = ocr_res.replace(' ', '')
        ocr_res = ocr_res.replace('D', '0')
        ocr_res = ocr_res.replace('I', '1')
        ocr_res = ocr_res.replace('G', '1')
        ocr_res = ocr_res.replace('B', '8')

        if ocr_res.replace('.', '', 1).isdigit():
            roi_data.set_ocr_res(ocr_res)

    def run(self):
        if len(self.roi_list) < 1:
            self.lwLog.addItem('No ROI info error. %s' % (time.ctime()))
            return

        self.run = True

        self.lwLog.addItem('Monitoring is started. %s' % (time.ctime()))

        cap_webcam = cv2.VideoCapture(WEBCAM_INDEX)  # from webcam

        if not WEBCAM_FOCUS_AUTO:
            cap_webcam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            cap_webcam.set(cv2.CAP_PROP_FOCUS, self.webcam_focus)

        cap_webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap_webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while self.run:
            success, image = cap_webcam.read()

            if RUN_WITHOUT_WEBCAM_MODE:
                image = self.sample_image

            if RUN_UPSIDE_DOWN_MODE:
                rows, cols = image.shape[:2]
                temp_image = cv2.getRotationMatrix2D((cols / 2, rows / 2), 180, 1)
                image = cv2.warpAffine(image, temp_image, (cols, rows))

            today = str(date.today())
            now = str(time.strftime("%H:%M:%S"))

            for roi in self.roi_list:
                col, row, width, height, threshold = roi.x, roi.y, roi.width, roi.height, roi.threshold
                margin = 20

                if not RUN_WITHOUT_SCREEN_MODE:
                    cv2.rectangle(image, (col, row), (col + width, row + height), (0, 255, 0), 5)

                    cv2.imshow('monitor', image)

                roi_image = image[row: row + height, col: col + width]
                roi_base = np.zeros((height + 2 * margin, width + 2 * margin, 3), np.uint8) + 255
                roi_base[margin: height + margin, margin: margin + width] = roi_image

                gray_image = cv2.cvtColor(roi_base, cv2.COLOR_BGR2GRAY)

                success, roi_image = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)

                roi.set_roi_image(Image.fromarray(roi_image))

                if SAVE_ROI_IMAGE:
                    cv2.imwrite('%i.jpg' % random.randint(1, 20), roi_image)

                if cv2.waitKey(25) & 0xFF == ord('f'):
                    break

            # OCR processing
            start = time.time()

            threads = []

            for roi in self.roi_list:
                threads.append(Thread(target=self.ocr_execute, args=(roi.roi_image, roi,)))

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            end = time.time()

            ocr_elapsed = end - start

            # print('all OCR time: %s' % ocr_elapsed)

            time.sleep(1.0 - ocr_elapsed)

            self.update_to_client()

            self.statusbar.showMessage('OCR processing (sec.): %f' % ocr_elapsed)

            self.repaint()

        cap_webcam.release()
        cv2.destroyAllWindows()

    def finish(self):
        self.run = False

        self.lwLog.addItem('Monitoring is finished. %s' % (time.ctime()))

    def onChange(self, x):
        pass

    def onMouse(self, event, x, y, flags, param):
        if self.capture:
            if event == cv2.EVENT_LBUTTONDOWN:
                self.rectangle = True
                self.col, self.row = x, y
            elif event == cv2.EVENT_MOUSEMOVE:
                if self.rectangle:
                    self.image = self.image_.copy()
                    cv2.rectangle(self.image, (self.col, self.row), (x, y), (0, 255, 0), 2)
                    cv2.imshow('image', self.image)
            elif event == cv2.EVENT_LBUTTONUP:
                self.capture = False
                self.rectangle = False
                cv2.rectangle(self.image, (self.col, self.row), (x, y), (0, 255, 0), 2)
                self.height, self.width = abs(self.row - y), abs(self.col - x)

                print('col %s, row %s, width %s, height %s' % (self.col, self.row, self.width, self.height))

                roi_image = self.image[self.row:self.row + self.height, self.col:self.col + self.width]
                roi_base = np.zeros((self.height + 2 * self.margin_height, self.width + 2 * self.margin_width, 3),
                                    np.uint8) + 255
                roi_base[self.margin_height:self.height + self.margin_height,
                self.margin_width:self.margin_width + self.width] = roi_image

                cv2.namedWindow('threshold')
                cv2.imshow('threshold', roi_base)
                cv2.createTrackbar('thresholdbar', 'threshold', 0, 255, self.onChange)

                self.threshold = True

                thresholdvalue = 0

                while self.threshold:
                    k = cv2.waitKey(25) & 0xFF
                    if k == ord('t'):
                        self.threshold = False
                        self.thresholdvalue = thresholdvalue

                        self.add_region()

                        break

                    roi_grayscale = cv2.cvtColor(roi_base, cv2.COLOR_BGR2GRAY)
                    thresholdvalue = cv2.getTrackbarPos('thresholdbar', 'threshold')

                    ret, thr1 = cv2.threshold(roi_grayscale, thresholdvalue, 255, cv2.THRESH_BINARY)
                    cv2.imshow('threshold', thr1)

                cv2.destroyWindow('threshold')

        return

    def set_camera_focus(self, value):
        self.webcam_focus += value

        if self.webcam_focus < 0:
            self.webcam_focus = 0
        elif self.webcam_focus > 250:
            self.webcam_focus = 250

        print('webcam focus = %i' % self.webcam_focus)

    def connect_camera(self):
        # vidCap = cv2.VideoCapture('sample_big.mov')
        vidCap = cv2.VideoCapture(WEBCAM_INDEX)  # for webcam
        print('start video capture')

        if not WEBCAM_FOCUS_AUTO:
            vidCap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            vidCap.set(cv2.CAP_PROP_FOCUS, self.webcam_focus)

        vidCap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        vidCap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.onMouse)

        while True:
            vidCap.set(cv2.CAP_PROP_FOCUS, self.webcam_focus)

            success, self.image = vidCap.read()

            if RUN_WITHOUT_WEBCAM_MODE:
                self.image = self.sample_image

            if RUN_UPSIDE_DOWN_MODE:
                rows, cols = self.image.shape[:2]
                temp_image = cv2.getRotationMatrix2D((cols / 2, rows / 2), 180, 1)
                self.image = cv2.warpAffine(self.image, temp_image, (cols, rows))
                # self.image = cv2.flip(usd_image, 1)

            if not success and not RUN_WITHOUT_WEBCAM_MODE:
                print('Fail to read a video image')
                break

            cv2.imshow('image', self.image)

            key = cv2.waitKey(25) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('i'):
                self.set_camera_focus(5)
            elif key == ord('o'):
                self.set_camera_focus(-5)
            elif key == ord('c'):
                self.capture = True
                self.image_ = self.image.copy()

                while self.capture:
                    cv2.imshow('image', self.image)
                    cv2.waitKey(0)

        vidCap.release()
        cv2.destroyAllWindows()

class KEMConsole():
    sample_image = None

    if RUN_WITHOUT_WEBCAM_MODE:
        sample_image = cv2.imread(SAMPLE_IMAGE)

    image, image_, capture, rectangle, threshold = None, None, False, False, False
    col, row, width, height = -1, -1, -1, -1
    thresholdvalue = 0
    margin_width, margin_height = 100, 30
    roi_list = []

    ocr_engine = ocr_engine.OCREngine()
    
    run = False

    def __init__(self, parent=None):
        pass

    def load_roi_data(self):
        with open('roi_data.kem', 'rb') as input:
            self.roi_list = pickle.load(input)

        print('ROI data is loaded. %s' % (time.ctime()))

    def update_to_console(self):
        index = 1

        for roi in self.roi_list:
            print('%i. %s: %s' % (index, roi.name, roi.ocr_res))

            index += 1

    def ocr_execute(self, roi_image, roi_data):
        ocr_res = self.ocr_engine.ocr_process(roi_image)

        # post-processing
        ocr_res = ocr_res.replace(' ', '')
        ocr_res = ocr_res.replace('D', '0')
        ocr_res = ocr_res.replace('I', '1')
        ocr_res = ocr_res.replace('G', '1')
        ocr_res = ocr_res.replace('B', '8')

        roi_data.set_ocr_res(ocr_res)

    def run(self):
        if len(self.roi_list) < 1:
            print('No ROI info error. %s' % (time.ctime()))
            return

        self.run = True

        print('Monitoring is started. %s' % (time.ctime()))

        cap_webcam = cv2.VideoCapture(WEBCAM_INDEX)  # from webcam

        if not WEBCAM_FOCUS_AUTO:
            cap_webcam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            cap_webcam.set(cv2.CAP_PROP_FOCUS, 30)

        cap_webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap_webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while self.run:
            start = time.time()

            success, image = cap_webcam.read()

            if RUN_WITHOUT_WEBCAM_MODE:
                image = self.sample_image

            if RUN_UPSIDE_DOWN_MODE:
                rows, cols = image.shape[:2]
                temp_image = cv2.getRotationMatrix2D((cols / 2, rows / 2), 180, 1)
                image = cv2.warpAffine(image, temp_image, (cols, rows))
                # self.image = cv2.flip(usd_image, 1)

            today = str(date.today())
            now = str(time.strftime("%H:%M:%S"))

            for roi in self.roi_list:
                col, row, width, height, threshold = roi.x, roi.y, roi.width, roi.height, roi.threshold
                margin = 20

                roi_image = image[row: row + height, col: col + width]
                roi_base = np.zeros((height + 2 * margin, width + 2 * margin, 3), np.uint8) + 255
                roi_base[margin: height + margin, margin: margin + width] = roi_image

                gray_image = cv2.cvtColor(roi_base, cv2.COLOR_BGR2GRAY)

                success, roi_image = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)

                roi.set_roi_image(Image.fromarray(roi_image))

                if SAVE_ROI_IMAGE:
                    cv2.imwrite('%i.jpg' % random.randint(1, 20), roi_image)

            # OCR processing

            threads = []

            for roi in self.roi_list:
                threads.append(Thread(target=self.ocr_execute, args=(roi.roi_image, roi,)))

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            end = time.time()

            ocr_elapsed = end - start

            self.update_to_console()

            print('OCR processing (sec.): %f' % ocr_elapsed)

        cap_webcam.release()

    def finish(self):
        self.run = False

        print('Monitoring is finished. %s' % (time.ctime()))

def main():

    if RUN_CONSOLE_ONLY_MODE is False:
        app = QApplication(sys.argv)
        window = KEM_CNCMT_Client()
        window.show()
        app.exec_()
    else:
        print('Start console mode without GUI client.')
        console = KEMConsole()
        console.load_roi_data()
        console.run()

if __name__ == '__main__':
    main()
