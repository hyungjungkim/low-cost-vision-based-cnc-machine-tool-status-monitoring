KEM_WEBCAM_SELECTOR_UI_PATH = 'kem_webcam_selector.ui'

#from msilib.schema import ComboBox
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5 import uic

import cv2

MAX_CAMERA_INDEX = 10

class WebcamSelector(QDialog):
    webcam_index = -1

    camera_list = []

    def __init__(self, parent=None):
        super().__init__()
        self.ui = uic.loadUi(KEM_WEBCAM_SELECTOR_UI_PATH, self)
        self.ui.show()
        
        self.init_camera_list()
        self.cbb_camera_list.currentIndexChanged.connect(self.on_webcam_selection)
        self.btn_refresh_camera.clicked.connect(self.refresh_available_camera)
        self.btn_test_webcam.clicked.connect(self.test_webcam)
        self.btn_close.clicked.connect(self.close)

    def init_camera_list(self):
        self.cbb_camera_list.clear()
        self.cbb_camera_list.addItem('None - Only for demo')

        self.webcam_index = -1

    def on_webcam_selection(self):
        if self.cbb_camera_list.currentIndex() > -1:
            current_text = self.cbb_camera_list.currentText()
            if current_text == 'None - Only for demo' or current_text == '':
                self.webcam_index = -1
            else:
                self.webcam_index = int(self.cbb_camera_list.currentText().split('-')[-1])
                print('The selected camera index is ' + str(self.webcam_index))
    
    def get_cameras(self):
        camera_list = []

        for index in range(0, MAX_CAMERA_INDEX):
            camera = cv2.VideoCapture(index,cv2.CAP_V4L)
            if camera.isOpened():
                camera_list.append(index)
                print('Found ' + str(index))
            else: break
            camera.release()

        return camera_list

    def refresh_available_camera(self):
        self.camera_list = self.get_cameras()
        
        self.init_camera_list()
        for camera in self.camera_list:
            self.cbb_camera_list.addItem('Camera Index - ' + str(camera))

    def test_webcam(self):
        if self.webcam_index != -1:
            camera = cv2.VideoCapture(self.webcam_index,cv2.CAP_V4L)
            ret, frame = camera.read()
            cv2.imshow('Test Image of the selected camera (index %d)' % self.webcam_index, frame)
            cv2.waitKey(3000)
            camera.release()
            cv2.destroyAllWindows()
        else:
            QMessageBox.about(self, "Information", "No camera is selected.\nDemo mode is only available.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    webcam_selector = WebcamSelector()
    app.exec_()
    print(webcam_selector.webcam_index)
