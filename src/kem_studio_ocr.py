# For OCR processing
import cv2
import platform
from PIL import Image
from threading import Thread
import ocr_engine # Using pytesseract
CYCLE_PERIOD = 1.0

# For GUI
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QTableWidgetItem
from PyQt5 import uic,QtGui
import webbrowser
from kem_webcam_selector import WebcamSelector
import kem_studio_rc
KEM_CLIENT_UI_PATH = 'kem_studio_ocr.ui'
AOI_EDITOR_UI_PATH = 'aoi_editor.ui'
AOI_ADD_UI_PATH = 'kem_studio_add_aoi.ui'
ABOUT_DIALOG_PATH = 'kem_studio_ocr_about.ui'
OPTION_DIALOG_PATH = 'kem_studio_ocr_option.ui'

# Misc.
import numpy as np
import pickle # For saving aoi data in file
import time
from datetime import date
import random # For saving aoi image for test purpose
WEBSITE_URL = 'https://github.com/hyungjungkim/vision-based-status-monitoring-for-legacy-HMI'
SAMPLE_IMAGE = 'sample_image/OCRCNC2.png'
RUN_CONSOLE_ONLY_MODE = False

# Option
import configparser

config = configparser.ConfigParser()
if(platform.system() == 'Windows'):
    config.read('setting.ini')
else:
    config.read('setting_lin.ini')
opt_TESSERACT_EXE = config.get('default','tes_exe_loc')
opt_TESSERACTOCR_DIR = config.get('default','tes_data_loc')
opt_RUN_WITHOUT_SCREEN_MODE = config.getboolean('default','run_wo_sc')
opt_RUN_WITHOUT_WEBCAM_MODE = config.getboolean('default','run_wo_wc')
opt_WEBCAM_INDEX = config.getint('default','wc_index')
opt_WEBCAM_AUTOFOCUS = config.getboolean('default','wc_focus')
opt_SAVE_AOI_IMAGE = config.getboolean('default', 'save_AOI_Img')
opt_CAM_URL = config.get('default','cam_url')
opt_USE_URL = config.getboolean('default','use_url')
# opt_UPSIDE_DOWN_MODE = False


class AboutDialog(QDialog):
    def __init__(self):
        super(AboutDialog, self).__init__()
        uic.loadUi(ABOUT_DIALOG_PATH, self)
        self.btn_ok.clicked.connect(self.close)


class OptionDialog(QMainWindow):
    config = configparser.ConfigParser()
    if(platform.system() == 'Windows'):
        config.read('setting.ini')
    else:
        config.read('setting_lin.ini')

    def __init__(self,parent=None):
        super(OptionDialog, self).__init__(parent)
        uic.loadUi(OPTION_DIALOG_PATH, self)

        self.tesseract_exe_loc_line.setText(opt_TESSERACT_EXE)
        self.tesseractocr_loc_line.setText(opt_TESSERACTOCR_DIR)
        self.run_without_webcam_check.setChecked(opt_RUN_WITHOUT_WEBCAM_MODE)
        
        self.rb_webcam_index.setEnabled(not opt_RUN_WITHOUT_WEBCAM_MODE)
        self.rb_webcam_index.setChecked(not opt_USE_URL)
        self.webcam_index_box.setValue(opt_WEBCAM_INDEX)
        self.webcam_index_box.setEnabled(not opt_RUN_WITHOUT_WEBCAM_MODE)
        self.btn_camera_index.setEnabled(not opt_RUN_WITHOUT_WEBCAM_MODE)
        self.rb_ip_stream.setEnabled(not opt_RUN_WITHOUT_WEBCAM_MODE)
        self.rb_ip_stream.setChecked(opt_USE_URL)
        self.camera_url.setText(opt_CAM_URL)
        self.camera_url.setEnabled(not opt_RUN_WITHOUT_WEBCAM_MODE)

        # self.run_upside_down_check.setChecked(opt_UPSIDE_DOWN_MODE)
        self.run_without_screen_check.setChecked(opt_RUN_WITHOUT_SCREEN_MODE)
        self.focus_auto_check.setChecked(opt_WEBCAM_AUTOFOCUS)
        self.save_aoi_image_check.setChecked(opt_SAVE_AOI_IMAGE)

        self.run_without_webcam_check.toggled.connect(self.toggled)
        self.btn_save.clicked.connect(self.save)
        self.btn_close.clicked.connect(self.close)
        self.btn_camera_index.clicked.connect(self.search_camera_index)
    
    def save(self):
        global opt_RUN_WITHOUT_SCREEN_MODE, opt_WEBCAM_AUTOFOCUS, opt_SAVE_AOI_IMAGE, opt_RUN_WITHOUT_WEBCAM_MODE, opt_TESSERACT_EXE,opt_TESSERACTOCR_DIR, opt_WEBCAM_INDEX, opt_CAM_URL, opt_USE_URL #,opt_UPSIDE_DOWN_MODE
        # opt_UPSIDE_DOWN_MODE = self.run_upside_down_check.isChecked()
        opt_RUN_WITHOUT_SCREEN_MODE = self.run_without_screen_check.isChecked()
        opt_WEBCAM_AUTOFOCUS = self.focus_auto_check.isChecked()
        opt_SAVE_AOI_IMAGE = self.save_aoi_image_check.isChecked()
        opt_RUN_WITHOUT_WEBCAM_MODE = self.run_without_webcam_check.isChecked()

        opt_TESSERACT_EXE = self.tesseract_exe_loc_line.text()
        opt_TESSERACTOCR_DIR =  self.tesseractocr_loc_line.text()
        opt_WEBCAM_INDEX = self.webcam_index_box.value()
        opt_CAM_URL = self.camera_url.text()
        opt_USE_URL = self.rb_ip_stream.isChecked()

        self.config.set('default','tes_exe_loc',opt_TESSERACT_EXE)
        self.config.set('default','tes_data_loc',opt_TESSERACTOCR_DIR)
        self.config.set('default','run_wo_sc',str(opt_RUN_WITHOUT_SCREEN_MODE))
        self.config.set('default','run_wo_wc',str(opt_RUN_WITHOUT_WEBCAM_MODE))
        self.config.set('default','wc_index',str(opt_WEBCAM_INDEX))
        self.config.set('default','wxc_focus',str(opt_WEBCAM_AUTOFOCUS))
        self.config.set('default', 'save_AOI_Img', str(opt_SAVE_AOI_IMAGE))
        self.config.set('default','cam_url',opt_CAM_URL)
        self.config.set('default','use_url',str(opt_USE_URL))

        if(platform.system() == 'Windows'):
            with open('setting.ini','w') as configfile:
                self.config.write(configfile)
        else:
            with open('setting_lin.ini','w') as configfile:
                self.config.write(configfile)

        self.close()
        
    
    def toggled(self):
        self.rb_webcam_index.setEnabled(not self.rb_webcam_index.isEnabled())        
        self.webcam_index_box.setEnabled(not self.webcam_index_box.isEnabled())
        self.btn_camera_index.setEnabled(not self.btn_camera_index.isEnabled())
        self.rb_ip_stream.setEnabled(not self.rb_ip_stream.isEnabled())
        self.camera_url.setEnabled(not self.camera_url.isEnabled())

    def search_camera_index(self):
        webcam_selector = WebcamSelector()

class AOIAdd(QDialog):
    name = ''
    col, row, x, y, width, height = -1, -1, -1, -1, -1, -1
    threshold = 0 # cv2 threshold manipulation
    type = 0 # 0 : None, 1 : Int, 2 : Float, 3: Text
    image,image_,disp_img = None, None, None
    camera_focus = 30
    rectangle = False
    thresholdvalue = 0
    margin_width, margin_height = 0 , 0
    finished = False
    sample_image = cv2.imread(SAMPLE_IMAGE)
    ocr_engine = ocr_engine.OCREngine(opt_TESSERACT_EXE)
    camera_viewer_title = 'Camera image'

    def __init__(self,parent= None):
        super().__init__()
        self.ui = uic.loadUi(AOI_ADD_UI_PATH, self)
        self.ui.show()
        self.btnAOI.clicked.connect(self.addAOI)
        self.btnOCRTest.clicked.connect(self.testOCR)
        self.btnRetry.clicked.connect(self.retry)
        self.txtName.textChanged.connect(self.on_name_change)
        self.sldThreshold.valueChanged.connect(self.on_threshold_change)
    
    def retry(self):
        self.addAOI()

    def showCaptureResult(self,img):
        h,w = img.shape
        qImg = QtGui.QImage(img.data, w, h, w, QtGui.QImage.Format_Grayscale8)
        if h > 200 or w > 400:
            max_rat = max(w/400,h/200)
            w_rat = int(w/max_rat)
            h_rat = int(h/max_rat)
            resize_img = cv2.resize(img,(w_rat,h_rat))
            qImg = QtGui.QImage(resize_img.data, w_rat, h_rat, w_rat, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.lblImage.setPixmap(pixmap)
        self.lblImage.show()

    def onMouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.rectangle = True
            self.col, self.row = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.rectangle:
                self.image = self.image_.copy()
                cv2.rectangle(self.image, (self.col, self.row), (x, y), (0, 255, 0), 2)
                cv2.imshow(self.camera_viewer_title, self.image)
        elif event == cv2.EVENT_LBUTTONUP:
            self.capture = False
            self.rectangle = False
            cv2.rectangle(self.image, (self.col, self.row), (x, y), (0, 255, 0), 2)
            self.height, self.width = abs(self.row - y), abs(self.col - x)

            print('col %s, row %s, width %s, height %s' % (self.col, self.row, self.width, self.height))
            aoi_image = self.image[self.row:self.row + self.height, self.col:self.col + self.width]
            aoi_base = np.zeros((self.height + 2 * self.margin_height, self.width + 2 * self.margin_width, 3), np.uint8) + 255
            aoi_base[self.margin_height:self.height + self.margin_height, self.margin_width:self.margin_width + self.width] = aoi_image 
            aoi_grayscale = cv2.cvtColor(aoi_base, cv2.COLOR_BGR2GRAY)
            self.disp_img = aoi_grayscale
            self.showCaptureResult(self.disp_img)

            self.x = self.col
            self.y = self.row
            self.txtLocX.setText(str(self.x))
            self.txtLocY.setText(str(self.y))
            self.txtSizeW.setText(str(self.width))
            self.txtSizeH.setText(str(self.height))
            if(platform.system() == 'Windows'):
                cv2.destroyWindow(self.camera_viewer_title)
    
    def addAOI(self):
        self.btnAOI.hide()
        if opt_RUN_WITHOUT_WEBCAM_MODE:
            sample_image = cv2.imread(SAMPLE_IMAGE)
            message = 'Load smaple image'
            print(message)
            self.image = self.sample_image
        
        else:
            if opt_USE_URL:
                cap_camera = cv2.VideoCapture(opt_CAM_URL)
                message = 'Start capturing an image from %s.' % opt_CAM_URL

            else :
                cap_camera = cv2.VideoCapture(opt_WEBCAM_INDEX)
                message = 'Start capturing an image from %d.' % opt_WEBCAM_INDEX
            print(message)

            if not opt_WEBCAM_AUTOFOCUS:
                cap_camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                # cap_camera.set(cv2.CAP_PROP_FOCUS, self.camera_focus)

            # cap_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            # cap_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            success, self.image = cap_camera.read()
            
            if not success:
                print('Fail to read an image.')
                return
        
        cv2.namedWindow(self.camera_viewer_title)
        cv2.setMouseCallback(self.camera_viewer_title, self.onMouse)
        
        self.image_ = self.image.copy()

        while(1) : 
            cv2.imshow(self.camera_viewer_title, self.image)
            cv2.waitKey(50)
            if cv2.getWindowProperty(self.camera_viewer_title, cv2.WND_PROP_VISIBLE) < 1:
                break
        cv2.destroyAllWindows()
        if not opt_RUN_WITHOUT_WEBCAM_MODE:
            cap_camera.release()
        message = 'Capturing an image is finished.'
        print(message)
        
    
    def on_name_change(self):
        if self.txtName.text() != '':
            self.buttonBox.setEnabled(True)
        else :
            self.buttonBox.setEnabled(False)
    
    def on_threshold_change(self):
        self.thresholdvalue = self.sldThreshold.value()
        self.txtThreshold.setText(str(self.sldThreshold.value()))
        ret, thr1 = cv2.threshold(self.disp_img, self.thresholdvalue, 255, cv2.THRESH_BINARY)
        self.showCaptureResult(thr1)

    def testOCR(self):
        print('Start testing. %s' % (time.ctime()))
        success, aoi_image = cv2.threshold(self.disp_img, self.thresholdvalue, 255, cv2.THRESH_BINARY)
        global opt_TESSERACTOCR_DIR
        ocr_res = self.ocr_engine.execute_ocr(aoi_image, opt_TESSERACTOCR_DIR)
        self.txtOCRTestResult.setText(ocr_res)
        print('End testing. %s' % (time.ctime()))


    def accept(self):
        # update data
        self.name = self.txtName.text()
        self.x = int(self.txtLocX.text())
        self.y = int(self.txtLocY.text())
        self.width = int(self.txtSizeW.text())
        self.height = int(self.txtSizeH.text())
        self.threshold = int(self.sldThreshold.value())
        self.type = int(self.cbbType.currentIndex())
        self.finished = True
        self.done(1)

    def reject(self):
        self.done(0)
'''
class AOIEditor(QDialog):
    name = ''
    x, y, width, height = -1, -1, -1, -1
    threshold = 0  # cv2 threshold manipulation
    type = 0 # 0 : None, 1 : Int, 2 : Float, 3: Text

    def __init__(self, parent=None):
        super().__init__()
        self.ui = uic.loadUi(AOI_EDITOR_UI_PATH, self)
        self.ui.show()
        self.txtName.textChanged.connect(self.on_name_change)

    def on_name_change(self):
        if self.txtName.text() != '':
            self.buttonBox.setEnabled(True)
        else :
            self.buttonBox.setEnabled(False)

    def accept(self):
        # update data
        self.name = self.txtName.text()
        self.x = int(self.txtLocX.text())
        self.y = int(self.txtLocY.text())
        self.width = int(self.txtSizeW.text())
        self.height = int(self.txtSizeH.text())
        self.threshold = int(self.txtThreshold.text())
        self.type = int(self.cbbType.currentIndex())
        self.done(1)

    def reject(self):
        self.done(0)
'''

class AOI:
    name = 'param_id'
    x, y, width, height = -1, -1, -1, -1
    threshold = 128  # cv2 threshold manipulation
    type = 0  # numeric 0, text 1, mixed 2
    aoi_image = None
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

    def set_aoi_image(self, aoi_image):
        self.aoi_image = aoi_image

    def set_ocr_res(self, ocr_res):
        self.ocr_res = ocr_res
    
    def __getstate__(self):
        return (self.name, self.x, self.y, self.width, self.height, self.threshold,
        self.type, self.aoi_image, self.ocr_res)

    def __setstate__(self, state):
        name, x, y, width, height, threshold, type, aoi_image, ocr_res = state      
        self.name, self.x, self.y, self.width, self.height, self.threshold = name, x, y, width, height, threshold
        self.type, self.aoi_image, self.ocr_res = type, aoi_image, ocr_res


class KEM_STUDIO_OCR(QMainWindow):
    sample_image = None
    global opt_TESSERACT_EXE,opt_TESSERACTOCR_DIR
    if opt_RUN_WITHOUT_WEBCAM_MODE:
        sample_image = cv2.imread(SAMPLE_IMAGE)

    image, image_, capture, rectangle, threshold = None, None, False, False, False
    col, row, width, height = -1, -1, -1, -1
    thresholdvalue = 0
    margin_width, margin_height = 100, 30
    aoi_list = []
    ocr_engine = ocr_engine.OCREngine(opt_TESSERACT_EXE)

    watch = False

    camera_focus = 30
    
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(KEM_CLIENT_UI_PATH, self)
        self.ui.show()

        self.actionLoad.triggered.connect(self.load_aoi_data)
        self.actionSave.triggered.connect(self.save_aoi_data)
        self.actionExit.triggered.connect(self.close)
        self.tbactionExit.triggered.connect(self.close)

        self.actionCameraConnect.triggered.connect(self.connect_camera)
        self.tbactionCameraConnect.triggered.connect(self.connect_camera)

        self.actionOptions.triggered.connect(self.show_option_dialog)
        self.tbactionOptions.triggered.connect(self.show_option_dialog)

        self.actionWatch.triggered.connect(self.watch)
        self.tbactionWatch.triggered.connect(self.watch)

        self.actionStop.triggered.connect(self.finish)
        self.tbactionStop.triggered.connect(self.finish)

        self.actionWebsite.triggered.connect(self.visit_website)
        self.actionAbout.triggered.connect(self.show_about)

        self.actionLive.triggered.connect(self.live_view)

        self.update_status('Ready')

    

    def update_status(self, message):
        self.status_bar.showMessage('%s - %s' % (message, time.ctime()))

    def show_option_dialog(self):
        self.mainWindow = OptionDialog()
        self.mainWindow.show()

    def live_view(self):
        self.update_status('Test an image.')
        if opt_RUN_WITHOUT_WEBCAM_MODE:
            self.update_status('No Live View in Without Webcam Mode')
            return
        
        camera = cv2.VideoCapture(opt_WEBCAM_INDEX)        
        ret, frame = camera.read()
        cv2.imshow('Test an image from the selected camera (index %d)' % opt_WEBCAM_INDEX, frame)
        cv2.waitKey()
        camera.release()
        cv2.destroyAllWindows()

    def close(self):
        super().close()
        quit()
    
    def load_aoi_data(self):
        with open('aoi_data.kem', 'rb') as input:
            self.aoi_list = pickle.load(input)

        message = 'AOI data is loaded.'
        self.update_status(message)
        self.update_aoi()
        print(message)
        self.tbactionOptions.setEnabled(True)
        self.actionOptions.setEnabled(True)
        self.tbactionWatch.setEnabled(True)
        self.actionWatch.setEnabled(True)

    def save_aoi_data(self):
        with open('aoi_data.kem', 'wb') as output:  # Overwrites an existing file.
            pickle.dump(self.aoi_list, output, pickle.HIGHEST_PROTOCOL)

        message = 'AOI data is saved.'
        self.update_status(message)
        self.update_aoi()
        print(message)

    '''
    def add_region(self):
        self.dialog = AOIEditor(self)

        self.dialog.txtLocX.setText(str(self.col))
        self.dialog.txtLocY.setText(str(self.row))
        self.dialog.txtSizeW.setText(str(self.width))
        self.dialog.txtSizeH.setText(str(self.height))
        self.dialog.txtThreshold.setText(str(self.thresholdvalue))
        #self.dialog.txtType.setText('0')

        self.dialog.show()
        if self.dialog.exec_():
            aoi = AOI()
            aoi.set_name(self.dialog.name)
            aoi.set_location(self.dialog.x, self.dialog.y)
            aoi.set_size(self.dialog.width, self.dialog.height)
            aoi.set_threshold(self.dialog.threshold)
            aoi.set_type(self.dialog.type)
            #aoi.set_id(self.dialog.selected_index)
            self.aoi_list.append(aoi)
            self.status_bar.showMessage('AOI of %s is added. %s' % (self.dialog.name, time.ctime()))
    '''
    def add_region(self, addAOI):
        aoi = AOI()
        aoi.set_name(addAOI.name)
        aoi.set_location(addAOI.x, addAOI.y)
        aoi.set_size(addAOI.width, addAOI.height)
        aoi.set_threshold(addAOI.threshold)
        aoi.set_type(addAOI.type)
        self.aoi_list.append(aoi)
        self.status_bar.showMessage('AOI of %s is added. %s' % (addAOI.name, time.ctime()))
        self.update_aoi()

    def update_aoi(self):
        index = 1
        self.result_table.setRowCount(len(self.aoi_list) + 1)
        for aoi in self.aoi_list:
            widgetItem1 = QTableWidgetItem('%i (%s)' % (index, aoi.name))
            widgetItem2 = QTableWidgetItem('(%i,%i,%i,%i)\n%i'%(aoi.x,aoi.y,aoi.width,aoi.height,aoi.threshold))
            widgetItem1.setTextAlignment(0x0084)
            widgetItem2.setTextAlignment(0x0084)
            self.result_table.setItem(index, 0, widgetItem1)
            self.result_table.setItem(index, 1, widgetItem2)
            index += 1
    
    def update_result(self):        
        index = 1
        for aoi in self.aoi_list:
            widgetItem1 = QTableWidgetItem('%i (%s)' % (index, aoi.name))
            widgetItem2 = QTableWidgetItem('%s' % str(aoi.ocr_res))
            widgetItem1.setTextAlignment(0x0084)
            widgetItem2.setTextAlignment(0x0084)
            self.result_table.setItem(index, 0, widgetItem1)
            self.result_table.setItem(index, 1, widgetItem2)
            index += 1

    def execute_aoi_ocr(self, aoi_image, aoi_data):
        global opt_TESSERACTOCR_DIR
        ocr_res = self.ocr_engine.execute_ocr(aoi_image, opt_TESSERACTOCR_DIR)
        print('Result : ' + ocr_res)

        aoi_data.set_ocr_res(ocr_res)

    def watch(self):
        if len(self.aoi_list) < 1:
            print('No AOI data is found. %s' % (time.ctime()))
            return
        self.result_table.setRowCount(len(self.aoi_list) + 1)
        self.watch = True
        self.tbactionOptions.setEnabled(False)
        self.actionOptions.setEnabled(False)
        self.tbactionCameraConnect.setEnabled(False)
        self.actionCameraConnect.setEnabled(False)
        self.actionWatch.setEnabled(False)
        self.tbactionWatch.setEnabled(False)
        self.actionStop.setEnabled(True)
        self.tbactionStop.setEnabled(True)
        print('Start watching. %s' % (time.ctime()))
        if not opt_RUN_WITHOUT_WEBCAM_MODE:
            if opt_USE_URL :
                cap_camera = cv2.VideoCapture(0)
            if not opt_USE_URL :
                cap_camera = cv2.VideoCapture(opt_WEBCAM_INDEX)

            if not opt_WEBCAM_AUTOFOCUS:
                cap_camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                # cap_camera.set(cv2.CAP_PROP_FOCUS, self.camera_focus)

            # cap_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            # cap_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while self.watch:
            if not opt_RUN_WITHOUT_WEBCAM_MODE:
                if opt_USE_URL:
                    cap_camera = cv2.VideoCapture(opt_CAM_URL)
                    cap_camera.set(cv2.CAP_PROP_BUFFERSIZE,1)
                
                cap_camera.set(cv2.CAP_PROP_POS_FRAMES,0)
                success, image = cap_camera.read()
            else:
                image = self.sample_image
            
            # if opt_UPSIDE_DOWN_MODE:
            #     rows, cols = image.shape[:2]
            #     temp_image = cv2.getRotationMatrix2D((cols / 2, rows / 2), 180, 1)
            #     image = cv2.warpAffine(image, temp_image, (cols, rows))

            today = str(date.today())
            now = str(time.strftime("%H:%M:%S"))
            self.current_time.setText(today +'    '+ now)

            for aoi in self.aoi_list:
                col, row, width, height, threshold = aoi.x, aoi.y, aoi.width, aoi.height, aoi.threshold
                margin = 20

                if not opt_RUN_WITHOUT_SCREEN_MODE:
                    cv2.rectangle(image, (col, row), (col + width, row + height), (0, 255, 0), 5)

                    cv2.imshow('monitor', image)

                aoi_image = image[row: row + height, col: col + width]
                aoi_base = np.zeros((height + 2 * margin, width + 2 * margin, 3), np.uint8) + 255
                aoi_base[margin: height + margin, margin: margin + width] = aoi_image

                gray_image = cv2.cvtColor(aoi_base, cv2.COLOR_BGR2GRAY)

                success, aoi_image = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)

                aoi.set_aoi_image(Image.fromarray(aoi_image))

                if opt_SAVE_AOI_IMAGE:
                    cv2.imwrite('%i.jpg' % random.randint(1, 20), aoi_image)

                if cv2.waitKey(25) & 0xFF == ord('f'):
                    break

            # OCR processing
            start = time.time()

            threads = []

            for aoi in self.aoi_list:
                threads.append(Thread(target=self.execute_aoi_ocr, args=(aoi.aoi_image, aoi,)))

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            end = time.time()

            ocr_elapsed = end - start

            time.sleep(CYCLE_PERIOD - ocr_elapsed)
            
            self.update_result()

            self.status_bar.showMessage('OCR processing (sec.): %f' % ocr_elapsed)

            self.repaint()
            
            if not opt_RUN_WITHOUT_WEBCAM_MODE:
                if opt_USE_URL:
                    cap_camera.release()

        if not opt_RUN_WITHOUT_WEBCAM_MODE:
            if not opt_USE_URL:
                cap_camera.release()
        cv2.destroyAllWindows()
        self.update_status('OCR processing is finished. ')
        print('OCR processing is finished. %s' % (time.ctime()))

    def finish(self):
        self.watch = False
        self.tbactionOptions.setEnabled(True)
        self.actionOptions.setEnabled(True)
        self.tbactionCameraConnect.setEnabled(True)
        self.actionCameraConnect.setEnabled(True)
        self.actionWatch.setEnabled(True)
        self.tbactionWatch.setEnabled(True)
        self.actionStop.setEnabled(False)
        self.tbactionStop.setEnabled(False)
        self.current_time.setText("Not Running!!!")
        self.update_status('Watching is finished.')

    def onChange(self, x):
        pass

    '''
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

                aoi_image = self.image[self.row:self.row + self.height, self.col:self.col + self.width]
                aoi_base = np.zeros((self.height + 2 * self.margin_height, self.width + 2 * self.margin_width, 3),
                                    np.uint8) + 255
                aoi_base[self.margin_height:self.height + self.margin_height,
                self.margin_width:self.margin_width + self.width] = aoi_image
                self.thresholdvalue = 68
                self.add_region()

                cv2.namedWindow('threshold')
                cv2.imshow('threshold', aoi_base)
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

                    aoi_grayscale = cv2.cvtColor(aoi_base, cv2.COLOR_BGR2GRAY)
                    thresholdvalue = cv2.getTrackbarPos('thresholdbar', 'threshold')

                    ret, thr1 = cv2.threshold(aoi_grayscale, thresholdvalue, 255, cv2.THRESH_BINARY)
                    cv2.imshow('threshold', thr1)

                cv2.destroyWindow('threshold')

        return
    '''

    def set_camera_focus(self, value):
        self.camera_focus += value

        if self.camera_focus < 0:
            self.camera_focus = 0
        elif self.camera_focus > 250:
            self.camera_focus = 250

        print('Webcam focus = %i' % self.camera_focus)

    def connect_camera(self):
        dialog = AOIAdd(self)
        dialog.exec_()
        if(dialog.finished) : 
            self.add_region(dialog)
        self.tbactionOptions.setEnabled(True)
        self.actionOptions.setEnabled(True)
        self.tbactionWatch.setEnabled(True)
        self.actionWatch.setEnabled(True)
        '''
        cap_camera = cv2.VideoCapture(opt_WEBCAM_INDEX)
        message = 'Start capturing an image.'
        self.update_status(message)
        print(message)

        if not opt_WEBCAM_AUTOFOCUS:
            cap_camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            cap_camera.set(cv2.CAP_PROP_FOCUS, self.camera_focus)

        cap_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.onMouse)

        while (1): 
            cap_camera.set(cv2.CAP_PROP_FOCUS, self.camera_focus)
            success, self.image = cap_camera.read()
            if opt_RUN_WITHOUT_WEBCAM_MODE:
                self.image = self.sample_image

            # if opt_UPSIDE_DOWN_MODE:
            #     rows, cols = self.image.shape[:2]
            #     temp_image = cv2.getRotationMatrix2D((cols / 2, rows / 2), 180, 1)
            #     self.image = cv2.warpAffine(self.image, temp_image, (cols, rows))
            #     # self.image = cv2.flip(usd_image, 1)

            if not success and not opt_RUN_WITHOUT_WEBCAM_MODE:
                print('Fail to read an image.')
                break

            org1 = (20,40)
            org2 = (20,60)
            org3 = (20,80)
            org4 = (20,100)
            org5 = (20,120)
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 0.5
            color = (255, 255, 255)
            thickness = 1
            cv2.putText(self.image,'C : Capture',org1,font,fontScale,color,thickness,cv2.LINE_AA)
            cv2.putText(self.image,'T : Threshold Save',org2,font,fontScale,color,thickness,cv2.LINE_AA)
            cv2.putText(self.image,'Q : Quit',org3,font,fontScale,color,thickness,cv2.LINE_AA)
            cv2.putText(self.image,'I : Camera Focus In',org4,font,fontScale,color,thickness,cv2.LINE_AA)
            cv2.putText(self.image,'O : Camera Focus Out',org5,font,fontScale,color,thickness,cv2.LINE_AA)

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

        cap_camera.release()
        self.tbactionOptions.setEnabled(True)
        self.actionOptions.setEnabled(True)
        self.tbactionWatch.setEnabled(True)
        self.actionWatch.setEnabled(True)
        cv2.destroyAllWindows()
        message = 'Capturing an image is finished.'
        self.update_status(message)
        print(message)
        '''
    
    def visit_website(self):
        webbrowser.open(WEBSITE_URL)
    
    def show_about(self):
        dialog = AboutDialog()
        dialog.exec_()
        

class KEM_Headless_OCR():
    sample_image = None

    if opt_RUN_WITHOUT_WEBCAM_MODE:
        sample_image = cv2.imread(SAMPLE_IMAGE)

    image, image_, capture, rectangle, threshold = None, None, False, False, False
    col, row, width, height = -1, -1, -1, -1
    thresholdvalue = 0
    margin_width, margin_height = 100, 30
    aoi_list = []
    global opt_TESSERACT_EXE
    ocr_engine = ocr_engine.OCREngine(opt_TESSERACT_EXE)
    
    run = False

    def __init__(self, parent=None):
        pass

    def load_aoi_data(self):
        with open('aoi_data.kem', 'rb') as input:
            self.aoi_list = pickle.load(input)

        print('AOI data is loaded. %s' % (time.ctime()))

    def update_result(self):
        index = 1

        for aoi in self.aoi_list:
            print('%i. %s: %s' % (index, aoi.name, aoi.ocr_res))

            index += 1

    def ocr_execute(self, aoi_image, aoi_data):
        ocr_res = self.ocr_engine.execute_ocr(aoi_image,opt_TESSERACTOCR_DIR)

        aoi_data.set_ocr_res(ocr_res)

    def run(self):
        if len(self.aoi_list) < 1:
            print('No AOI info error. %s' % (time.ctime()))
            return

        self.run = True

        print('Start watching. %s' % (time.ctime()))

        cap_camera = cv2.VideoCapture(opt_WEBCAM_INDEX)

        if not opt_WEBCAM_AUTOFOCUS:
            cap_camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            cap_camera.set(cv2.CAP_PROP_FOCUS, 30)

        # cap_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        # cap_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while self.run:
            start = time.time()

            success, image = cap_camera.read()

            if opt_RUN_WITHOUT_WEBCAM_MODE:
                image = self.sample_image

            # if opt_UPSIDE_DOWN_MODE:
            #     rows, cols = image.shape[:2]
            #     temp_image = cv2.getRotationMatrix2D((cols / 2, rows / 2), 180, 1)
            #     image = cv2.warpAffine(image, temp_image, (cols, rows))
            #     # self.image = cv2.flip(usd_image, 1)

            for aoi in self.aoi_list:
                col, row, width, height, threshold = aoi.x, aoi.y, aoi.width, aoi.height, aoi.threshold
                margin = 20

                aoi_image = image[row: row + height, col: col + width]
                aoi_base = np.zeros((height + 2 * margin, width + 2 * margin, 3), np.uint8) + 255
                aoi_base[margin: height + margin, margin: margin + width] = aoi_image

                gray_image = cv2.cvtColor(aoi_base, cv2.COLOR_BGR2GRAY)

                success, aoi_image = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)

                aoi.set_aoi_image(Image.fromarray(aoi_image))

                if opt_SAVE_AOI_IMAGE:
                    cv2.imwrite('/aoi_image/%i.jpg' % random.randint(1, 20), aoi_image)

            threads = []

            for aoi in self.aoi_list:
                threads.append(Thread(target=self.ocr_execute, args=(aoi.aoi_image, aoi,)))

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            end = time.time()

            ocr_elapsed = end - start

            self.update_result()

            print('OCR processing (sec.): %f' % ocr_elapsed)

        cap_camera.release()

    def finish(self):
        self.run = False
        print('Watching is finished. %s' % (time.ctime()))

def main():

    if RUN_CONSOLE_ONLY_MODE is False:
        app = QApplication(sys.argv)
        window = KEM_STUDIO_OCR()
        window.show()
        app.exec_()
    else:
        print('Start console mode without GUI client.')
        console = KEM_Headless_OCR()
        console.load_aoi_data()
        console.run()

if __name__ == '__main__':
    main()
